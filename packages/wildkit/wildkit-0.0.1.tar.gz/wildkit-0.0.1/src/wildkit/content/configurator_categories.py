import requests
from dataclasses import dataclass

from .const import Urls, ConfiguratorConst
from .common import get_response_json


@dataclass
class Category:
    objectID: str
    parentID: str
    objectName: str
    parentName: str
    isVisible: bool


def configurator_get_all_categories(ses: requests.Session, name: str = None) -> list[Category]:
    query = {
        "top": ConfiguratorConst.MaxCategories,
        "name": name,
    }
    query = {k: v for k, v in query.items() if v}

    r = ses.get(Urls.ContentConfiguratorGetAllCategories, params=query, timeout=ConfiguratorConst.TimeoutSec)
    j = get_response_json(r)

    result = [Category(**x) for x in j.get("data", [])]

    return result
