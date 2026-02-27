import pandas as pd

from config import USERS_FILE
from services.client_service import ensure_db_structure


def load_users():
    ensure_db_structure()
    return pd.read_csv(USERS_FILE)


def authenticate_user(client_id, username, password):
    users = load_users()
    match = users[
        (users["client_id"].astype(str) == str(client_id))
        & (users["username"] == username)
        & (users["password"] == password)
    ]
    if match.empty:
        return None
    return match.iloc[0].to_dict()


def check_login(client_id, username, password):
    return authenticate_user(client_id, username, password) is not None
