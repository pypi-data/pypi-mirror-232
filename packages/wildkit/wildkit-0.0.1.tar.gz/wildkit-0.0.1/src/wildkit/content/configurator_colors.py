import requests
from dataclasses import dataclass

from .const import CONTENT_API, ConfiguratorConst
from .common import get_response_json


@dataclass
class Color:
    name: str
    parentName: str


def configurator_get_all_colors(ses: requests.Session) -> list[Color]:
    r = ses.get(CONTENT_API + "/content/v1/directory/colors", timeout=ConfiguratorConst.TimeoutSec)
    j = get_response_json(r)

    result = [Color(**x) for x in j.get("data", [])]

    return result
