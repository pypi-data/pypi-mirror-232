import requests


def new_client(token: str) -> requests.Session:
    assert isinstance(token, str) and token != "", "Need not empty API token"

    client = requests.Session()
    client.headers.update({"Authorization": token})

    return client
