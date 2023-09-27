import os
from abc import ABC, abstractmethod
from typing import Optional, Callable

import httpx
from httpx import Response as APIResponse

from thepeer.utils import HTTPMethod, Response

__version__ = "0.1.0"


class AbstractClient(ABC):
    BASE_URL = "https://api.thepeer.co"
    ENV_SECRET_KEY_NAME = "THEPEER_SECRET_KEY"

    def __init__(self, secret_key: Optional[str] = None):
        if secret_key:
            self.secret_key = secret_key
        else:
            self.secret_key = os.getenv(self.ENV_SECRET_KEY_NAME)
        if not self.secret_key:
            raise ValueError(
                (
                    "secret_key not provided on client instantiation or set"
                    f" in the environmental variables as {self.ENV_SECRET_KEY_NAME}"
                )
            )

    @property
    def headers(self) -> dict:
        return {
            "x-api-key": self.secret_key,
            "Accept": "Application/json",
            "User-Agent": f"thepeer {__version__}",
        }

    @abstractmethod
    def api_call(
        self, endpoint_path: str, method: HTTPMethod, data: Optional[dict] = None
    ) -> Response:
        ...

    def _parse_http_method_callable_kwargs(
        self, endpoint_path: str, method: HTTPMethod, data: Optional[dict]
    ) -> dict:
        kwargs = {
            "url": self.BASE_URL + endpoint_path,
            "headers": self.headers,
            "json": data,
        }
        if (
            method in {HTTPMethod.GET, HTTPMethod.OPTIONS, HTTPMethod.HEAD}
            or data is None
        ):
            kwargs.pop("json", None)
        return kwargs

    def _parse_response(self, response: APIResponse) -> Response:
        return Response(
            status_code=response.status_code,
            data=response.json(),
        )


class BaseClient(AbstractClient):
    def __init__(self, secret_key: Optional[str] = None):
        super().__init__(secret_key)

    def api_call(
        self, endpoint_path: str, method: HTTPMethod, data: Optional[dict] = None
    ) -> Response:
        http_method_callable = self._get_http_method_callable(method)
        http_method_callable_kwargs = self._parse_http_method_callable_kwargs(
            endpoint_path, method, data
        )
        response = http_method_callable(**http_method_callable_kwargs)
        return self._parse_response(response)

    def _get_http_method_callable(self, method: HTTPMethod) -> Callable:
        return {
            HTTPMethod.GET: httpx.get,
            HTTPMethod.POST: httpx.post,
            HTTPMethod.PUT: httpx.put,
            HTTPMethod.PATCH: httpx.patch,
            HTTPMethod.DELETE: httpx.delete,
            HTTPMethod.OPTIONS: httpx.options,
            HTTPMethod.HEAD: httpx.head,
        }[method]


class BaseAsyncClient(AbstractClient):
    def __init__(self, secret_key: Optional[str] = None):
        super().__init__(secret_key)
        self._client = httpx.AsyncClient()

    async def api_call(
        self, endpoint_path: str, method: HTTPMethod, data: Optional[dict] = None
    ) -> Response:
        http_method_callable = getattr(self._client, method)
        http_method_callable_kwargs = self._parse_http_method_callable_kwargs(
            endpoint_path, method, data
        )
        response = await http_method_callable(**http_method_callable_kwargs)
        return self._parse_response(response)
