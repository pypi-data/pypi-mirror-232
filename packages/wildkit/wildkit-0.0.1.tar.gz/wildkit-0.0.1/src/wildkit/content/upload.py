import dataclasses
from typing import Any

import requests
from dataclasses import dataclass

from .const import CONTENT_API, ConfiguratorConst
from .common import get_response_json


def generate_barcodes(ses: requests.Session, count: int) -> list[str]:
    body = {
        "count": count,
    }

    r = ses.post(CONTENT_API + "/content/v1/barcodes", json=body, timeout=ConfiguratorConst.TimeoutSec)
    j = get_response_json(r)

    return j.get("data", [])


@dataclass
class CreateCardSize:
    techSize: str
    wbSize: str
    price: int
    skus: list[str]


@dataclass
class CreateCard:
    characteristics: list[Any]
    vendorCode: str
    sizes: list[CreateCardSize]


def new_property(name: str, value: Any) -> dict:
    return {
        name: value,
    }


def new_property_subject(value: str) -> dict:
    return {
        "Предмет": value,
    }


def create_cards(ses: requests.Session, cards: list[CreateCard]) -> list[str]:
    body = [[dataclasses.asdict(c) for c in cards]]

    r = ses.post(CONTENT_API + "/content/v1/cards/upload", json=body, timeout=ConfiguratorConst.TimeoutSec)
    j = get_response_json(r)

    return j.get("data", [])


@dataclass
class CardCreateError:
    object: str
    vendorCode: str
    updateAt: str
    objectID: int
    errors: list[str]


def get_errors(ses: requests.Session) -> list[CardCreateError]:
    r = ses.get(CONTENT_API + "/content/v1/cards/error/list", timeout=ConfiguratorConst.TimeoutSec)
    j = get_response_json(r)

    return [CardCreateError(**x) for x in j.get("data", [])]
