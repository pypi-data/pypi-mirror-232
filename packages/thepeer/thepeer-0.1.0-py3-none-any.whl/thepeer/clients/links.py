from typing import Optional

from thepeer._base import BaseClient, BaseAsyncClient
from thepeer.utils import HTTPMethod, Currency, Response


class LinkClient(BaseClient):
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

    def get_user_links(self, user_reference: str) -> Response:
        """Fetch all linked accounts of a user.

        Args:
            user_reference: The user’s reference — the one returned
                when the user was indexed.

        Returns:
            Response: A dataclass containing the HTTP status code and
                data returned by thepeer servers
        """
        return self.api_call(
            endpoint_path=f"/users/{user_reference}/links", method=HTTPMethod.GET
        )

    def get_linked_account(self, link_id: str) -> Response:
        """Fetch a user's linked account's details.

        Args:
            link_id: The link’s identifier

        Returns:
            Response: A dataclass containing the HTTP status code and
                data returned by thepeer servers
        """
        return self.api_call(endpoint_path=f"/link/{link_id}", method=HTTPMethod.GET)

    def charge(
        self, link_id: str, amount: int, remark: str, currency: Currency = Currency.NGN
    ) -> Response:
        """Charge a user’s linked account.

        Args:
            link_id: The link’s identifier
            amount: The amount you are debiting the customer. This should be in kobo.
            remark: The narration of the charge.
            currency: The currency of the transaction.

        Returns:
            Response: A dataclass containing the HTTP status code and
                data returned by thepeer servers
        """
        data = {"amount": amount, "remark": remark, "currency": currency}
        return self.api_call(
            endpoint_path=f"/link/{link_id}/charge", method=HTTPMethod.POST, data=data
        )


class AsyncLinkClient(BaseAsyncClient):
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

    async def get_user_links(self, user_reference: str) -> Response:
        """Fetch all linked accounts of a user.

        Args:
            user_reference: The user’s reference — the one returned
                when the user was indexed.

        Returns:
            Response: A dataclass containing the HTTP status code and
                data returned by thepeer servers
        """
        return await self.api_call(
            endpoint_path=f"/users/{user_reference}/links", method=HTTPMethod.GET
        )

    async def get_linked_account(self, link_id: str) -> Response:
        """Fetch a user's linked account's details.

        Args:
            link_id: The link’s identifier

        Returns:
            Response: A dataclass containing the HTTP status code and
                data returned by thepeer servers
        """
        return await self.api_call(
            endpoint_path=f"/link/{link_id}", method=HTTPMethod.GET
        )

    async def charge(
        self, link_id: str, amount: int, remark: str, currency: Currency = Currency.NGN
    ) -> Response:
        """Charge a user’s linked account.

        Args:
            link_id: The link’s identifier
            amount: The amount you are debiting the customer. This should be in kobo.
            remark: The narration of the charge.
            currency: The currency of the transaction.

        Returns:
            Response: A dataclass containing the HTTP status code and
                data returned by thepeer servers
        """
        data = {"amount": amount, "remark": remark, "currency": currency}
        return await self.api_call(
            endpoint_path=f"/link/{link_id}/charge", method=HTTPMethod.POST, data=data
        )
