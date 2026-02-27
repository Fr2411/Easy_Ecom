import streamlit as st

from config import APP_TITLE, PAGE_ICON, PAGE_TITLE
from services.auth_service import authenticate_user
from services.client_service import ensure_db_structure
from ui.add_product_tab import render_add_product_tab
from ui.assets_tab import render_assets_tab
from ui.dashboard_tab import render_dashboard_tab
from ui.sales_tab import render_sales_tab


ensure_db_structure()
st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON, layout="wide")
st.title(APP_TITLE)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.subheader("Login")
    client_id = st.text_input("Client ID", value="demo_client")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        user = authenticate_user(client_id, username, password)
        if user:
            st.session_state.logged_in = True
            st.session_state.client_id = user["client_id"]
            st.session_state.username = user["username"]
            st.success("Logged in successfully!")
            st.rerun()
        else:
            st.error("Invalid client, username or password")
else:
    active_client_id = st.session_state.get("client_id")
    st.caption(f"Logged in as {st.session_state.get('username')} ({active_client_id})")
    tab_dashboard, tab_add, tab_assets, tab_sales = st.tabs(
        ["📊 Dashboard", "➕ Add Product", "📦 Assets Summary", "💰 Sales Entry"]
    )

    with tab_dashboard:
        render_dashboard_tab(active_client_id)

    with tab_add:
        render_add_product_tab(active_client_id)

    with tab_assets:
        render_assets_tab(active_client_id)

    with tab_sales:
        render_sales_tab(active_client_id)

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.pop("client_id", None)
        st.session_state.pop("username", None)
        st.rerun()
