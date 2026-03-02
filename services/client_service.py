"""Legacy client service removed.

Client management must be handled by backend APIs.
"""

CLIENT_COLUMNS: list[str] = []


def get_client_profile(client_id: str) -> dict:
    return {"client_id": client_id}


def get_all_clients():
    raise NotImplementedError("Client operations moved to backend APIs.")


def add_client(payload: dict):
    del payload
    raise NotImplementedError("Client operations moved to backend APIs.")


def update_client(client_id: str, payload: dict):
    del client_id, payload
    raise NotImplementedError("Client operations moved to backend APIs.")
