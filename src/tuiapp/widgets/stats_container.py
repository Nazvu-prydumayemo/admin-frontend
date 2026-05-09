"""Stats container widget for displaying stats in a scrollable horizontal layout."""

from textual.containers import HorizontalScroll


class StatsContainer(HorizontalScroll):
    """A horizontally scrollable container for StatCard widgets.

    Displays multiple StatCard widgets side by side in the Statistics tab.
    """

    DEFAULT_CLASSES = "stats-container"
