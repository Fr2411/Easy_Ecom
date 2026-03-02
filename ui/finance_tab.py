import streamlit as st


def render_finance_tab(client_id: str, actor_username: str) -> None:
    del client_id, actor_username
    st.info("Finance operations are managed by backend APIs. UI integration can be added to dedicated endpoints.")
