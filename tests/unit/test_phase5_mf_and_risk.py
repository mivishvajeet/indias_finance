"""Unit and Integration Tests for Phase 5 AMFI Mutual Funds and Financial Risk Engine."""
from datetime import date, timedelta
import pandas as pd
import pytest

from src.analytics.risk_engine import FinancialRiskEngine
from src.ingestion.amfi_mf import AmfiMutualFundIngestor, TOP_FUNDS
from src.ingestion.models import MutualFundNavRawRecord


class TestFinancialRiskEngine:
    """Tests the financial risk calculations: CAGR, Volatility, Sharpe, Sortino, Drawdown."""

    @pytest.fixture
    def risk_engine(self):
        return FinancialRiskEngine(risk_free_rate=0.065, trading_days_per_year=252)

    def test_cagr_calculation_exact(self, risk_engine):
        # 100 growing to 144 in exactly 2 years (~730.5 days) is 20% CAGR
        cagr = risk_engine.calculate_cagr(100.0, 144.0, 730)
        assert round(cagr, 2) == 0.20

    def test_volatility_calculation(self, risk_engine):
        returns = pd.Series([0.01, -0.01, 0.01, -0.01, 0.01, -0.01])
        vol = risk_engine.calculate_annualized_volatility(returns)
        assert vol > 0.0
        assert isinstance(vol, float)

    def test_sharpe_and_sortino_ratio(self, risk_engine):
        # Strongly positive trending returns
        returns = pd.Series([0.005, 0.004, -0.001, 0.003, 0.006, 0.002, 0.004] * 10)
        sharpe = risk_engine.calculate_sharpe_ratio(returns)
        sortino = risk_engine.calculate_sortino_ratio(returns)

        assert sharpe > 0.0
        assert sortino > 0.0
        # Sortino should typically exceed Sharpe when downside deviations are small
        assert sortino >= sharpe

    def test_drawdown_series(self, risk_engine):
        # Price climbs to 100, drops to 80, recovers to 90
        prices = pd.Series([50, 75, 100, 90, 80, 85, 90])
        max_dd, dd_series = risk_engine.calculate_drawdown_series(prices)

        # Max drop from 100 to 80 is -20% (-0.20)
        assert round(max_dd, 2) == -0.20
        assert len(dd_series) == len(prices)
        assert dd_series.iloc[2] == 0.0  # Peak at 100 has 0% drawdown

    def test_profile_asset_series(self, risk_engine):
        # Varying positive returns to ensure non-zero volatility
        nav_vals = [100.0]
        for i in range(1, 100):
            nav_vals.append(nav_vals[-1] * (1.0 + 0.003 * ((i % 5) + 1)))

        df = pd.DataFrame({
            "date": pd.date_range("2026-01-01", periods=100, freq="B"),
            "nav": nav_vals,
        })
        profile = risk_engine.profile_asset_series(df, price_col="nav", date_col="date")

        assert profile["cagr_pct"] > 0.0
        assert profile["sharpe_ratio"] > 0.0
        assert profile["max_drawdown_pct"] == 0.0  # Monotonic rise has 0 drawdown


class TestAmfiMutualFundIngestion:
    """Tests AMFI ingestion models and fallback generator."""

    def test_top_funds_metadata(self):
        assert len(TOP_FUNDS) >= 5
        assert "122639" in TOP_FUNDS  # PPFAS
        assert "119063" in TOP_FUNDS  # HDFC

    def test_fallback_generator(self):
        ingestor = AmfiMutualFundIngestor()
        meta = TOP_FUNDS["122639"]
        records = ingestor._generate_fallback_navs(
            scheme_code="122639",
            meta=meta,
            start_date=date(2026, 10, 1),
            end_date=date(2026, 10, 15),
        )

        assert len(records) > 0
        assert all(r.nav > 0 for r in records)
        assert all(r.scheme_code == "122639" for r in records)
        assert records[0].payload_hash != ""
