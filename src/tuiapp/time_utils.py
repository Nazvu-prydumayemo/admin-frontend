"""Timezone conversion utilities for the TUI application."""

from datetime import UTC, date, datetime, time


def utc_to_local(t: time) -> time:
    """Convert a UTC time to the local timezone.

    Args:
        t: The time in UTC.

    Returns:
        The equivalent time in the local timezone.
    """
    dt = datetime.combine(date.today(), t, tzinfo=UTC)
    return dt.astimezone().time()


def local_to_utc(t: time) -> time:
    """Convert a local time to UTC.

    Args:
        t: The time in the local timezone.

    Returns:
        The equivalent time in UTC.
    """
    local_tz = datetime.now().astimezone().tzinfo
    dt = datetime.combine(date.today(), t, tzinfo=local_tz)
    return dt.astimezone(UTC).time()
