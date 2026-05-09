from __future__ import annotations

from typing import TYPE_CHECKING

from textual import on
from textual.containers import Container, Vertical
from textual.reactive import reactive
from textual.validation import Number
from textual.widgets import Button, Input, RadioButton, RadioSet, Static

from tuiapp.api.court.schema import CourtResult, CreateCourtRequest
from tuiapp.widgets.buttons import PrimaryButton, SecondaryButton
from tuiapp.widgets.inputs import TextInput
from tuiapp.widgets.modals.base_modal import BaseModal

if TYPE_CHECKING:
    from textual.app import ComposeResult
    from textual.events import Resize


class CreateCourtModal(BaseModal):
    """Modal for creating a new court."""

    SMALL_WIDTH_THRESHOLD = 64

    small: reactive[bool] = reactive(False)

    def watch_small(self, value: bool) -> None:
        self.set_class(value, "small")

    def on_resize(self, event: Resize) -> None:
        self.small = event.size.width < self.SMALL_WIDTH_THRESHOLD

    def compose_modal(self) -> ComposeResult:
        """Compose the modal with court detail inputs and action buttons."""

        yield Static("🎾", id="court-icon")
        yield Static("Create New Court", id="modal-title")

        with Vertical(classes="field"):
            yield Static("Court Name*", classes="field-label")
            yield TextInput(placeholder="", id="court-name", classes="info-value")

        with Vertical(classes="field"):
            yield Static("Location", classes="field-label")
            yield TextInput(placeholder="", id="court-location", classes="info-value")

        with Vertical(classes="field"):
            yield Static("Surface Type*", classes="field-label")
            yield TextInput(placeholder="", id="court-surface", classes="info-value")

        with Vertical(classes="field"):
            yield Static("Price (per hour)*", classes="field-label")
            yield Input(
                id="court-price",
                classes="info-value price-value",
                validators=[Number(minimum=0)],
                type="number",
            )

        with Vertical(classes="field"):
            yield Static("Facility Type*", classes="field-label")
            with RadioSet(id="court-facility"):
                yield RadioButton("Indoor", id="court-facility-indoor")
                yield RadioButton("Outdoor", id="court-facility-outdoor")

        with Vertical(classes="field"):
            yield Static("Operating Hours", classes="field-label")
            yield TextInput(placeholder="", id="court-hours", classes="info-value")

        with Container(id="buttons-container"):
            yield PrimaryButton("Create Court", variant="success", id="create")
            yield SecondaryButton("Cancel", variant="warning", id="close")

    @on(Button.Pressed, "#close")
    def cancel(self) -> None:
        """Closes the modal when the 'Cancel' button is clicked."""
        self.app.pop_screen()

    @on(Button.Pressed, "#create")
    async def create(self) -> None:
        """Validates inputs and submits the court creation request."""
        name = self.query_one("#court-name", TextInput).value
        location = self.query_one("#court-location", TextInput).value
        surface = self.query_one("#court-surface", TextInput).value
        price_str = self.query_one("#court-price", Input).value
        hours = self.query_one("#court-hours", TextInput).value

        facility_set = self.query_one("#court-facility", RadioSet)
        selected = facility_set.pressed_button
        is_indoor: bool | None = None
        if selected is not None:
            is_indoor = selected.id == "court-facility-indoor"

        if not name:
            self.notify("Please enter the court name", title="Validation", severity="warning")
            return

        if not surface:
            self.notify("Please enter the surface type", title="Validation", severity="warning")
            return

        if not price_str:
            self.notify("Please enter the price per hour", title="Validation", severity="warning")
            return

        try:
            price = float(price_str)
            if price < 0:
                raise ValueError

        except ValueError:
            self.notify("Please enter a valid price", title="Validation", severity="warning")
            return

        if is_indoor is None:
            self.notify("Please select a facility type", title="Validation", severity="warning")
            return

        request = CreateCourtRequest(
            name=name,
            surface_type=surface,
            is_indoor=is_indoor,
            location=location or None,
            price_per_hour=price,
            working_hours=hours or None,
        )

        result: CourtResult = await self.app.court.post_court(request)  # type: ignore

        if result.status != "success":
            self.notify(result.message, title="Court Creation", severity="error")
            return

        self.notify("Successfully created a new court", title="Court Creation")
        self.dismiss(True)
