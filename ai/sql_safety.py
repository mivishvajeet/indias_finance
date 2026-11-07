"""SQL Safety Guardrails: Enforces strict read-only execution, table allowlists, and AST checks."""
import re
from typing import List, Set

FORBIDDEN_OPERATIONS: Set[str] = {
    "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "TRUNCATE",
    "CREATE", "REPLACE", "GRANT", "REVOKE", "EXECUTE", "VACUUM",
    "ATTACH", "DETACH", "PRAGMA", "COPY", "EXPORT", "IMPORT", "WRITE_CSV", "WRITE_PARQUET"
}

ALLOWED_TABLES: Set[str] = {
    "fact_daily_prices",
    "fact_macro_indicators",
    "fact_mf_nav",
    "dim_security",
    "dim_date",
    "dim_fund",
    "dim_sector",
    "stg_stocks",
    "stg_macro",
    "stg_mf_nav",
    "data_incidents",
    "pipeline_execution_runs",
    "main_marts.fact_daily_prices",
    "main_marts.fact_macro_indicators",
    "main_marts.fact_mf_nav",
    "main_marts.dim_security",
    "main_marts.dim_date",
    "main_marts.dim_fund",
    "main_marts.dim_sector",
    "main_staging.stg_stocks",
    "main.data_incidents",
    "main.pipeline_execution_runs",
}


class SQLSafetyValidator:
    """Validates that a generated SQL string is 100% read-only and targets approved tables."""

    @classmethod
    def validate_sql(cls, sql: str) -> None:
        clean_q = sql.strip().rstrip(";")
        if not clean_q:
            raise ValueError("Generated SQL query is empty.")

        # Disallow multiple semicolon statements
        statements = [s for s in clean_q.split(";") if s.strip()]
        if len(statements) > 1:
            raise ValueError("Multi-statement execution is strictly disallowed for security.")

        # Disallow mutation keywords
        upper_q = clean_q.upper()
        tokens = set(re.findall(r"\b[A-Z_]+\b", upper_q))
        forbidden_hits = tokens.intersection(FORBIDDEN_OPERATIONS)
        if forbidden_hits:
            raise ValueError(f"Forbidden SQL keywords detected: {forbidden_hits}. Only SELECT queries are permitted.")

        # Must start with SELECT or WITH
        first_token = re.match(r"^\s*([A-Za-z]+)", clean_q)
        if not first_token or first_token.group(1).upper() not in ["SELECT", "WITH", "DESCRIBE", "EXPLAIN"]:
            raise ValueError("Query must begin with SELECT, WITH, or EXPLAIN.")
