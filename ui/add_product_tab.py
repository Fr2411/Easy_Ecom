import streamlit as st

from services.inventory_service import add_product, load_products


def render_add_product_tab(client_id):
    st.subheader("Add Product")
    with st.form("add_product_form", clear_on_submit=True):
        product_name = st.text_input("Product Name")
        quantity = st.number_input("Quantity", min_value=1, step=1)
        unit_cost = st.number_input("Unit Cost", min_value=0.0, step=0.01)
        submitted = st.form_submit_button("Add Product")
        if submitted:
            if product_name:
                ok, message = add_product(client_id, product_name, quantity, unit_cost)
                if ok:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
            else:
                st.error("Enter product name")

    st.markdown("---")
    st.subheader("Recently Added Products Statement")
    products_df = load_products(client_id)

    if products_df.empty:
        st.info("No product records found yet for this client.")
        return

    statement_df = products_df.sort_values(by=["product_name"]).reset_index(drop=True)
    statement_df.index = statement_df.index + 1
    st.dataframe(statement_df, use_container_width=True)
