import streamlit as st


def render_role_access_tab(client_id: str) -> None:
    del client_id
    st.subheader("Role Access")
    st.info("Role access management must be performed via backend RBAC APIs.")
