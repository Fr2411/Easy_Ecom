"""Compatibility wrappers for sales calls.

Runtime persistence is API-only.
"""

from services import api_client


def load_sales(client_id: str):
    return api_client.get_sales(client_id)


def add_sale(client_id: str, product_id: str, quantity_sold: int, unit_price: float):
    api_client.create_sale(
        {
            "client_id": client_id,
            "product_id": product_id,
            "quantity": int(quantity_sold),
            "selling_price": float(unit_price),
        }
    )
    return True, "Sale recorded successfully"
