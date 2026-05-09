from typing import Any

from textual import on
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, ScrollableContainer, Vertical
from textual.css.query import NoMatches
from textual.message import Message
from textual.reactive import reactive
from textual.validation import Number
from textual.widgets import Input, RadioButton, RadioSet, Static

from tuiapp.api.court.schema import Court
from tuiapp.widgets.buttons import DangerButton, PrimaryButton
from tuiapp.widgets.inputs import TextInput
from tuiapp.widgets.modals.confirmation_modal import ConfirmationModal
from tuiapp.widgets.views.base_view import BaseView


class CourtView(BaseView):
    """View that displays general information about a tennis court."""

    DEFAULT_CLASSES = "view-container"

    court: reactive[Court | None] = reactive(None)
    small: reactive[bool] = reactive(False)

    class CourtDeleted(Message):
        pass

    def compose_view(self) -> ComposeResult:
        with ScrollableContainer(id="court-scroll"):
            with Horizontal(id="court-body"):
                with Vertical(id="court-info-card"):
                    yield Static("COURT INFORMATION", id="court-info-title")

                    yield Static("Court Name", classes="info-label")
                    yield TextInput(id="court-name", classes="info-value")

                    yield Static("Location", classes="info-label")
                    yield TextInput(id="court-location", classes="info-value")

                    yield Static("Surface Type", classes="info-label")
                    yield TextInput(id="court-surface", classes="info-value")

                    yield Static("Price (per hour)", classes="info-label")
                    yield Input(
                        id="court-price",
                        classes="info-value price-value",
                        validators=[Number(minimum=0)],
                        type="number",
                    )

                    yield Static("Facility Type", classes="info-label")
                    with RadioSet(id="court-facility"):
                        yield RadioButton("Indoor", id="court-facility-indoor")
                        yield RadioButton("Outdoor", id="court-facility-outdoor")

                    yield Static("Operating Hours", classes="info-label")
                    yield TextInput(id="court-hours", classes="info-value")

            with Container(id="buttons-container"):
                yield PrimaryButton(
                    "Update Court",
                    variant="primary",
                    id="update-court",
                    classes="action-button",
                )
                yield Static(id="span")
                yield DangerButton(
                    "Delete Court",
                    variant="error",
                    id="delete-court",
                    classes="action-button",
                )

    def _set_input(self, widget_id: str, value: str) -> None:
        try:
            self.query_one(f"#{widget_id}", Input).value = value
        except NoMatches:
            pass

    def _set_facility(self, is_indoor: bool) -> None:
        try:
            indoor_btn = self.query_one("#court-facility-indoor", RadioButton)
            outdoor_btn = self.query_one("#court-facility-outdoor", RadioButton)
            indoor_btn.value = False
            outdoor_btn.value = False

            indoor_btn.value = is_indoor
            outdoor_btn.value = not is_indoor

        except NoMatches:
            pass

    def _get_facility(self) -> bool | None:
        """Return True for Indoor, False for Outdoor, None if nothing selected."""
        try:
            radio_set = self.query_one("#court-facility", RadioSet)
            if radio_set.pressed_index == -1:
                return None

            return radio_set.pressed_index == 0

        except NoMatches:
            return None

    def watch_small(self, is_small: bool) -> None:
        try:
            buttons_container = self.query_one("#buttons-container", Container)
            buttons_container.styles.layout = "vertical" if is_small else "horizontal"
            self.query_one("#update-court", PrimaryButton).styles.width = "100%" if is_small else 32
            self.query_one("#delete-court", DangerButton).styles.width = "100%" if is_small else 32

        except NoMatches:
            pass

    def on_resize(self) -> None:
        self.small = self.size.width <= 70

    def watch_court(self, court: Any) -> None:
        self.on_view_activated()

    def on_view_activated(self) -> None:
        court = self.court
        is_empty = court is None

        try:
            self.query_one("#court-scroll", ScrollableContainer).disabled = is_empty
            self.query_one("#update-court", PrimaryButton).disabled = is_empty
            self.query_one("#delete-court", DangerButton).disabled = is_empty
        except NoMatches:
            pass

        if is_empty:
            self._set_input("court-name", "N/A")
            self._set_input("court-location", "N/A")
            self._set_input("court-surface", "N/A")
            self._set_input("court-price", "0.0")
            self._set_facility(False)
            self._set_input("court-hours", "N/A")
            return

        self._set_input("court-name", court.name)
        self._set_input("court-location", court.location or "N/A")
        self._set_input("court-surface", court.surface_type)
        self._set_input("court-price", f"{court.price_per_hour:.2f}")
        self._set_facility(court.is_indoor)
        self._set_input("court-hours", court.working_hours or "N/A")

    @on(DangerButton.Pressed, "#delete-court")
    async def delete_court(self) -> None:
        if not self.court:
            return

        self.screen.show_modal(ConfirmationModal("Delete Court"), self._delete_court)

    async def _delete_court(self, delete: bool | None) -> None:
        if not delete:
            return

        if not self.court:
            return

        response = await self.app.court.delete_court(id=self.court.id)
        if response.status != "success":
            self.notify(response.message, title="Courts", severity="error")
            return

        self.notify(response.message, title="Courts", severity="information")
        self.court = None
        self.post_message(self.CourtDeleted())

    def on_view_closed(self) -> None:
        pass
