from datetime import date, datetime, time
from enum import Enum

from pydantic import BaseModel

from tuiapp.api.schema import Result


class Day(Enum):
    """Enum representing days of the week.

    Attributes:
        MONDAY: Monday (value 0).
        TUESDAY: Tuesday (value 1).
        WEDNESDAY: Wednesday (value 2).
        THURSDAY: Thursday (value 3).
        FRIDAY: Friday (value 4).
        SATURDAY: Saturday (value 5).
        SUNDAY: Sunday (value 6).
    """

    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6


class Court(BaseModel):
    """A tennis court model.

    Attributes:
        id: The unique court identifier.
        created_at: When the court was created.
        name: The court name.
        description: Optional description of the court.
        surface_type: The type of surface (e.g. clay, hard).
        is_indoor: Whether the court is indoor.
        location: Optional location description.
        price_per_hour: The rental price per hour.
        working_hours: Optional operating hours description.
    """

    id: int
    created_at: datetime

    name: str
    description: str | None = None

    surface_type: str
    is_indoor: bool

    location: str | None = None
    price_per_hour: float
    working_hours: str | None = None


class CreateCourtRequest(BaseModel):
    """Request model for creating a new court.

    Attributes:
        name: The court name.
        description: Optional description of the court.
        surface_type: The type of surface.
        is_indoor: Whether the court is indoor.
        location: Optional location description.
        price_per_hour: The rental price per hour.
        working_hours: Optional operating hours description.
    """

    name: str
    description: str | None = None

    surface_type: str
    is_indoor: bool

    location: str | None = None
    price_per_hour: float
    working_hours: str | None = None


class ChangeCourtRequest(BaseModel):
    """Request model for updating an existing court.

    Attributes:
        name: The updated court name.
        description: The updated description.
        surface_type: The updated surface type.
        is_indoor: Whether the court is indoor.
        location: The updated location.
        price_per_hour: The updated price per hour.
        working_hours: The updated operating hours.
    """

    name: str | None = None
    description: str | None = None

    surface_type: str | None = None
    is_indoor: bool | None = None

    location: str | None = None
    price_per_hour: float | None = None
    working_hours: str | None = None


class CourtSchedule(BaseModel):
    """A court schedule entry for a specific day.

    Attributes:
        day_of_week: The day of the week.
        opening_time: The opening time (UTC), or None if closed.
        closing_time: The closing time (UTC), or None if closed.
        id: The schedule entry identifier.
        court_id: The court this schedule belongs to.
        created_at: When the schedule entry was created.
    """

    day_of_week: Day
    opening_time: time | None
    closing_time: time | None
    id: int
    court_id: int
    created_at: datetime


class CourtScheduleCreate(BaseModel):
    """Request model for creating a court schedule entry.

    Attributes:
        day_of_week: The day of the week as an integer (0=Monday, 6=Sunday).
        opening_time: The opening time (UTC).
        closing_time: The closing time (UTC).
    """

    day_of_week: int
    opening_time: time | None = None
    closing_time: time | None = None


class CourtScheduleSlot(BaseModel):
    """A single time slot in a court's schedule.

    Attributes:
        start_time: The start time of the slot.
        end_time: The end time of the slot.
        id: The slot identifier.
        court_id: The court this slot belongs to.
        slot_date: The date of the slot.
        is_available: Whether the slot is available for booking.
        order_id: The order ID if the slot is booked, otherwise None.
        created_at: When the slot was created.
    """

    start_time: time
    end_time: time
    id: int
    court_id: int
    slot_date: date
    is_available: bool
    order_id: int | None = None
    created_at: datetime


class CourtScheduleSlotsAll(BaseModel):
    """Container for all available slots on a given date.

    Attributes:
        court_id: The court identifier.
        slot_date: The date of the slots.
        available_slots: The list of available slots.
        total_slots: The total number of slots for the day.
    """

    court_id: int
    slot_date: date
    available_slots: list[CourtScheduleSlot]
    total_slots: int


class CourtScheduleSlotsAllResult(Result):
    """Result model for available slots queries.

    Attributes:
        slots: The available slots data, or None on failure.
        message: A descriptive message about the result.
        status: The status of the operation.
    """

    slots: CourtScheduleSlotsAll | None


class CourtScheduleResult(Result):
    """Result model for court schedule queries.

    Attributes:
        schedule: The list of schedule entries, or None on failure.
        message: A descriptive message about the result.
        status: The status of the operation.
    """

    schedule: list[CourtSchedule] | None


class CourtResult(Result):
    """Result model for court queries.

    Attributes:
        court: The court data, or None on failure.
        message: A descriptive message about the result.
        status: The status of the operation.
    """

    court: Court | None


class CourtsAll(BaseModel):
    """Paginated list of courts.

    Attributes:
        items: The list of courts on this page.
        total: The total number of courts.
        skip: The offset used for pagination.
        limit: The page size used for pagination.
    """

    items: list[Court]
    total: int
    skip: int
    limit: int


class CourtsAllResult(Result):
    """Result model for paginated court list queries.

    Attributes:
        courts: The paginated courts data, or None on failure.
        message: A descriptive message about the result.
        status: The status of the operation.
    """

    courts: CourtsAll | None
