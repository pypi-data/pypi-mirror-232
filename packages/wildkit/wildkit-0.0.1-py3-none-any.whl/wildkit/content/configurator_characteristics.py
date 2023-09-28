import requests
from dataclasses import dataclass

from .const import CONTENT_API, ConfiguratorConst
from .common import get_response_json


@dataclass
class Characteristic:
    objectName: str
    name: str
    required: bool
    unitName: str
    maxCount: int
    popular: bool
    charcType: int

    def is_numeric(self):
        return self.charcType == 4

    def is_string(self):
        return self.charcType in [0, 1]


def configurator_get_all_characteristics(ses: requests.Session, category_name: str = None) -> list[Characteristic]:
    query = {
        "name": category_name,
    }
    query = {k: v for k, v in query.items() if v}

    r = ses.get(CONTENT_API + "/content/v1/object/characteristics/list/filter", params=query, timeout=ConfiguratorConst.TimeoutSec)
    j = get_response_json(r)

    result = [Characteristic(**x) for x in j.get("data", [])]

    return result



