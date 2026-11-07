"""NSE Equities & Benchmark Indices Ingestion Connector."""
from datetime import date, datetime, timedelta
import logging
from pathlib import Path
from typing import Dict, List, Optional
import yaml

from src.ingestion.base_client import BasePublicClient
from src.ingestion.models import DailyStockRawRecord

logger = logging.getLogger(__name__)


class NseStockIngestor:
    """Ingests daily OHLCV bars for Nifty 50 and Indian benchmark indices."""

    def __init__(self, symbols_config_path: Optional[Path] = None):
        self.client = BasePublicClient()
        if symbols_config_path is None:
            symbols_config_path = Path("config/symbols_nifty50.yaml")
        self.symbols_config_path = symbols_config_path
        self.universe: List[Dict[str, str]] = self._load_universe()

    def _load_universe(self) -> List[Dict[str, str]]:
        if not self.symbols_config_path.exists():
            logger.warning("Config %s not found, using fallback symbols", self.symbols_config_path)
            return [
                {"symbol": "^NSEI", "name": "Nifty 50", "sector": "Index"},
                {"symbol": "RELIANCE.NS", "name": "Reliance", "sector": "Energy"},
                {"symbol": "TCS.NS", "name": "TCS", "sector": "IT"},
                {"symbol": "HDFCBANK.NS", "name": "HDFC Bank", "sector": "Financials"},
            ]
        with open(self.symbols_config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        indices = data.get("indices", [])
        equities = data.get("equities", [])
        return indices + equities

    def fetch_symbol_data(
        self,
        symbol: str,
        start_date: date,
        end_date: date,
    ) -> List[DailyStockRawRecord]:
        """Fetch daily historical price bars for a given symbol via yfinance with fallback."""
        records: List[DailyStockRawRecord] = []
        try:
            import yfinance as yf
            # yfinance end_date is exclusive, add 1 day
            yf_end = end_date + timedelta(days=1)
            ticker = yf.Ticker(symbol)
            df = ticker.history(
                start=start_date.isoformat(),
                end=yf_end.isoformat(),
                interval="1d",
                auto_adjust=False,
            )
            if df is not None and not df.empty:
                for idx, row in df.iterrows():
                    # Handle Timestamp or DatetimeIndex
                    t_date = idx.date() if hasattr(idx, "date") else datetime.strptime(str(idx)[:10], "%Y-%m-%d").date()
                    import math
                    raw_open = float(row.get("Open", 0.0))
                    raw_high = float(row.get("High", 0.0))
                    raw_low = float(row.get("Low", 0.0))
                    raw_close = float(row.get("Close", 0.0))
                    raw_adj = float(row.get("Adj Close", raw_close))
                    raw_vol = row.get("Volume", 0)

                    # Data Quality Filter: skip incomplete in-session bars where OHLC are NaN
                    if any(math.isnan(v) for v in [raw_open, raw_high, raw_low, raw_close]):
                        # If close is NaN but adj_close or open exists, attempt recovery
                        if math.isnan(raw_close) and not math.isnan(raw_adj):
                            raw_close = raw_adj
                        elif math.isnan(raw_close) and not math.isnan(raw_open):
                            raw_close = raw_open
                        else:
                            continue  # Drop incomplete/unclosed session bar

                    clean_vol = 0 if (raw_vol is None or math.isnan(raw_vol)) else int(raw_vol)
                    if clean_vol < 0:
                        clean_vol = 0

                    rec = DailyStockRawRecord(
                        symbol=symbol,
                        trade_date=t_date,
                        open=round(raw_open if not math.isnan(raw_open) else raw_close, 2),
                        high=round(raw_high if not math.isnan(raw_high) else max(raw_open, raw_close), 2),
                        low=round(raw_low if not math.isnan(raw_low) else min(raw_open, raw_close), 2),
                        close=round(raw_close, 2),
                        adj_close=round(raw_adj if not math.isnan(raw_adj) else raw_close, 2),
                        volume=clean_vol,
                        source="yfinance",
                    )
                    records.append(rec)
                logger.info("Successfully fetched %d records for %s from yfinance", len(records), symbol)
                return records
        except Exception as e:
            logger.warning("yfinance fetch failed for %s: %s. Using synthetic offline generator.", symbol, e)

        # Hermetic / Offline fallback generator (simulates authentic Indian price levels)
        return self._generate_fallback_series(symbol, start_date, end_date)

    def _generate_fallback_series(
        self,
        symbol: str,
        start_date: date,
        end_date: date,
    ) -> List[DailyStockRawRecord]:
        """Generates realistic market price data when public internet or API is unreachable."""
        base_prices = {
            "^NSEI": 24200.0,
            "^NSEBANK": 51500.0,
            "RELIANCE.NS": 2950.0,
            "TCS.NS": 4120.0,
            "HDFCBANK.NS": 1640.0,
            "INFY.NS": 1780.0,
            "ICICIBANK.NS": 1210.0,
        }
        current_price = base_prices.get(symbol, 1500.0)
        curr = start_date
        records = []

        import math
        day_count = 0
        while curr <= end_date:
            # Skip weekends (Saturday=5, Sunday=6)
            if curr.weekday() < 5:
                # Modulated deterministic fluctuation
                drift = math.sin(day_count * 0.4) * 0.008 + math.cos(day_count * 0.2) * 0.005
                current_price = round(current_price * (1.0 + drift), 2)
                day_open = round(current_price * 0.998, 2)
                day_high = round(max(day_open, current_price) * 1.012, 2)
                day_low = round(min(day_open, current_price) * 0.988, 2)
                vol = int(1200000 + abs(math.sin(day_count)) * 800000)

                rec = DailyStockRawRecord(
                    symbol=symbol,
                    trade_date=curr,
                    open=day_open,
                    high=day_high,
                    low=day_low,
                    close=current_price,
                    adj_close=current_price,
                    volume=vol,
                    source="synthetic_fallback",
                )
                records.append(rec)
                day_count += 1
            curr += timedelta(days=1)

        logger.info("Generated %d synthetic fallback bars for %s (%s to %s)", len(records), symbol, start_date, end_date)
        return records

    def fetch_universe(
        self,
        symbols: Optional[List[str]] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> List[DailyStockRawRecord]:
        """Ingests daily bars for all configured symbols across the date window."""
        if end_date is None:
            end_date = date.today()
        if start_date is None:
            start_date = end_date - timedelta(days=30)

        target_symbols = symbols or [item["symbol"] for item in self.universe]
        all_records: List[DailyStockRawRecord] = []

        for sym in target_symbols:
            logger.info("Ingesting symbol %s for range %s to %s", sym, start_date, end_date)
            recs = self.fetch_symbol_data(sym, start_date, end_date)
            all_records.extend(recs)

        return all_records
