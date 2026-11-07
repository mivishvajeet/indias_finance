"""Centralized DuckDB Client with Read-Only Safety and Execution Tracking."""
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
import duckdb
import pandas as pd

logger = logging.getLogger("duckdb_client")
DEFAULT_WAREHOUSE_PATH = Path(__file__).resolve().parent.parent / "data" / "warehouse" / "curated.duckdb"


class DuckDBClient:
    """Manages queries, table introspection, and incident persistence."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = Path(db_path) if db_path else DEFAULT_WAREHOUSE_PATH
        self.ops_db_path = self.db_path.parent / "operational_metadata.duckdb"
        if not self.db_path.exists():
            raise FileNotFoundError(f"DuckDB warehouse not found at {self.db_path}")

    def get_read_only_connection(self) -> duckdb.DuckDBPyConnection:
        """Returns a read-only DuckDB connection for analytics and dashboards."""
        return duckdb.connect(str(self.db_path), read_only=True)

    def get_read_write_connection(self) -> duckdb.DuckDBPyConnection:
        """Returns a connection to the decoupled operational state store for incident persistence."""
        return duckdb.connect(str(self.ops_db_path), read_only=False)

    def query(self, sql: str, params: Optional[List[Any]] = None) -> pd.DataFrame:
        """Executes a SQL query and returns a pandas DataFrame."""
        con = self.get_read_only_connection()
        try:
            if params:
                return con.execute(sql, params).df()
            return con.execute(sql).df()
        finally:
            con.close()

    def get_table_counts(self) -> Dict[str, int]:
        """Queries actual row counts for all base tables and views across schemas."""
        con = self.get_read_only_connection()
        try:
            tables = con.execute("""
                SELECT table_schema, table_name, table_type
                FROM information_schema.tables
                WHERE table_schema IN ('main', 'main_staging', 'main_intermediate', 'main_marts')
                ORDER BY table_schema, table_name
            """).fetchall()

            counts = {}
            for schema, name, ttype in tables:
                key = f"{schema}.{name}"
                try:
                    c = con.execute(f'SELECT COUNT(*) FROM "{schema}"."{name}"').fetchone()[0]
                    counts[key] = c
                except Exception as e:
                    counts[key] = -1
            return counts
        finally:
            con.close()


# Global client singleton
db_client = DuckDBClient()
