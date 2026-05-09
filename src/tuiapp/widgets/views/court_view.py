from textual import on
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, ScrollableContainer, Vertical
from textual.css.query import NoMatches
from textual.message import Message
from textual.reactive import reactive
from textual.validation import Number
from textual.widgets import Input, RadioButton, RadioSet, Static

from tuiapp.api.court.schema import ChangeCourtRequest, Court
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

    class CourtChanged(Message):
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

    def watch_court(self, court: Court) -> None:
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

    @on(PrimaryButton.Pressed, "#update-court")
    async def update_court(self) -> None:
        if not self.court:
            return

        changes = self._get_changes()
        if not changes:
            self.notify("No changes to update.", title="Courts", severity="warning")
            return

        self.screen.show_modal(ConfirmationModal("Update Court"), self._update_court)

    async def _update_court(self, confirm: bool | None) -> None:
        if not confirm:
            return

        if not self.court:
            return

        changes = self._get_changes()
        if not changes:
            return

        response = await self.app.court.patch_court(
            id=self.court.id,
            json=ChangeCourtRequest(**changes),
        )

        if response.status != "success":
            self.notify(response.message, title="Courts", severity="error")
            return

        self.notify(response.message, title="Courts", severity="information")
        self.court = response.court
        self.post_message(self.CourtChanged())

    def _get_changes(self) -> dict:
        """Return only the fields that differ from the current court."""
        court = self.court
        if not court:
            return {}

        changes = {}

        def get_input(widget_id: str) -> str:
            try:
                return self.query_one(f"#{widget_id}", Input).value
            except NoMatches:
                return ""

        name = get_input("court-name")
        if name and name != "N/A" and name != court.name:
            changes["name"] = name

        location = get_input("court-location")
        if location and location != "N/A" and location != (court.location or "N/A"):
            changes["location"] = location

        surface = get_input("court-surface")
        if surface and surface != "N/A" and surface != court.surface_type:
            changes["surface_type"] = surface

        price_str = get_input("court-price")
        try:
            price = float(price_str)
            if price != court.price_per_hour:
                changes["price_per_hour"] = price  # type: ignore
        except (ValueError, TypeError):
            pass

        is_indoor = self._get_facility()
        if is_indoor is not None and is_indoor != court.is_indoor:
            changes["is_indoor"] = is_indoor  # type: ignore

        hours = get_input("court-hours")
        if hours and hours != "N/A" and hours != (court.working_hours or "N/A"):
            changes["working_hours"] = hours

        return changes

    def on_view_closed(self) -> None:
        pass
