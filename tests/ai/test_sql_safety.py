"""Unit tests for SQL Safety and Guardrail Enforcement."""
import pytest
from ai.sql_safety import SQLSafetyValidator


class TestSQLSafety:
    """Verifies that the SQLSafetyValidator rejects all dangerous mutations and accepts valid SELECTs."""

    def test_valid_select_allowed(self):
        valid_queries = [
            "SELECT * FROM main_marts.fact_daily_prices WHERE close_price > 500",
            "WITH ranked AS (SELECT symbol, close_price FROM main_marts.fact_daily_prices) SELECT * FROM ranked",
            "SELECT symbol, AVG(daily_return_pct) FROM main_marts.fact_daily_prices GROUP BY symbol",
            "DESCRIBE main_marts.fact_daily_prices",
        ]
        for q in valid_queries:
            SQLSafetyValidator.validate_sql(q)  # Should not raise

    def test_forbidden_mutations_blocked(self):
        dangerous_queries = [
            "DROP TABLE main_marts.fact_daily_prices",
            "DELETE FROM main_marts.fact_daily_prices WHERE close_price < 0",
            "INSERT INTO main_marts.fact_daily_prices VALUES ('1', 'S1', 20261101, 100)",
            "UPDATE main_marts.fact_daily_prices SET close_price = 0",
            "ALTER TABLE main_marts.fact_daily_prices DROP COLUMN rsi_14",
            "ATTACH 'malicious.db'",
            "PRAGMA show_tables",
            "TRUNCATE TABLE main_marts.fact_daily_prices",
        ]
        for q in dangerous_queries:
            with pytest.raises(ValueError) as exc:
                SQLSafetyValidator.validate_sql(q)
            assert "Forbidden SQL" in str(exc.value) or "Query must begin with" in str(exc.value)

    def test_multi_statement_blocked(self):
        multi_q = "SELECT * FROM main_marts.fact_daily_prices; DROP TABLE main_marts.dim_security;"
        with pytest.raises(ValueError) as exc:
            SQLSafetyValidator.validate_sql(multi_q)
        assert "Multi-statement execution is strictly disallowed" in str(exc.value)
