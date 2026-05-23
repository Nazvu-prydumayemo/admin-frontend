"""Hub screen - the main authenticated user dashboard."""

from typing import ClassVar

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.css.query import NoMatches
from textual.events import Mount
from textual.reactive import reactive
from textual.widgets import Footer, Header, TabbedContent, TabPane

from tuiapp.api.court.schema import Court
from tuiapp.api.order.schema import OrderDetail
from tuiapp.screens.base_screen import AuthScreen
from tuiapp.time_utils import utc_to_local
from tuiapp.widgets.courts.card_container import CardContainer
from tuiapp.widgets.courts.court_card import CourtCard
from tuiapp.widgets.modals.create_court_modal import CreateCourtModal
from tuiapp.widgets.order.order_card import OrderCard
from tuiapp.widgets.stat_card import StatCard
from tuiapp.widgets.stats_container import StatsContainer
from tuiapp.widgets.views.court_view import CourtView
from tuiapp.widgets.views.order_view import OrderView


class DashBoardScreen(AuthScreen):
    """Main dashboard screen displayed after successful authentication."""

    courts: reactive[list[Court] | None] = reactive(None)
    selected_court: reactive[Court | None] = reactive(None)

    orders: reactive[list[OrderDetail] | None] = reactive(None)
    selected_order: reactive[OrderDetail | None] = reactive(None)

    BINDINGS: ClassVar[list[Binding]] = [
        *AuthScreen.BINDINGS,
        Binding(
            key="ctrl+n",
            action="push_court_creation",
            description="New Court",
            tooltip="Create a New Court",
        ),
    ]

    def action_push_court_creation(self) -> None:
        """Open the create court modal."""
        self.show_modal(CreateCourtModal(), self._on_court_created)

    PAGE_SIZE = 100

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.page = 0

    def _get_page_offset(self, page: int) -> int:
        return page * self.PAGE_SIZE

    @on(Mount)
    async def _auth_guard(self) -> None:
        await super()._auth_guard()
        await self._load_courts()
        await self._load_orders()

    async def _on_court_created(self, created: bool) -> None:
        """Called when CreateCourtModal is dismissed. Reloads courts if creation succeeded."""
        if created:
            self.page = 0
            await self._load_courts()

    async def _load_courts(self) -> None:
        result = await self.app.court.get_all_courts(
            self._get_page_offset(self.page), self.PAGE_SIZE
        )
        if result.status != "success":
            self.notify(result.message, title="Courts", severity="error")
            return

        self.courts = result.courts.items if result.courts and result.courts.items else None
        self.selected_court = self.courts[0] if self.courts else None
        self.page += 1

    async def _load_orders(self) -> None:
        result = await self.app.order.get_orders()
        if result.status != "success":
            self.notify(result.message, title="Orders", severity="error")
            return

        self.orders = result.orders if result.orders else None
        self.selected_order = self.orders[0] if self.orders else None

    def watch_selected_court(self, new_court: Court | None = None) -> None:
        try:
            for card in self.query(CourtCard):
                card.selected = card.court == new_court

            view = self.query_one(CourtView)
            view.court = new_court
        except NoMatches:
            pass

    def watch_selected_order(self, new_order: OrderDetail | None = None) -> None:
        try:
            for card in self.query(OrderCard):
                card.selected = card.order == new_order

            view = self.query_one(OrderView)
            view.order = new_order

            court_name = None
            if new_order is not None and self.courts:
                for court in self.courts:
                    if court.id == new_order.court_id:
                        court_name = court.name
                        break
            view.court_name = court_name

            if new_order is not None:
                self.app.call_later(self._load_order_time_range)
        except NoMatches:
            pass

    async def _load_order_time_range(self) -> None:
        order = self.selected_order
        if order is None:
            return
        result = await self.app.order.get_order(order.id)
        if result.status != "success" or result.order is None or not result.order.booking_slots:
            return

        slots = sorted(result.order.booking_slots, key=lambda s: s.start_time)

        def fmt(t):
            return utc_to_local(t).strftime("%H:%M")

        groups = []
        group_start = slots[0].start_time
        group_end = slots[0].end_time

        for s in slots[1:]:
            if s.start_time == group_end:
                group_end = s.end_time
            else:
                groups.append(f"{fmt(group_start)} - {fmt(group_end)}")
                group_start = s.start_time
                group_end = s.end_time
        groups.append(f"{fmt(group_start)} - {fmt(group_end)}")

        time_range = "  ".join(groups)

        try:
            view = self.query_one(OrderView)
            view.booking_time_range = time_range
        except NoMatches:
            pass

    def watch_orders(self, new_orders: list[OrderDetail] | None = None) -> None:
        try:
            container = self.query_one("#order-list", CardContainer)
            container.remove_children()

            if not new_orders:
                return

            for order in new_orders:
                card = OrderCard(order=order)
                card.selected = order == self.selected_order
                container.mount(card)

        except NoMatches:
            pass

    def watch_courts(self, new_courts: list[Court] | None = None) -> None:
        try:
            container = self.query_one("#court-list", CardContainer)
            container.remove_children()

            if not new_courts:
                return

            for court in new_courts:
                card = CourtCard(court=court)
                card.selected = court == self.selected_court
                container.mount(card)

        except NoMatches:
            pass

    def compose(self) -> ComposeResult:
        yield Header()
        with TabbedContent(id="hub-container"):
            with TabPane("Statistics", id="statistics-info"):
                with StatsContainer(id="stats-container"):
                    yield StatCard(
                        title="Total Courts",
                        value="12",
                        description="Active tennis courts",
                    )
                    yield StatCard(
                        title="Total Revenue",
                        value="$4,250",
                        description="This month",
                    )
                    yield StatCard(
                        title="Active Users",
                        value="48",
                        description="Registered players",
                    )
                    yield StatCard(
                        title="Bookings Today",
                        value="15",
                        description="Confirmed reservations",
                    )

            with TabPane("Courts", id="court-info"):
                with CardContainer(id="court-list"):
                    pass

                yield CourtView()

            with TabPane("Orders", id="order-info"):
                with CardContainer(id="order-list"):
                    pass

                yield OrderView()

        yield Footer()

    @on(CourtCard.Pressed)
    def on_court_card_pressed(self, event: CourtCard.Pressed) -> None:
        self.selected_court = event.court_card.court

    @on(OrderCard.Pressed)
    def on_order_card_pressed(self, event: OrderCard.Pressed) -> None:
        self.selected_order = event.order_card.order

    @on(CourtView.CourtDeleted)
    async def on_court_deleted(self) -> None:
        self.page = 0
        await self._load_courts()

    @on(CourtView.CourtChanged)
    async def on_court_changed(self) -> None:
        self.page = 0
        await self._load_courts()
