from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING

from textual.containers import Container

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from tuiapp.app import TUIApplication
    from tuiapp.screens.base_screen import BaseScreen


class BaseView(Container):
    """Base class for all views."""

    DEFAULT_CLASSES = "view-container"

    def compose(self) -> ComposeResult:
        yield from self.compose_view()

    """Each subclass should handle button events of the view."""

    @abstractmethod
    def compose_view(self) -> ComposeResult:
        """Define the actual content of the view.

        Subclasses must implement this method to yield the widgets
        that make up the view's body.

        Yields:
            Widget instances for the view content.
        """
        pass

    @abstractmethod
    def on_view_activated(self) -> None:
        """Handle actions when the view becomes active.

        Subclasses must implement this to update the view state
        when it receives new data.
        """
        pass

    @abstractmethod
    def on_view_closed(self) -> None:
        """Handle cleanup when the view is closed.

        Subclasses must implement this to perform any necessary cleanup.
        """
        pass

    @property
    def screen(self) -> BaseScreen:
        """Get the parent screen cast to the base screen type.

        Returns:
            The BaseScreen instance this view belongs to.
        """
        return super().screen  # type: ignore

    @property
    def app(self) -> TUIApplication:
        """Get the application instance cast to the TUI application type.

        Returns:
            The TUIApplication instance.
        """
        return super().app  # type: ignore
