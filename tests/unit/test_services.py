"""Unit tests for Market, Equity, Mutual Fund, Lineage, and Incident Services."""
import pytest
from services.market_service import MarketService
from services.equity_service import EquityScreenerService
from services.stock_service import StockAnalyticsService
from services.mutual_fund_service import MutualFundService
from services.macro_service import MacroIntelligenceService
from services.risk_service import RiskAnalyticsService
from services.lineage_service import DataLineageService
from services.incident_service import IncidentService


class TestPlatformServices:
    """Tests all analytical and data engineering service endpoints against warehouse marts."""

    def test_market_service_snapshot(self):
        snapshot = MarketService.get_market_snapshot()
        assert "indices" in snapshot
        assert "breadth" in snapshot
        assert snapshot["breadth"]["total_tracked"] > 0
        assert "NIFTY 50" in snapshot["indices"]

    def test_equity_screener_service(self):
        universe = EquityScreenerService.get_screenable_universe()
        assert not universe.empty
        assert "symbol" in universe.columns
        assert "close_price" in universe.columns

        # Filter by sector
        filtered = EquityScreenerService.apply_filters(universe, symbol_query="RELIANCE")
        assert len(filtered) <= len(universe)

    def test_stock_analytics_service(self):
        profile = StockAnalyticsService.get_security_profile("HDFCBANK.NS")
        assert profile != {}
        assert "metadata" in profile
        assert "history" in profile
        assert "risk_profile" in profile
        assert profile["metadata"]["symbol"] == "HDFCBANK.NS"

    def test_mutual_fund_service(self):
        summary = MutualFundService.get_all_funds_summary()
        assert not summary.empty
        assert "scheme_code" in summary.columns
        assert "sharpe_ratio" in summary.columns
        assert len(summary) >= 5

    def test_macro_service(self):
        macro_summary = MacroIntelligenceService.get_macro_summary()
        assert len(macro_summary) > 0
        codes = [m["code"] for m in macro_summary]
        assert "USD_INR" in codes or "REPO_RATE" in codes

    def test_risk_analytics_service(self):
        profiles = RiskAnalyticsService.get_cross_asset_risk_profiles()
        assert not profiles.empty
        assert "cagr_pct" in profiles.columns
        assert "volatility_pct" in profiles.columns

    def test_lineage_service(self):
        lineage = DataLineageService.get_lineage_graph()
        assert "nodes" in lineage
        assert "edges" in lineage
        assert "coords" in lineage
        assert "raw_stocks_daily" in lineage["nodes"]
        assert "fact_daily_prices" in lineage["nodes"]

    def test_incident_service(self):
        metrics = IncidentService.get_incident_metrics()
        assert metrics["total"] >= 2
        blast = IncidentService.get_blast_radius("main_marts.fact_daily_prices")
        assert "target_table" in blast
        assert len(blast["downstream_impact"]) > 0
