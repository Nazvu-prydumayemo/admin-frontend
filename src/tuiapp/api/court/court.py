from datetime import date

from tuiapp.api.client import APIClient
from tuiapp.api.court.schema import (
    ChangeCourtRequest,
    Court,
    CourtResult,
    CourtsAll,
    CourtsAllResult,
    CourtSchedule,
    CourtScheduleCreate,
    CourtScheduleResult,
    CourtScheduleSlotsAll,
    CourtScheduleSlotsAllResult,
    CreateCourtRequest,
)
from tuiapp.api.errors import APIError
from tuiapp.api.schema import Result


class CourtService:
    def __init__(self, client: APIClient) -> None:
        self._client = client

    async def get_court_schedule(self, id: int) -> CourtScheduleResult:
        try:
            response = await self._client.get(
                f"/courts/{id}/schedule", response_model=list[CourtSchedule]
            )
            return CourtScheduleResult(
                message=f"Loaded schedule for court: {id}", status="success", schedule=response
            )

        except APIError as error:
            if error.status_code == 401:
                return CourtScheduleResult(
                    message="Not authenticated", status="invalid", schedule=None
                )

            if error.status_code == 404:
                return CourtScheduleResult(
                    message=f"Court {id} does not exist", status="error", schedule=None
                )

            if error.status_code == 422:
                return CourtScheduleResult(
                    message="Invalid data provided", status="error", schedule=None
                )

            return CourtScheduleResult(
                message=f"Server Error: {error.status_code}", status="error", schedule=None
            )

    async def get_court_available_slots(
        self, id: int, slot_date: date
    ) -> CourtScheduleSlotsAllResult:
        try:
            response = await self._client.get(
                f"/courts/{id}/available-slots?slot_date={slot_date.strftime('%Y-%m-%d')}",
                response_model=CourtScheduleSlotsAll,
            )
            return CourtScheduleSlotsAllResult(
                message=f"Loaded schedule for court: {id}", status="success", slots=response
            )

        except APIError as error:
            if error.status_code == 400:
                return CourtScheduleSlotsAllResult(
                    message=f"Can only query 7 days from {slot_date}", status="invalid", slots=None
                )

            if error.status_code == 401:
                return CourtScheduleSlotsAllResult(
                    message="Not authenticated", status="invalid", slots=None
                )

            if error.status_code == 404:
                return CourtScheduleSlotsAllResult(
                    message=f"Court {id} does not exist", status="error", slots=None
                )

            if error.status_code == 422:
                return CourtScheduleSlotsAllResult(
                    message="Invalid data provided", status="error", slots=None
                )

            return CourtScheduleSlotsAllResult(
                message=f"Server Error: {error.status_code}", status="error", slots=None
            )

    async def get_court(self, id: int) -> CourtResult:
        try:
            response = await self._client.get(f"/courts/{id}", response_model=Court)
            return CourtResult(message=f"Loaded court: {id}", status="success", court=response)

        except APIError as error:
            if error.status_code == 401:
                return CourtResult(message="Not authenticated", status="invalid", court=None)

            if error.status_code == 404:
                return CourtResult(message=f"Court {id} does not exist", status="error", court=None)

            if error.status_code == 422:
                return CourtResult(message="Invalid data provided", status="error", court=None)

            return CourtResult(
                message=f"Server Error: {error.status_code}", status="error", court=None
            )

    async def post_court(self, json: CreateCourtRequest) -> CourtResult:
        try:
            response = await self._client.post("/courts/", json=json, response_model=Court)
            return CourtResult(message=f"Created court: {id}", status="success", court=response)

        except APIError as error:
            if error.status_code == 401:
                return CourtResult(message="Not authenticated", status="invalid", court=None)

            if error.status_code == 422:
                return CourtResult(message="Invalid data provided", status="error", court=None)

            return CourtResult(
                message=f"Server Error: {error.status_code}", status="error", court=None
            )

    async def delete_court(self, id: int) -> CourtResult:
        try:
            response = await self._client.delete(f"/courts/{id}", response_model=Court)
            return CourtResult(message=f"Deleted court: {id}", status="success", court=response)

        except APIError as error:
            if error.status_code == 401:
                return CourtResult(message="Not authenticated", status="invalid", court=None)

            if error.status_code == 404:
                return CourtResult(message=f"Court {id} does not exist", status="error", court=None)

            if error.status_code == 422:
                return CourtResult(message="Invalid data provided", status="error", court=None)

            return CourtResult(
                message=f"Server Error: {error.status_code}", status="error", court=None
            )

    async def patch_court(self, id: int, json: ChangeCourtRequest) -> CourtResult:
        try:
            response = await self._client.patch(f"/courts/{id}", json=json, response_model=Court)
            return CourtResult(message=f"Changed court: {id}", status="success", court=response)

        except APIError as error:
            if error.status_code == 401:
                return CourtResult(message="Not authenticated", status="invalid", court=None)

            if error.status_code == 404:
                return CourtResult(message=f"Court {id} does not exist", status="error", court=None)

            if error.status_code == 422:
                return CourtResult(message="Invalid data provided", status="error", court=None)

            return CourtResult(
                message=f"Server Error: {error.status_code}", status="error", court=None
            )

    async def post_court_schedule(self, court_id: int, json: CourtScheduleCreate) -> Result:
        try:
            _ = await self._client.post(
                f"/courts/{court_id}/schedule", json=json, response_model=CourtSchedule
            )
            return Result(
                message=f"Created schedule for court: {court_id}",
                status="success",
            )

        except APIError as error:
            if error.status_code == 401:
                return Result(
                    message="Not authenticated",
                    status="invalid",
                )

            if error.status_code == 404:
                return Result(
                    message=f"Court {court_id} does not exist",
                    status="error",
                )

            if error.status_code == 422:
                return Result(
                    message="Invalid data provided",
                    status="error",
                )

            return Result(
                message=f"Server Error: {error.status_code}",
                status="error",
            )

    async def get_all_courts(self, skip: int, limit: int = 10) -> CourtsAllResult:
        try:
            response = await self._client.get(
                f"/courts/?skip={skip}&limit={limit}", response_model=CourtsAll
            )
            return CourtsAllResult(message="Loaded all courts", status="success", courts=response)

        except APIError as error:
            if error.status_code == 401:
                return CourtsAllResult(message="Not authenticated", status="invalid", courts=None)

            return CourtsAllResult(
                message=f"Server Error: {error.status_code}", status="error", courts=None
            )
