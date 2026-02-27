from __future__ import annotations

from pathlib import Path

import pandas as pd

from config import CLIENTS_FILE, DB_DIR, PRODUCTS_FILE, SALES_FILE, USERS_FILE

CLIENT_COLUMNS = [
    "client_id",
    "client_name",
    "business_overview",
    "opening_hours",
    "closing_hours",
    "max_discount_pct",
    "return_refund_policy",
    "sales_commission_pct",
]
USER_COLUMNS = ["client_id", "username", "password", "role"]
PRODUCT_COLUMNS = ["client_id", "product_name", "quantity", "unit_cost", "total_cost"]
SALES_COLUMNS = [
    "client_id",
    "date",
    "product_name",
    "quantity_sold",
    "unit_price",
    "unit_cost",
    "total_sale",
    "cost_of_goods_sold",
    "profit",
]


SEED_CLIENTS = [
    {
        "client_id": "demo_client",
        "client_name": "Demo Retail Co",
        "business_overview": "General retail store focusing on fast-moving household products.",
        "opening_hours": "09:00",
        "closing_hours": "21:00",
        "max_discount_pct": 15,
        "return_refund_policy": "Returns accepted within 7 days with valid bill.",
        "sales_commission_pct": 3,
    }
]
SEED_USERS = [{"client_id": "demo_client", "username": "admin", "password": "admin123", "role": "owner"}]
SEED_PRODUCTS = [
    {"client_id": "demo_client", "product_name": "sample 1", "quantity": 30, "unit_cost": 2.0, "total_cost": 60.0},
    {"client_id": "demo_client", "product_name": "sample 2", "quantity": 28, "unit_cost": 3.0, "total_cost": 84.0},
    {"client_id": "demo_client", "product_name": "sample 3", "quantity": 2, "unit_cost": 5.0, "total_cost": 10.0},
    {"client_id": "demo_client", "product_name": "sample 4", "quantity": 6, "unit_cost": 3.0, "total_cost": 18.0},
    {"client_id": "demo_client", "product_name": "sample 5", "quantity": 4, "unit_cost": 3.0, "total_cost": 12.0},
]
SEED_SALES = [
    {
        "client_id": "demo_client",
        "date": "2026-02-20 10:00:00",
        "product_name": "sample 1",
        "quantity_sold": 5,
        "unit_price": 2.5,
        "unit_cost": 2.0,
        "total_sale": 12.5,
        "cost_of_goods_sold": 10.0,
        "profit": 2.5,
    }
]


def _ensure_csv(path: Path, columns: list[str], seed_rows: list[dict] | None = None) -> None:
    DB_DIR.mkdir(parents=True, exist_ok=True)
    if path.exists():
        df = pd.read_csv(path)
        for col in columns:
            if col not in df.columns:
                df[col] = ""
        df = df[columns]
        df.to_csv(path, index=False)
        return

    seed_df = pd.DataFrame(seed_rows or [], columns=columns)
    seed_df.to_csv(path, index=False)


def ensure_db_structure() -> None:
    _ensure_csv(CLIENTS_FILE, CLIENT_COLUMNS, SEED_CLIENTS)
    _ensure_csv(USERS_FILE, USER_COLUMNS, SEED_USERS)
    _ensure_csv(PRODUCTS_FILE, PRODUCT_COLUMNS, SEED_PRODUCTS)
    _ensure_csv(SALES_FILE, SALES_COLUMNS, SEED_SALES)


def get_client_profile(client_id: str) -> dict:
    ensure_db_structure()
    clients = pd.read_csv(CLIENTS_FILE)
    row = clients[clients["client_id"].astype(str) == str(client_id)]
    if row.empty:
        return {}
    data = row.iloc[0].to_dict()
    data["max_discount_pct"] = float(data.get("max_discount_pct", 0) or 0)
    data["sales_commission_pct"] = float(data.get("sales_commission_pct", 0) or 0)
    return data
