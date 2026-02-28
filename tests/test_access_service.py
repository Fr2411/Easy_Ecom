from services.access_service import FEATURE_LABELS, get_user_feature_access, set_user_feature_access


def test_default_employee_access_excludes_finance_and_admin_features():
    access = get_user_feature_access("demo_client", "employee", "employee")

    assert access["dashboard"] is True
    assert access["add_product"] is True
    assert access["assets"] is True
    assert access["sales"] is True
    assert access["finance"] is False
    assert access["client_admin"] is False


def test_toggle_update_persists_for_user():
    ok, message = set_user_feature_access(
        "demo_client",
        "employee",
        {
            "dashboard": True,
            "add_product": False,
            "assets": True,
            "sales": True,
            "finance": True,
            "client_admin": False,
        },
    )
    assert ok is True
    assert message == "Access updated"

    updated = get_user_feature_access("demo_client", "employee", "employee")
    assert updated["add_product"] is False
    assert updated["finance"] is True

    # Restore default to keep local DB predictable.
    set_user_feature_access(
        "demo_client",
        "employee",
        {feature: feature in {"dashboard", "add_product", "assets", "sales"} for feature in FEATURE_LABELS},
    )
