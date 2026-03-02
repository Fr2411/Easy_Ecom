"""Legacy auth service removed.

Authentication must be handled by backend APIs.
"""

from services import api_client


def authenticate_user(client_id: str, username: str, password: str):
    response = api_client.authenticate_user(
        {"client_id": client_id, "username": username, "password": password}
    )
    return True, response.get("user")


def create_client_user(payload: dict):
    del payload
    raise NotImplementedError("User creation must be implemented via backend API endpoint.")
