"""Market Overview Service: Aggregates index performance, market breadth, and sector movers."""
from typing import Any, Dict, List, Optional
import pandas as pd
from data_access.duckdb_client import db_client


class MarketService:
    """Provides market-wide intelligence and breadth analytics from the Gold layer."""

    @staticmethod
    def get_market_snapshot() -> Dict[str, Any]:
        """Returns benchmarks, market breadth (advancers/decliners), and tracked assets."""
        df_latest = db_client.query("""
            WITH ranked AS (
                SELECT 
                    p.*,
                    s.company_name,
                    s.security_type,
                    s.sector_name,
                    ROW_NUMBER() OVER (PARTITION BY p.symbol ORDER BY p.trade_date DESC) as rn
                FROM main_marts.fact_daily_prices p
                LEFT JOIN main_marts.dim_security s ON p.security_id = s.security_id
            )
            SELECT * FROM ranked WHERE rn = 1
        """)

        # Indices
        indices = {}
        for sym, name in [
            ("^NSEI", "NIFTY 50"),
            ("^NSEBANK", "NIFTY BANK"),
            ("^CNXIT", "NIFTY IT"),
            ("^BSESN", "SENSEX"),
        ]:
            row = df_latest[df_latest["symbol"] == sym]
            if not row.empty:
                r = row.iloc[0]
                indices[name] = {
                    "symbol": sym,
                    "close": r["close_price"],
                    "prev_close": r["prev_close_price"] or r["close_price"],
                    "change": r["close_price"] - (r["prev_close_price"] or r["close_price"]),
                    "change_pct": (r["daily_return_pct"] or 0.0) * 100,
                    "date": str(r["trade_date"]),
                }

        # Equities only for breadth
        equities = df_latest[df_latest["security_type"] != "Index"]
        advancers = len(equities[equities["daily_return_pct"] > 0])
        decliners = len(equities[equities["daily_return_pct"] < 0])
        unchanged = len(equities[equities["daily_return_pct"] == 0])

        return {
            "indices": indices,
            "breadth": {
                "advancers": advancers,
                "decliners": decliners,
                "unchanged": unchanged,
                "total_tracked": len(df_latest),
                "advance_decline_ratio": round(advancers / decliners, 2) if decliners > 0 else advancers,
            },
            "latest_trade_date": str(df_latest["trade_date"].max()) if not df_latest.empty else "N/A",
        }

    @staticmethod
    def get_market_movers(limit: int = 5) -> Dict[str, pd.DataFrame]:
        """Returns top gainers and top losers among tracked equities."""
        df_latest = db_client.query("""
            WITH ranked AS (
                SELECT 
                    p.symbol,
                    s.company_name,
                    s.sector_name,
                    p.close_price,
                    p.daily_return_pct,
                    p.volume,
                    ROW_NUMBER() OVER (PARTITION BY p.symbol ORDER BY p.trade_date DESC) as rn
                FROM main_marts.fact_daily_prices p
                JOIN main_marts.dim_security s ON p.security_id = s.security_id
                WHERE s.security_type != 'Index'
            )
            SELECT symbol, company_name, sector_name, close_price, daily_return_pct, volume
            FROM ranked WHERE rn = 1
        """)

        gainers = df_latest.sort_values(by="daily_return_pct", ascending=False).head(limit)
        losers = df_latest.sort_values(by="daily_return_pct", ascending=True).head(limit)

        return {"gainers": gainers, "losers": losers}

    @staticmethod
    def get_sector_performance() -> pd.DataFrame:
        """Calculates equal-weighted sector returns from current stock prices."""
        df_sectors = db_client.query("""
            WITH latest AS (
                SELECT 
                    s.sector_name,
                    p.daily_return_pct,
                    p.volume,
                    ROW_NUMBER() OVER (PARTITION BY p.symbol ORDER BY p.trade_date DESC) as rn
                FROM main_marts.fact_daily_prices p
                JOIN main_marts.dim_security s ON p.security_id = s.security_id
                WHERE s.security_type != 'Index'
            )
            SELECT 
                sector_name,
                COUNT(*) as constituents,
                AVG(daily_return_pct) * 100 as avg_return_pct,
                SUM(volume) as total_volume
            FROM latest
            WHERE rn = 1
            GROUP BY sector_name
            ORDER BY avg_return_pct DESC
        """)
        return df_sectors

    @staticmethod
    def get_market_insights() -> List[str]:
        """Generates deterministic data-driven observations."""
        df = db_client.query("""
            WITH ranked AS (
                SELECT 
                    p.symbol,
                    s.company_name,
                    p.close_price,
                    p.sma_20,
                    p.high_52w,
                    p.daily_return_pct,
                    ROW_NUMBER() OVER (PARTITION BY p.symbol ORDER BY p.trade_date DESC) as rn
                FROM main_marts.fact_daily_prices p
                JOIN main_marts.dim_security s ON p.security_id = s.security_id
            )
            SELECT * FROM ranked WHERE rn = 1
        """)

        insights = []
        if df.empty:
            return ["No active market data available in warehouse."]

        # Stocks above SMA 20
        above_sma20 = df[df["close_price"] > df["sma_20"]]
        pct_above = round((len(above_sma20) / len(df)) * 100, 1)
        insights.append(f"**Market Breadth**: {pct_above}% of tracked assets are trading above their 20-Day SMA ({len(above_sma20)}/{len(df)}).")

        # 52W High Proximity (Within 3%)
        near_high = df[(df["close_price"] >= df["high_52w"] * 0.97) & (df["high_52w"] > 0)]
        if not near_high.empty:
            names = ", ".join(near_high["symbol"].tolist()[:3])
            insights.append(f"**52-Week High Proximity**: {len(near_high)} securities are within 3% of their 52-week highs ({names}).")

        # Top performer
        top_stock = df.sort_values(by="daily_return_pct", ascending=False).iloc[0]
        insights.append(f"**Session Leader**: {top_stock['company_name']} ({top_stock['symbol']}) led gains with {(top_stock['daily_return_pct'] or 0)*100:+.2f}%.")

        return insights
