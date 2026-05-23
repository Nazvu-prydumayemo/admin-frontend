from tuiapp.api.client import APIClient
from tuiapp.api.errors import APIError
from tuiapp.api.order.schema import Order, OrderDetail, OrderDetailResult, OrderRequest, OrderResult


class OrderService:
    """Service for managing order operations via the API."""

    def __init__(self, client: APIClient) -> None:
        self._client = client

    async def get_order(self, id: int) -> OrderResult:
        """Get a single order by its ID.

        Args:
            id: The order ID.

        Returns:
            An OrderResult containing the order data or error details.
        """
        try:
            response = await self._client.get(f"/orders/{id}", response_model=Order)
            return OrderResult(
                message="Loaded orders for current user", status="success", order=response
            )

        except APIError as error:
            if error.status_code == 401:
                return OrderResult(message="Not authenticated", status="error", order=None)

            if error.status_code == 403:
                return OrderResult(message="Inactive account", status="error", order=None)

            if error.status_code == 404:
                return OrderResult(message="Order not found", status="error", order=None)

            return OrderResult(
                message=f"Server Error: {error.status_code}", status="error", order=None
            )

    async def create_order(self, json: OrderRequest) -> OrderResult:
        """Create a new order.

        Args:
            json: The order creation request data.

        Returns:
            An OrderResult containing the created order or error details.
        """
        try:
            response = await self._client.post("/orders/", json=json, response_model=Order)
            return OrderResult(
                message="Loaded orders for current user", status="success", order=response
            )

        except APIError as error:
            if error.status_code == 401:
                return OrderResult(message="Slots not available", status="invalid", order=None)

            if error.status_code == 401:
                return OrderResult(message="Not authenticated", status="error", order=None)

            if error.status_code == 403:
                return OrderResult(message="Inactive account", status="error", order=None)

            if error.status_code == 404:
                return OrderResult(
                    message="Court or booking slots not found", status="error", order=None
                )

            return OrderResult(
                message=f"Server Error: {error.status_code}", status="error", order=None
            )

    async def get_orders(self) -> OrderDetailResult:
        """Get all orders.

        Returns:
            An OrderDetailResult containing the list of orders or error details.
        """
        try:
            response = await self._client.get("/orders/", response_model=list[OrderDetail])
            return OrderDetailResult(
                message="Loaded orders for current user", status="success", orders=response
            )

        except APIError as error:
            if error.status_code == 401:
                return OrderDetailResult(message="Not authenticated", status="error", orders=None)

            if error.status_code == 403:
                return OrderDetailResult(message="Inactive account", status="error", orders=None)

            return OrderDetailResult(
                message=f"Server Error: {error.status_code}", status="error", orders=None
            )
