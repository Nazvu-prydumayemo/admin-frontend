from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar

from textual.binding import Binding
from textual.screen import Screen

from tuiapp.api.auth.auth_guard import AuthGuard
from tuiapp.widgets.modals.confirmation_modal import ConfirmationModal

if TYPE_CHECKING:
    from textual.types import CallbackType

    from tuiapp.app import TUIApplication
    from tuiapp.widgets.modals.base_modal import BaseModal


class BaseScreen(Screen):
    """Base screen class. All screens should inherit from this."""

    if TYPE_CHECKING:
        app: TUIApplication  # type: ignore

    def show_modal(self, modal: BaseModal, callback: CallbackType | Any | None = None) -> None:
        """Shows a modal by pushing it onto the stack.

        Args:
            modal: The modal to show.
        """
        self.app.push_screen(modal, callback)  # type: ignore


class AuthScreen(AuthGuard, BaseScreen):  # type: ignore
    """Base screen for authenticated screens requiring a valid session."""

    BINDINGS: ClassVar[list[Binding]] = [
        Binding(
            key="ctrl+l",
            action="logout",
            description="Logout",
            tooltip="Logout",
        ),
    ]

    def _check_logout(self, logout: bool | None) -> None:
        if logout:
            self.app.token_manager.logout()
            self.notify("Goodbye!", title="Logout")

    def action_logout(self) -> None:
        """Show a logout confirmation modal and log the user out if confirmed."""
        self.show_modal(ConfirmationModal("Logout"), self._check_logout)
