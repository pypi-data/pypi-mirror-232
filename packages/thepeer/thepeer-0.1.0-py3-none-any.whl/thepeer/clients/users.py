from typing import Optional

from thepeer._base import BaseClient, BaseAsyncClient
from thepeer.utils import HTTPMethod, Response


class UserClient(BaseClient):
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

    def create(self, name: str, identifier: str, email: str) -> Response:
        """Index a user on thepeer.

        For you to be able to carry out any transaction via Thepeer,
        just like in person, you will need to have customers. Or as we
        call them on Thepeer, users. To index your users on Thepeer,
        you need to provide identifiers that match the identifier type
        registered on your business. see. https://docs.thepeer.co/users/index-user

        Args:
            name: Kind of obvious, but it’s the user’s name.
            identifier: The user’s identifier. This should match your chosen
                identifier type at signup (email or username)
            email: The user’s email address

        Returns:
            Response: A dataclass containing the HTTP status code and
                data returned by thepeer servers
        """
        data = {"name": name, "identifier": identifier, "email": email}
        return self.api_call(endpoint_path="/users", method=HTTPMethod.POST, data=data)

    def all(self, page: int = 1, per_page: int = 10) -> Response:
        """Fetch all indexed users.

        Args:
            page: The page number to return. If not specify we use a default to page 1
            per_page: The number of records to return per page.
                If not specify we use a default value of 10

        Returns:
            Response: A dataclass containing the HTTP status code and
                data returned by thepeer servers
        """
        return self.api_call(
            endpoint_path=f"/users?page={page}&perPage={per_page}",
            method=HTTPMethod.GET,
        )

    def update(self, user_reference: str, identifier: str) -> Response:
        """Update an indexed user's identifier.

        Args:
            user_reference: The user’s reference — the one
                returned when the user was indexed.
            identifier: The user’s new identifier that matches
                the business’s identifier type.

        Returns:
            Response: A dataclass containing the HTTP status code and
                data returned by thepeer servers
        """
        return self.api_call(
            endpoint_path=f"/users/{user_reference}",
            method=HTTPMethod.PUT,
            data={"identifier": identifier},
        )

    def delete(self, user_reference: str) -> Response:
        """Delete an indexed user.

        Args:
            user_reference: The user’s reference — the one
                returned when the user was indexed.

        Returns:
            Response: A dataclass containing the HTTP status code and
                data returned by thepeer servers
        """
        return self.api_call(
            endpoint_path=f"/users/{user_reference}", method=HTTPMethod.DELETE
        )


class AsyncUserClient(BaseAsyncClient):
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

    async def create(self, name: str, identifier: str, email: str) -> Response:
        """Index a user on thepeer.

        For you to be able to carry out any transaction via Thepeer,
        just like in person, you will need to have customers. Or as we
        call them on Thepeer, users. To index your users on Thepeer,
        you need to provide identifiers that match the identifier type
        registered on your business. see. https://docs.thepeer.co/users/index-user

        Args:
            name: Kind of obvious, but it’s the user’s name.
            identifier: The user’s identifier. This should match your chosen
                identifier type at signup (email or username)
            email: The user’s email address

        Returns:
            Response: A dataclass containing the HTTP status code and
                data returned by thepeer servers
        """
        data = {"name": name, "identifier": identifier, "email": email}
        return await self.api_call(
            endpoint_path="/users", method=HTTPMethod.POST, data=data
        )

    async def all(self, page: int = 1, per_page: int = 10) -> Response:
        """Fetch all indexed users.

        Args:
            page: The page number to return. If not specify we use a default to page 1
            per_page: The number of records to return per page.
                If not specify we use a default value of 10

        Returns:
            Response: A dataclass containing the HTTP status code and
                data returned by thepeer servers
        """
        return await self.api_call(
            endpoint_path=f"/users?page={page}&perPage={per_page}",
            method=HTTPMethod.GET,
        )

    async def update(self, user_reference: str, identifier: str) -> Response:
        """Update an indexed user's identifier.

        Args:
            user_reference: The user’s reference — the one
                returned when the user was indexed.
            identifier: The user’s new identifier that matches
                the business’s identifier type.

        Returns:
            Response: A dataclass containing the HTTP status code and
                data returned by thepeer servers
        """
        return await self.api_call(
            endpoint_path=f"/users/{user_reference}",
            method=HTTPMethod.PUT,
            data={"identifier": identifier},
        )

    async def delete(self, user_reference: str) -> Response:
        """Delete an indexed user.

        Args:
            user_reference: The user’s reference — the one
                returned when the user was indexed.

        Returns:
            Response: A dataclass containing the HTTP status code and
                data returned by thepeer servers
        """
        return await self.api_call(
            endpoint_path=f"/users/{user_reference}", method=HTTPMethod.DELETE
        )
