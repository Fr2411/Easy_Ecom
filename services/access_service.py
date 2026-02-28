from __future__ import annotations

import pandas as pd

from config import USER_ACCESS_FILE, USERS_FILE
from services.auth_service import load_users
from services.client_service import ensure_db_structure

FEATURE_LABELS = {
    "dashboard": "Dashboard",
    "add_product": "Add Product",
    "assets": "Assets Summary",
    "sales": "Sales Entry",
    "finance": "Finance",
    "client_admin": "Client Admin",
}

BASE_FEATURES = {"dashboard", "add_product", "assets", "sales"}


def _default_enabled_features(role: str, client_id: str) -> set[str]:
    role_name = str(role or "employee").lower()
    if role_name == "admin" and str(client_id) == "__admin__":
        return set(FEATURE_LABELS.keys())
    if role_name == "owner":
        return BASE_FEATURES | {"finance"}
    return set(BASE_FEATURES)



def _bool_series(values: pd.Series) -> pd.Series:
    return values.astype(str).str.strip().str.lower().isin({"1", "true", "yes", "y"})


def ensure_access_records() -> pd.DataFrame:
    ensure_db_structure()
    users = load_users()
    access_df = pd.read_csv(USER_ACCESS_FILE)

    if access_df.empty:
        access_df = pd.DataFrame(columns=["client_id", "username", "feature", "enabled"])

    access_df["client_id"] = access_df.get("client_id", "").astype(str)
    access_df["username"] = access_df.get("username", "").astype(str)
    access_df["feature"] = access_df.get("feature", "").astype(str)
    access_df["enabled"] = _bool_series(access_df.get("enabled", pd.Series([], dtype=object)))

    for _, user in users.iterrows():
        client_id = str(user["client_id"])
        username = str(user["username"])
        role = str(user.get("role", "employee"))

        user_mask = (access_df["client_id"] == client_id) & (access_df["username"] == username)
        existing_features = set(access_df.loc[user_mask, "feature"].astype(str))

        missing = [f for f in FEATURE_LABELS if f not in existing_features]
        if missing:
            defaults = _default_enabled_features(role, client_id)
            rows = [
                {
                    "client_id": client_id,
                    "username": username,
                    "feature": feature,
                    "enabled": feature in defaults,
                }
                for feature in missing
            ]
            access_df = pd.concat([access_df, pd.DataFrame(rows)], ignore_index=True)

    access_df = access_df[access_df["feature"].isin(FEATURE_LABELS.keys())]
    access_df = access_df.drop_duplicates(subset=["client_id", "username", "feature"], keep="last")
    access_df.to_csv(USER_ACCESS_FILE, index=False)
    return access_df


def get_user_feature_access(client_id: str, username: str, role: str) -> dict[str, bool]:
    access_df = ensure_access_records()
    user_rows = access_df[
        (access_df["client_id"].astype(str) == str(client_id))
        & (access_df["username"].astype(str) == str(username))
    ]

    if user_rows.empty:
        return {feature: feature in _default_enabled_features(role, client_id) for feature in FEATURE_LABELS}

    return {
        feature: bool(
            user_rows[user_rows["feature"].astype(str) == feature]["enabled"].astype(bool).iloc[0]
            if not user_rows[user_rows["feature"].astype(str) == feature].empty
            else feature in _default_enabled_features(role, client_id)
        )
        for feature in FEATURE_LABELS
    }


def list_user_access_matrix() -> pd.DataFrame:
    access_df = ensure_access_records()
    users = pd.read_csv(USERS_FILE)
    users["role"] = users["role"].astype(str).str.lower()

    matrix = (
        access_df.pivot_table(
            index=["client_id", "username"],
            columns="feature",
            values="enabled",
            aggfunc="last",
            fill_value=False,
        )
        .reset_index()
        .rename_axis(None, axis=1)
    )

    matrix = matrix.merge(users[["client_id", "username", "role"]], on=["client_id", "username"], how="left")
    matrix = matrix[["client_id", "username", "role", *FEATURE_LABELS.keys()]]
    matrix = matrix.sort_values(["client_id", "username"]).reset_index(drop=True)
    return matrix


def set_user_feature_access(client_id: str, username: str, feature_access: dict[str, bool]) -> tuple[bool, str]:
    access_df = ensure_access_records()
    client_id = str(client_id).strip()
    username = str(username).strip()

    if not client_id or not username:
        return False, "Client ID and username are required"

    users = load_users()
    exists = users[(users["client_id"].astype(str) == client_id) & (users["username"].astype(str) == username)]
    if exists.empty:
        return False, "User not found"

    for feature in FEATURE_LABELS:
        if feature not in feature_access:
            continue
        mask = (
            (access_df["client_id"].astype(str) == client_id)
            & (access_df["username"].astype(str) == username)
            & (access_df["feature"].astype(str) == feature)
        )
        access_df.loc[mask, "enabled"] = bool(feature_access[feature])

    access_df.to_csv(USER_ACCESS_FILE, index=False)
    return True, "Access updated"
