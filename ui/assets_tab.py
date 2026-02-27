import streamlit as st

from services.inventory_service import load_products


def render_assets_tab(client_id):
    df = load_products(client_id)
    if not df.empty:
        st.dataframe(df.style.format({"unit_cost": "${:.2f}", "total_cost": "${:.2f}"}))
        st.write("Total Asset Value:", f"${df['total_cost'].sum():,.2f}")
    else:
        st.info("No products available.")
