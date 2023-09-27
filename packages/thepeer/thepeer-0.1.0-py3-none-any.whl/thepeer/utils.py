from dataclasses import dataclass
from enum import Enum
from typing import Union


class HTTPMethod(str, Enum):
    GET = "get"
    POST = "post"
    PUT = "put"
    PATCH = "patch"
    DELETE = "delete"
    OPTIONS = "options"
    HEAD = "head"


@dataclass
class Response:
    status_code: int
    data: Union[dict, list]


class ChargeEvent(str, Enum):
    SUCCESS = "success"
    INSUFFICIENT_FUNDS = "insufficient_funds"
    BUSINESS_DECLINE = "business_decline"
    USER_DECLINE = "user_decline"


class Currency(str, Enum):
    NGN = "NGN"
    USD = "USD"


class PaymentChannel(str, Enum):
    SEND = "send"
    CHECKOUT = "checkout"
    DIRECT_CHARGE = "direct_charge"
