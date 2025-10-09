"""
Datetime utility functions
"""
from datetime import datetime


def parse_datetime(value):
    """Parse datetime value from various formats"""
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S"):
                try:
                    return datetime.strptime(value, fmt)
                except ValueError:
                    continue
    return None


def format_datetime_for_display(dt):
    """Format datetime for display in UI"""
    if not dt:
        return ""
    return dt.strftime('%Y-%m-%d %H:%M:%S')


def days_since(dt):
    """Calculate days since given datetime"""
    if not dt:
        return None
    return (datetime.now() - dt).days
