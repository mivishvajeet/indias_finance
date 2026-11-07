"""NSE Trading Calendar Validator: Differentiates market holidays from data dropouts."""
from datetime import date, timedelta
import logging
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from pydantic import BaseModel
import yaml

logger = logging.getLogger(__name__)


class CalendarAuditReport(BaseModel):
    """Structured audit report analyzing calendar coverage against expected trading days."""

    start_date: date
    end_date: date
    total_calendar_days: int
    weekend_days: int
    official_holiday_days: int
    expected_trading_days: int
    actual_trading_days_found: int
    missing_trading_days: List[date]
    coverage_percentage: float
    is_clean: bool
    details: Dict[str, str] = {}


class CalendarValidator:
    """Validates date sequences against the official National Stock Exchange (NSE) schedule."""

    def __init__(self, holidays_yaml_path: Optional[Path] = None):
        if holidays_yaml_path is None:
            holidays_yaml_path = Path("config/trading_holidays_nse.yaml")
        self.holidays_yaml_path = holidays_yaml_path
        self.holidays: Dict[date, str] = self._load_holidays()

    def _load_holidays(self) -> Dict[date, str]:
        """Loads NSE official holidays from YAML configuration."""
        if not self.holidays_yaml_path.exists():
            logger.warning("Holiday config %s not found. Using empty holiday registry.", self.holidays_yaml_path)
            return {}

        with open(self.holidays_yaml_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        holidays = {}
        for item in data.get("holidays", []):
            try:
                dt = date.fromisoformat(item["date"])
                holidays[dt] = item.get("description", "Official NSE Holiday")
            except Exception as e:
                logger.warning("Error parsing holiday entry %s: %s", item, e)
        return holidays

    def is_trading_day(self, check_date: date) -> Tuple[bool, str]:
        """Checks if a given date is a valid NSE trading day.

        Returns:
            Tuple of (is_open: bool, reason: str)
        """
        # Saturday = 5, Sunday = 6
        if check_date.weekday() >= 5:
            day_name = "Saturday" if check_date.weekday() == 5 else "Sunday"
            return False, f"Weekend ({day_name})"

        if check_date in self.holidays:
            return False, f"NSE Holiday: {self.holidays[check_date]}"

        return True, "Regular NSE Trading Session"

    def get_expected_trading_days(self, start_date: date, end_date: date) -> List[date]:
        """Generates all expected NSE trading days in a closed date interval [start_date, end_date]."""
        expected = []
        curr = start_date
        while curr <= end_date:
            is_open, _ = self.is_trading_day(curr)
            if is_open:
                expected.append(curr)
            curr += timedelta(days=1)
        return expected

    def audit_coverage(
        self,
        actual_dates: Set[date],
        start_date: date,
        end_date: date,
    ) -> CalendarAuditReport:
        """Audits actual ingested dates against expected exchange trading dates.

        Identifies true data dropouts (when market was open but 0 rows exist).
        """
        expected_days = self.get_expected_trading_days(start_date, end_date)
        expected_set = set(expected_days)

        missing_days = sorted(list(expected_set - actual_dates))
        total_cal_days = (end_date - start_date).days + 1

        weekend_count = sum(1 for i in range(total_cal_days) if (start_date + timedelta(days=i)).weekday() >= 5)
        holiday_count = sum(1 for i in range(total_cal_days) if (start_date + timedelta(days=i)) in self.holidays)

        coverage_pct = round((len(actual_dates & expected_set) / max(1, len(expected_days))) * 100.0, 2)
        is_clean = len(missing_days) == 0

        details = {}
        for m in missing_days:
            details[m.isoformat()] = "CRITICAL ANOMALY: Market was OPEN, but NO data was ingested."

        return CalendarAuditReport(
            start_date=start_date,
            end_date=end_date,
            total_calendar_days=total_cal_days,
            weekend_days=weekend_count,
            official_holiday_days=holiday_count,
            expected_trading_days=len(expected_days),
            actual_trading_days_found=len(actual_dates & expected_set),
            missing_trading_days=missing_days,
            coverage_percentage=coverage_pct,
            is_clean=is_clean,
            details=details,
        )
