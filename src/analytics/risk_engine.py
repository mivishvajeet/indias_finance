"""Financial Risk Analytics & Mutual Fund Metrics Engine:
Sharpe, Sortino, CAGR, Volatility, Max Drawdown, and Calmar Ratio.
"""
from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd


class FinancialRiskEngine:
    """Calculates risk-adjusted performance and volatility metrics for equities and mutual funds."""

    def __init__(self, risk_free_rate: float = 0.065, trading_days_per_year: int = 252):
        self.risk_free_rate = risk_free_rate  # Default 6.5% (India 10Y G-Sec / Repo benchmark)
        self.annualization_factor = trading_days_per_year

    def calculate_cagr(self, initial_value: float, final_value: float, num_days: int) -> float:
        """Calculates Compound Annual Growth Rate (CAGR)."""
        if initial_value <= 0 or final_value <= 0 or num_days <= 0:
            return 0.0
        years = num_days / 365.25
        if years < 0.01:
            return 0.0
        return float((final_value / initial_value) ** (1.0 / years) - 1.0)

    def calculate_annualized_volatility(self, returns: pd.Series) -> float:
        """Calculates annualized standard deviation of returns: sigma * sqrt(252)."""
        clean_rets = returns.dropna()
        if len(clean_rets) < 2:
            return 0.0
        return float(clean_rets.std() * np.sqrt(self.annualization_factor))

    def calculate_sharpe_ratio(self, returns: pd.Series) -> float:
        """Calculates annualized Sharpe Ratio: (Ann Return - Rf) / Ann Volatility."""
        clean_rets = returns.dropna()
        if len(clean_rets) < 5:
            return 0.0

        daily_rf = (1.0 + self.risk_free_rate) ** (1.0 / self.annualization_factor) - 1.0
        excess_returns = clean_rets - daily_rf
        mean_excess = excess_returns.mean() * self.annualization_factor
        ann_vol = self.calculate_annualized_volatility(clean_rets)

        if ann_vol <= 1e-6:
            return 0.0
        return float(mean_excess / ann_vol)

    def calculate_sortino_ratio(self, returns: pd.Series, target_return: float = 0.0) -> float:
        """Calculates Sortino Ratio penalizing only downside volatility."""
        clean_rets = returns.dropna()
        if len(clean_rets) < 5:
            return 0.0

        daily_rf = (1.0 + self.risk_free_rate) ** (1.0 / self.annualization_factor) - 1.0
        excess_returns = clean_rets - daily_rf
        mean_excess = excess_returns.mean() * self.annualization_factor

        downside = clean_rets[clean_rets < target_return]
        if len(downside) < 2:
            return 0.0

        # Downside deviation relative to target return
        downside_std = np.sqrt(np.mean(downside ** 2)) * np.sqrt(self.annualization_factor)
        if downside_std <= 1e-6:
            return 0.0

        return float(mean_excess / downside_std)

    def calculate_drawdown_series(self, prices: pd.Series) -> Tuple[float, pd.Series]:
        """Calculates running percentage drawdown and maximum historical drawdown."""
        clean_p = prices.dropna()
        if clean_p.empty:
            return 0.0, pd.Series(dtype=float)

        cum_max = clean_p.cummax()
        drawdown = (clean_p - cum_max) / cum_max
        max_dd = float(drawdown.min())
        return max_dd, drawdown

    def profile_asset_series(self, df: pd.DataFrame, price_col: str = "close", date_col: str = "date") -> Dict[str, float]:
        """Produces comprehensive risk/return profile from historical time-series."""
        if df.empty or len(df) < 5:
            return {
                "cagr_pct": 0.0,
                "volatility_pct": 0.0,
                "sharpe_ratio": 0.0,
                "sortino_ratio": 0.0,
                "max_drawdown_pct": 0.0,
                "calmar_ratio": 0.0,
            }

        sorted_df = df.sort_values(by=date_col).copy()
        prices = sorted_df[price_col].astype(float)
        returns = prices.pct_change().dropna()

        # Days count
        dt_start = pd.to_datetime(sorted_df[date_col].iloc[0])
        dt_end = pd.to_datetime(sorted_df[date_col].iloc[-1])
        days = (dt_end - dt_start).days

        cagr = self.calculate_cagr(prices.iloc[0], prices.iloc[-1], days)
        vol = self.calculate_annualized_volatility(returns)
        sharpe = self.calculate_sharpe_ratio(returns)
        sortino = self.calculate_sortino_ratio(returns)
        max_dd, _ = self.calculate_drawdown_series(prices)
        calmar = abs(cagr / max_dd) if abs(max_dd) > 1e-4 else 0.0

        return {
            "cagr_pct": round(cagr * 100, 2),
            "volatility_pct": round(vol * 100, 2),
            "sharpe_ratio": round(sharpe, 2),
            "sortino_ratio": round(sortino, 2),
            "max_drawdown_pct": round(max_dd * 100, 2),
            "calmar_ratio": round(calmar, 2),
        }
