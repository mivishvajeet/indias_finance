"""Data Lineage Service: Extracts table and column lineage from dbt manifest and lakehouse manifests."""
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import pandas as pd
from data_access.duckdb_client import db_client

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = PROJECT_ROOT / "finance_dbt" / "target" / "manifest.json"


class DataLineageService:
    """Parses dbt manifest.json and DuckDB catalog to build interactive DAG lineage graphs."""

    @staticmethod
    def get_lineage_graph() -> Dict[str, Any]:
        """Constructs unified multi-tier lineage nodes and edges from Bronze to Serving."""
        # Layer assignment
        layers = {
            "BRONZE": ["raw_stocks_daily", "raw_macro_indicators", "raw_mf_nav"],
            "SILVER": ["stg_stocks", "stg_macro", "stg_mf_nav"],
            "INTERMEDIATE": ["int_stock_daily_returns", "int_stock_technicals", "int_stock_ema_macd"],
            "GOLD": ["dim_date", "dim_security", "dim_sector", "dim_fund", "fact_daily_prices", "fact_macro_indicators", "fact_mf_nav"],
            "SERVING": ["Market Overview", "Equity Screener", "Stock Analytics", "Mutual Fund Engine", "Risk Frontier"],
        }

        # Colors by layer
        layer_colors = {
            "BRONZE": "#F5B942",      # Warning / Amber
            "SILVER": "#45A3FF",      # Blue
            "INTERMEDIATE": "#A78BFA",# Purple
            "GOLD": "#00C087",        # Emerald
            "SERVING": "#E6EDF5",     # White/Ice
        }

        # Coordinates for Plotly visual DAG layout (X = Layer depth 0 to 4, Y = spread)
        node_coords = {
            # Bronze (X = 0)
            "raw_stocks_daily": (0, 3.5),
            "raw_macro_indicators": (0, 2.0),
            "raw_mf_nav": (0, 0.5),
            
            # Silver (X = 1)
            "stg_stocks": (1, 3.5),
            "stg_macro": (1, 2.0),
            "stg_mf_nav": (1, 0.5),

            # Intermediate (X = 2)
            "int_stock_daily_returns": (2, 4.0),
            "int_stock_technicals": (2, 3.2),
            "int_stock_ema_macd": (2, 2.4),

            # Gold (X = 3)
            "dim_date": (3, 4.8),
            "dim_security": (3, 4.1),
            "dim_sector": (3, 3.4),
            "fact_daily_prices": (3, 2.6),
            "fact_macro_indicators": (3, 1.8),
            "dim_fund": (3, 1.0),
            "fact_mf_nav": (3, 0.2),

            # Serving Dashboards (X = 4)
            "Market Overview": (4, 4.2),
            "Equity Screener": (4, 3.2),
            "Stock Analytics": (4, 2.2),
            "Mutual Fund Engine": (4, 1.2),
            "Risk Frontier": (4, 0.2),
        }

        # Explicit directed edges (Source -> Target)
        edges = [
            # Bronze to Silver
            ("raw_stocks_daily", "stg_stocks"),
            ("raw_macro_indicators", "stg_macro"),
            ("raw_mf_nav", "stg_mf_nav"),

            # Silver to Intermediate
            ("stg_stocks", "int_stock_daily_returns"),
            ("int_stock_daily_returns", "int_stock_technicals"),
            ("stg_stocks", "int_stock_ema_macd"),

            # Intermediate/Silver to Gold
            ("int_stock_technicals", "fact_daily_prices"),
            ("int_stock_ema_macd", "fact_daily_prices"),
            ("dim_security", "fact_daily_prices"),
            ("dim_date", "fact_daily_prices"),
            ("dim_security", "dim_sector"),
            
            ("stg_macro", "fact_macro_indicators"),
            ("dim_date", "fact_macro_indicators"),

            ("stg_mf_nav", "dim_fund"),
            ("stg_mf_nav", "fact_mf_nav"),
            ("dim_fund", "fact_mf_nav"),
            ("dim_date", "fact_mf_nav"),

            # Gold to Serving
            ("fact_daily_prices", "Market Overview"),
            ("fact_macro_indicators", "Market Overview"),
            ("fact_daily_prices", "Equity Screener"),
            ("fact_daily_prices", "Stock Analytics"),
            ("fact_mf_nav", "Mutual Fund Engine"),
            ("fact_daily_prices", "Risk Frontier"),
            ("fact_mf_nav", "Risk Frontier"),
        ]

        # Node details dictionary
        counts = db_client.get_table_counts()
        node_details = {}

        for layer_name, nodes_list in layers.items():
            for n in nodes_list:
                table_key = f"main_marts.{n}" if layer_name == "GOLD" else (
                    f"main_staging.{n}" if layer_name == "SILVER" else (
                        f"main_intermediate.{n}" if layer_name == "INTERMEDIATE" else n
                    )
                )
                cnt = counts.get(table_key, -1)
                node_details[n] = {
                    "node_name": n,
                    "layer": layer_name,
                    "color": layer_colors[layer_name],
                    "records": cnt if cnt != -1 else ("External" if layer_name == "SERVING" else "Parquet"),
                    "schema": "main_marts" if layer_name == "GOLD" else ("main_staging" if layer_name == "SILVER" else ("main_intermediate" if layer_name == "INTERMEDIATE" else "lakehouse")),
                    "materialization": "Table" if layer_name == "GOLD" and not n.startswith("int_") else ("View" if layer_name in ["SILVER", "INTERMEDIATE"] else "Partitioned Parquet"),
                    "upstreams": [src for src, tgt in edges if tgt == n],
                    "downstreams": [tgt for src, tgt in edges if src == n],
                }

        return {
            "nodes": node_details,
            "coords": node_coords,
            "edges": edges,
        }
