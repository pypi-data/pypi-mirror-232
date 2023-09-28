from typing import Any

import requests


def get_response_json(response: requests.Response) -> Any:
    # response.raise_for_status() -- doesn't provide response text in error message
    if response.status_code != 200:
        raise Exception(f"Status {response.status_code} for {response.url}. Body: {response.text}")

    ct = response.headers.get("Content-Type")
    if ct != "application/json":
        raise Exception(f"Expected application/json content-type for {response.url}, got '{ct}'")

    j = response.json()
    if j.get("error", False):
        raise Exception(f'Error for {response.url}: {j.get("errorText", "")}. {j.get("additionalErrors", "")}')

    return j


def tree(items: list, id_field, parent_field: str, children_field) -> list:
    root = [x for x in items if not x[parent_field]]
    for x in root:
        setup_tree_node(x, items, id_field, parent_field, children_field)

    return root


def setup_tree_node(node, items: list, id_field: str, parent_field: str, children_field):
    node[children_field] = [x for x in items if x[parent_field] == node[id_field]]
    for x in node[children_field]:
        setup_tree_node(x, items, id_field, parent_field, children_field)


def print_tree(root_elems: list, children_field: str, stringer):
    _print_tree("", root_elems, children_field, stringer)


def _print_tree(tab: str, elems: list, children_field: str, stringer):
    for x in elems:
        print(f"{tab}{stringer(x)}")
        _print_tree(tab+"  ", x.get(children_field, []), children_field, stringer)
