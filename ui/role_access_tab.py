import streamlit as st

from services.access_service import FEATURE_LABELS, list_user_access_matrix, set_user_feature_access


def render_role_access_tab() -> None:
    st.caption("Platform admin can configure feature-level access for each client user.")
    matrix = list_user_access_matrix()

    editable = matrix.copy()
    for feature in FEATURE_LABELS:
        editable[feature] = editable[feature].astype(bool)

    st.markdown("#### Current access matrix")
    st.dataframe(editable, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.subheader("Update user feature access")

    if editable.empty:
        st.info("No users available.")
        return

    user_keys = editable.apply(lambda r: f"{r['client_id']} | {r['username']} ({r['role']})", axis=1).tolist()
    selected_label = st.selectbox("Select user", user_keys)
    selected_row = editable.iloc[user_keys.index(selected_label)]

    with st.form("feature_toggle_form"):
        st.write(f"Client: **{selected_row['client_id']}** | User: **{selected_row['username']}**")
        access_update = {}
        for feature, label in FEATURE_LABELS.items():
            access_update[feature] = st.toggle(label, value=bool(selected_row[feature]), key=f"feature_{feature}")

        submitted = st.form_submit_button("Save access")

    if submitted:
        ok, message = set_user_feature_access(
            client_id=str(selected_row["client_id"]),
            username=str(selected_row["username"]),
            feature_access=access_update,
        )
        if ok:
            st.success(message)
            st.rerun()
        else:
            st.error(message)
