import streamlit as st

from services import api_client


def render_assets_tab(client_id: str, include_finance: bool = True) -> None:
    try:
        products = api_client.get_products(client_id)
    except Exception as exc:
        st.error(f"Could not load assets: {exc}")
        return

    if not products:
        st.info("No products available.")
        return

    if include_finance:
        st.dataframe(products, use_container_width=True)
    else:
        redacted = [{"name": p.get("name"), "category": p.get("category")} for p in products]
        st.dataframe(redacted, use_container_width=True)
        st.caption("Employee view hides finance columns by policy.")
