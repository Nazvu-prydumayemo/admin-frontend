from textual.app import ComposeResult
from textual.containers import Horizontal, ScrollableContainer, Vertical
from textual.css.query import NoMatches
from textual.reactive import reactive
from textual.widgets import Static

from tuiapp.api.order.schema import OrderDetail
from tuiapp.widgets.views.base_view import BaseView


class OrderView(BaseView):
    DEFAULT_CLASSES = "view-container"

    order: reactive[OrderDetail | None] = reactive(None)
    court_name: reactive[str | None] = reactive(None)
    booking_time_range: reactive[str | None] = reactive(None)

    def compose_view(self) -> ComposeResult:
        with ScrollableContainer(id="order-scroll"):
            with Horizontal(id="order-body"):
                with Vertical(id="order-info-card"):
                    yield Static("ORDER INFORMATION", id="order-info-title")

                    yield Static("Order ID", classes="info-label")
                    yield Static("N/A", id="order-id", classes="info-value")

                    yield Static("Created", classes="info-label")
                    yield Static("N/A", id="order-created", classes="info-value")

                    yield Static("Court", classes="info-label")
                    yield Static("N/A", id="order-court", classes="info-value")

                    yield Static("Booking Date", classes="info-label")
                    yield Static("N/A", id="order-date", classes="info-value")

                    yield Static("Total Price", classes="info-label")
                    yield Static("N/A", id="order-total", classes="info-value")

                    yield Static("Booking Time", classes="info-label")
                    yield Static("N/A", id="order-time", classes="info-value")

    def watch_order(self, order: OrderDetail) -> None:
        self.on_view_activated()

    def on_view_activated(self) -> None:
        order = self.order
        is_empty = order is None

        try:
            self.query_one("#order-scroll", ScrollableContainer).disabled = is_empty
        except NoMatches:
            pass

        if is_empty:
            self._set_value("order-id", "N/A")
            self._set_value("order-created", "N/A")
            self._set_value("order-court", "N/A")
            self._set_value("order-date", "N/A")
            self._set_value("order-total", "N/A")
            self._set_value("order-time", "N/A")
            return

        if order is None:
            return

        self._set_value("order-id", f"#{order.id}")
        self._set_value("order-created", order.created_at)
        self._set_value("order-court", self.court_name or f"Court #{order.court_id}")
        self._set_value("order-date", order.booking_date.isoformat())
        self._set_value("order-total", f"${order.total_price:.2f}")
        self._set_value("order-time", self.booking_time_range or "N/A")

    def _set_value(self, widget_id: str, value: str) -> None:
        try:
            self.query_one(f"#{widget_id}", Static).update(value)
        except NoMatches:
            pass

    def on_view_closed(self) -> None:
        pass
