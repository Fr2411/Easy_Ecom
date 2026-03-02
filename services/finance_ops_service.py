"""Legacy finance ops service removed.

Finance records must be managed by backend APIs.
"""


def get_transactions(client_id: str):
    del client_id
    raise NotImplementedError("Finance transactions moved to backend API.")


def add_transaction(client_id: str, payload: dict, actor_username: str):
    del client_id, payload, actor_username
    raise NotImplementedError("Finance transactions moved to backend API.")


def get_salary_setup(client_id: str):
    del client_id
    raise NotImplementedError("Salary setup moved to backend API.")


def upsert_salary_setup(client_id: str, payload: dict):
    del client_id, payload
    raise NotImplementedError("Salary setup moved to backend API.")
