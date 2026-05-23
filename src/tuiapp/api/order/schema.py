from datetime import date

from pydantic import BaseModel

from tuiapp.api.court.schema import CourtScheduleSlot
from tuiapp.api.schema import Result


class OrderRequest(BaseModel):
    """Request model for creating a new order.

    Attributes:
        court_id: The court to book.
        booking_slot_ids: The list of slot IDs to book.
    """

    court_id: int
    booking_slot_ids: list[int]


class OrderDetail(BaseModel):
    """Detailed information about an order.

    Attributes:
        id: The order identifier.
        user_id: The user who placed the order.
        court_id: The court being booked.
        booking_date: The date of the booking.
        total_price: The total price of the order.
        created_at: When the order was created.
    """

    id: int
    user_id: int
    court_id: int
    booking_date: date
    total_price: float
    created_at: str


class OrderDetailResult(Result):
    """Result model for order list queries.

    Attributes:
        orders: The list of orders, or None on failure.
        message: A descriptive message about the result.
        status: The status of the operation.
    """

    orders: list[OrderDetail] | None


class Order(OrderDetail):
    """An order including its booking slot details.

    Attributes:
        booking_slots: The slots associated with this order.
    """

    booking_slots: list[CourtScheduleSlot]


class OrderResult(Result):
    """Result model for single order queries.

    Attributes:
        order: The order data, or None on failure.
        message: A descriptive message about the result.
        status: The status of the operation.
    """

    order: Order | None
