"""Compatibility wrappers for inventory calls.

Runtime persistence is API-only.
"""

from services import api_client


def load_products(client_id: str):
    return api_client.get_products(client_id)


def add_product(client_id: str, product_name: str, quantity: int, unit_cost: float):
    del quantity
    payload = {
        "client_id": client_id,
        "name": product_name,
        "category": "General",
        "cost": float(unit_cost),
        "price": float(unit_cost),
    }
    api_client.create_product(payload)
    return True, "Product added successfully"
