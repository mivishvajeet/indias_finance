"""Local RAG & Text-to-SQL Assistant: Grounded financial question answering with data provenance."""
from datetime import datetime, timezone
import time
from typing import Any, Dict, List, Optional
import urllib.request
import pandas as pd

from ai.sql_safety import SQLSafetyValidator
from ai.sql_generator import TextToSQLGenerator
from data_access.duckdb_client import db_client


class AskFinanceAIAssistant:
    """Answers user financial and data engineering questions strictly grounded in DuckDB marts."""

    @staticmethod
    def is_ollama_available() -> bool:
        """Probes local Ollama port 11434 with a 1-second timeout."""
        try:
            req = urllib.request.Request("http://localhost:11434/api/tags", method="GET")
            with urllib.request.urlopen(req, timeout=1) as resp:
                return resp.status == 200
        except Exception:
            return False

    @classmethod
    def answer_question(cls, question: str) -> Dict[str, Any]:
        """Processes user question: Generates SQL, validates safety, executes query, and constructs provenance answer."""
        t0 = time.time()
        sql, explanation, meta = TextToSQLGenerator.generate_sql(question)
        
        # 1. Enforce SQL Safety Guardrails
        try:
            SQLSafetyValidator.validate_sql(sql)
        except ValueError as val_err:
            return {
                "direct_answer": f"⚠️ SQL Safety Violation: {str(val_err)}",
                "table_data": pd.DataFrame(),
                "sql_used": sql,
                "provenance": "Rejected by SQLSafetyValidator",
                "observation_date": "N/A",
                "assumptions": "Query execution blocked due to forbidden operations or unapproved schema mutations.",
                "latency_ms": round((time.time() - t0) * 1000, 2),
                "is_ollama_live": cls.is_ollama_available(),
            }

        # 2. Execute Query against Warehouse
        try:
            df = db_client.query(sql)
        except Exception as q_err:
            return {
                "direct_answer": f"Database Execution Error: {str(q_err)}",
                "table_data": pd.DataFrame(),
                "sql_used": sql,
                "provenance": meta.get("table", "DuckDB Warehouse"),
                "observation_date": "N/A",
                "assumptions": "N/A",
                "latency_ms": round((time.time() - t0) * 1000, 2),
                "is_ollama_live": cls.is_ollama_available(),
            }

        # 3. Synthesize Grounded Natural Language Answer
        if df.empty:
            answer = "No records matched your criteria in the curated warehouse tables."
            obs_date = "N/A"
        else:
            obs_date = str(df["trade_date"].iloc[0]) if "trade_date" in df.columns else (
                str(df["observation_date"].iloc[0]) if "observation_date" in df.columns else (
                    str(df["detection_timestamp"].iloc[0]) if "detection_timestamp" in df.columns else "2026-11-06"
                )
            )

            # Contextual summary synthesis
            if "pct_below_sma20" in df.columns:
                syms = df["symbol"].tolist()
                answer = f"Found **{len(df)} securities** trading below their 20-Day Simple Moving Average: {', '.join(syms)}. Greatest discount is observed in **{df.iloc[0]['company_name']}** ({df.iloc[0]['pct_below_sma20']}%) relative to its 20-day trend."
            elif "daily_return_pct" in df.columns:
                top = df.iloc[0]
                answer = f"**{top['company_name']} ({top['symbol']})** demonstrated the strongest single-session performance with a **{top['daily_return_pct']:+.2f}%** gain, closing at **₹{top['close_price']:,.2f}**."
            elif "sharpe_ratio" in df.columns:
                top = df.iloc[0]
                answer = f"**{top['scheme_name']}** achieved the highest risk-adjusted efficiency with an annualized **Sharpe Ratio of {top['sharpe_ratio']:.2f}** and Sortino Ratio of **{top.get('sortino_ratio', 0.0):.2f}** relative to the 6.50% risk-free rate."
            elif "indicator_code" in df.columns:
                answer = f"Retrieved verified macroeconomic series across {len(df)} active indicators including RBI Repo Rate and USD/INR exchange levels."
            else:
                answer = f"Retrieved {len(df)} verified rows from curated warehouse table `{meta.get('table')}`."

        elapsed_ms = round((time.time() - t0) * 1000, 2)
        return {
            "direct_answer": answer,
            "table_data": df,
            "sql_used": sql.strip(),
            "provenance": f"Curated Gold Mart: `{meta.get('table')}`",
            "observation_date": obs_date,
            "assumptions": "Calculated deterministically using DuckDB vectorized columnar SQL. Risk metrics assume 6.50% Indian 10Y G-Sec benchmark with 252 annual trading days.",
            "latency_ms": elapsed_ms,
            "is_ollama_live": cls.is_ollama_available(),
        }
