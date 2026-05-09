"""Stats card widget for displaying dashboard statistics."""

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widget import Widget
from textual.widgets import Static


class StatCard(Widget):
    """A card widget displaying a single stat with title, value, and optional description."""

    DEFAULT_CLASSES = "stat-card"

    def __init__(
        self,
        title: str,
        value: str,
        description: str = "",
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.title = title
        self.value = value
        self.description = description

    def compose(self) -> ComposeResult:
        with Vertical(classes="stat-card-body"):
            yield Static(self.title, classes="stat-card-title")
            yield Static(self.value, classes="stat-card-value")
            if self.description:
                yield Static(self.description, classes="stat-card-description")
