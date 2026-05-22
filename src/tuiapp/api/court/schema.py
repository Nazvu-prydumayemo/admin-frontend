from datetime import date, datetime, time
from enum import Enum

from pydantic import BaseModel

from tuiapp.api.schema import Result


class Day(Enum):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6


class Court(BaseModel):
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
    name: str
    description: str | None = None

    surface_type: str
    is_indoor: bool

    location: str | None = None
    price_per_hour: float
    working_hours: str | None = None


class ChangeCourtRequest(BaseModel):
    name: str | None = None
    description: str | None = None

    surface_type: str | None = None
    is_indoor: bool | None = None

    location: str | None = None
    price_per_hour: float | None = None
    working_hours: str | None = None


class CourtSchedule(BaseModel):
    day_of_week: Day
    opening_time: time | None
    closing_time: time | None
    id: int
    court_id: int
    created_at: datetime


class CourtScheduleCreate(BaseModel):
    day_of_week: int
    opening_time: time | None = None
    closing_time: time | None = None


class CourtScheduleSlot(BaseModel):
    start_time: time
    end_time: time
    id: int
    court_id: int
    slot_date: date
    is_available: bool
    order_id: int | None = None
    created_at: datetime


class CourtScheduleSlotsAll(BaseModel):
    court_id: int
    slot_date: date
    available_slots: list[CourtScheduleSlot]
    total_slots: int


class CourtScheduleSlotsAllResult(Result):
    slots: CourtScheduleSlotsAll | None


class CourtScheduleResult(Result):
    schedule: list[CourtSchedule] | None


class CourtResult(Result):
    court: Court | None


class CourtsAll(BaseModel):
    items: list[Court]
    total: int
    skip: int
    limit: int


class CourtsAllResult(Result):
    courts: CourtsAll | None
