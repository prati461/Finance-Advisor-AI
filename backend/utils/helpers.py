from datetime import date, datetime


def today_date() -> date:
    return date.today()


def parse_iso_date(value: str) -> date:
    return datetime.fromisoformat(value).date()


def format_datetime(value: datetime) -> str:
    return value.isoformat()


def get_month_name(month: int) -> str:
    """Get full month name from month number (1-12)."""
    months = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December",
    ]
    return months[month - 1] if 1 <= month <= 12 else ""


def get_month_short_name(month: int) -> str:
    """Get abbreviated month name (e.g., Jan, Feb)."""
    return get_month_name(month)[:3]
