from typing import Optional

from thepeer._base import BaseClient, BaseAsyncClient
from thepeer.utils import HTTPMethod, Response


class TransactionClient(BaseClient):
    def __init__(self, secret_key: Optional[str] = None):
        """
        Args:
             secret_key: your thepeer secret_key. if not provided,
                the client tries to access your thepeer secret key
                from your environmental variables via.
                THEPEER_SECRET_KEY=<secret_key>. if the secret
                key is provided on instantiation, it overrides
                the secret key in the environmental variables.
        """
        super().__init__(secret_key)

    def get(self, transaction_id: str) -> Response:
        """Fetch a transaction.

        Args:
            transaction_id: The transaction’s identifier

        Returns:
            Response: A dataclass containing the HTTP status code and
                data returned by thepeer servers
        """
        return self.api_call(
            endpoint_path=f"/transactions/{transaction_id}", method=HTTPMethod.GET
        )

    def refund(self, transaction_id: str, reason: str) -> Response:
        """Fetch a transaction.

        Args:
            transaction_id: The transaction’s identifier
            reason: why the refund is made.

        Returns:
            Response: A dataclass containing the HTTP status code and
                data returned by thepeer servers
        """
        return self.api_call(
            endpoint_path=f"/transactions/{transaction_id}/refund",
            method=HTTPMethod.POST,
            data={"reason": reason},
        )


class AsyncTransactionClient(BaseAsyncClient):
    def __init__(self, secret_key: Optional[str] = None):
        """
        Args:
             secret_key: your thepeer secret_key. if not provided,
                the client tries to access your thepeer secret key
                from your environmental variables via.
                THEPEER_SECRET_KEY=<secret_key>. if the secret
                key is provided on instantiation, it overrides
                the secret key in the environmental variables.
        """
        super().__init__(secret_key)

    async def get(self, transaction_id: str) -> Response:
        """Fetch a transaction.

        Args:
            transaction_id: The transaction’s identifier

        Returns:
            Response: A dataclass containing the HTTP status code and
                data returned by thepeer servers
        """
        return await self.api_call(
            endpoint_path=f"/transactions/{transaction_id}", method=HTTPMethod.GET
        )

    async def refund(self, transaction_id: str, reason: str) -> Response:
        """Fetch a transaction.

        Args:
            transaction_id: The transaction’s identifier
            reason: why the refund is made.

        Returns:
            Response: A dataclass containing the HTTP status code and
                data returned by thepeer servers
        """
        return await self.api_call(
            endpoint_path=f"/transactions/{transaction_id}/refund",
            method=HTTPMethod.POST,
            data={"reason": reason},
        )
