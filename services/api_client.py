import os
from typing import Any

import requests

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost/api").rstrip("/")
TIMEOUT_SECONDS = 10


def _request(method: str, path: str, **kwargs: Any) -> Any:
    response = requests.request(method=method, url=f"{API_BASE_URL}{path}", timeout=TIMEOUT_SECONDS, **kwargs)
    response.raise_for_status()
    if response.content:
        return response.json()
    return None


def authenticate_user(payload: dict) -> dict:
    return _request("POST", "/auth/login", json=payload)


def get_products(client_id: str) -> list[dict]:
    return _request("GET", "/products", params={"client_id": client_id})


def create_product(payload: dict) -> dict:
    return _request("POST", "/products", json=payload)


def get_sales(client_id: str) -> list[dict]:
    return _request("GET", "/sales", params={"client_id": client_id})


def create_sale(payload: dict) -> dict:
    return _request("POST", "/sales", json=payload)


class EasyEcomApiClient:
    def login(self, client_id: str, username: str, password: str) -> dict:
        return authenticate_user({"client_id": client_id, "username": username, "password": password})

    def get_products(self, client_id: str) -> list[dict]:
        return get_products(client_id)

    def create_product(self, payload: dict) -> dict:
        return create_product(payload)

    def get_sales(self, client_id: str) -> list[dict]:
        return get_sales(client_id)

    def create_sale(self, payload: dict) -> dict:
        return create_sale(payload)
