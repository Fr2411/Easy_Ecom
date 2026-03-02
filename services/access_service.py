"""Legacy access service removed.

RBAC/feature access is backend-owned.
"""

FEATURE_LABELS: dict[str, str] = {}


def list_user_access_matrix(client_id: str):
    del client_id
    return []


def set_user_feature_access(client_id: str, username: str, feature_flags: dict[str, bool]):
    del client_id, username, feature_flags
    raise NotImplementedError("Feature access must be managed via backend RBAC APIs.")


def get_user_feature_access(client_id: str, username: str, role: str):
    del client_id, username, role
    return {}
