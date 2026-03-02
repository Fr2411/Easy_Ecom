import streamlit as st

from services import api_client


def render_dashboard_tab(client_id: str) -> None:
    st.subheader("Dashboard")
    try:
        products = api_client.get_products(client_id)
        sales = api_client.get_sales(client_id)
    except Exception as exc:
        st.error(f"Could not load dashboard data: {exc}")
        return

    st.metric("Products", len(products))
    st.metric("Sales", len(sales))
