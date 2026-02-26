import streamlit as st
import pandas as pd
import os
import plotly.express as px
from datetime import datetime

PRODUCTS_FILE = "products.csv"
SALES_FILE = "sales.csv"
USERS_FILE = "users.csv"

# -------------------------
# PAGE CONFIG
# -------------------------
st.set_page_config(page_title="SME Asset Manager", page_icon="💼", layout="wide")
st.title("💼 SME Asset Manager Demo (Single-User Version)")

# -------------------------
# HELPER FUNCTIONS
# -------------------------

def load_users():
    return pd.read_csv(USERS_FILE)


def normalize_product_name(name):
    return str(name).strip().lower()

def check_login(username, password):
    users = load_users()
    if username in users['username'].values:
        user_pass = users.loc[users['username']==username, 'password'].values[0]
        return password == user_pass
    return False

# -------------------------
# PRODUCTS (Weighted Average Inventory)
# -------------------------
def load_products():
    columns = ["product_name","quantity","unit_cost","total_cost"]
    if os.path.exists(PRODUCTS_FILE):
        df = pd.read_csv(PRODUCTS_FILE)

        for col in columns:
            if col not in df.columns:
                df[col] = 0

        df["product_name"] = df["product_name"].apply(normalize_product_name)
        df = df[df["product_name"] != ""].copy()

        df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").fillna(0).astype(int).clip(lower=0)
        df["unit_cost"] = pd.to_numeric(df["unit_cost"], errors="coerce").fillna(0.0).clip(lower=0).round(2)

        df["line_value"] = (df["quantity"] * df["unit_cost"]).round(2)

        consolidated = (
            df.groupby("product_name", as_index=False)
            .agg(quantity=("quantity", "sum"), total_value=("line_value", "sum"))
        )
        consolidated["unit_cost"] = consolidated.apply(
            lambda row: round(row["total_value"] / row["quantity"], 2) if row["quantity"] > 0 else 0.0,
            axis=1,
        )
        consolidated["total_cost"] = (consolidated["quantity"] * consolidated["unit_cost"]).round(2)
        consolidated = consolidated[columns].sort_values("product_name").reset_index(drop=True)

        consolidated.to_csv(PRODUCTS_FILE, index=False)
        return consolidated
    else:
        df = pd.DataFrame(columns=columns)
        df.to_csv(PRODUCTS_FILE, index=False)
        return df

def add_product(product_name, quantity, unit_cost):
    product_name = normalize_product_name(product_name)
    df = load_products()
    quantity = int(quantity)
    unit_cost = round(float(unit_cost),2)

    if not product_name:
        return False, "Enter product name"
    if quantity <= 0:
        return False, "Quantity must be greater than zero"
    if unit_cost < 0:
        return False, "Unit cost cannot be negative"

    if product_name in df["product_name"].values:
        # Weighted Average Cost
        existing = df[df["product_name"] == product_name]
        old_qty = int(existing["quantity"].values[0])
        old_cost = float(existing["unit_cost"].values[0])

        new_total_qty = old_qty + quantity
        new_weighted_cost = round(((old_qty*old_cost)+(quantity*unit_cost))/new_total_qty,2)

        df.loc[df["product_name"] == product_name, "quantity"] = new_total_qty
        df.loc[df["product_name"] == product_name, "unit_cost"] = new_weighted_cost
        df.loc[df["product_name"] == product_name, "total_cost"] = round(new_total_qty*new_weighted_cost,2)
    else:
        total_cost = round(quantity*unit_cost,2)
        new_row = {"product_name":product_name,"quantity":quantity,"unit_cost":unit_cost,"total_cost":total_cost}
        df = pd.concat([df,pd.DataFrame([new_row])], ignore_index=True)

    df.to_csv(PRODUCTS_FILE, index=False)
    return True, "Product added / updated successfully"

# -------------------------
# SALES
# -------------------------
def load_sales():
    columns = [
        "date","product_name","quantity_sold","unit_price",
        "unit_cost","total_sale","cost_of_goods_sold","profit"
    ]
    if os.path.exists(SALES_FILE):
        df = pd.read_csv(SALES_FILE)
        for col in columns:
            if col not in df.columns:
                df[col] = 0

        df["product_name"] = df["product_name"].apply(normalize_product_name)
        df["quantity_sold"] = pd.to_numeric(df["quantity_sold"], errors="coerce").fillna(0).astype(int).clip(lower=0)
        df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce").fillna(0.0).clip(lower=0).round(2)
        df["unit_cost"] = pd.to_numeric(df["unit_cost"], errors="coerce").fillna(0.0).clip(lower=0).round(2)
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df["date"] = df["date"].fillna(datetime.now()).dt.strftime("%Y-%m-%d %H:%M:%S")

        # Recalculate all derived financial fields to repair historical miscalculations.
        df["total_sale"] = (df["quantity_sold"] * df["unit_price"]).round(2)
        df["cost_of_goods_sold"] = (df["quantity_sold"] * df["unit_cost"]).round(2)
        df["profit"] = (df["total_sale"] - df["cost_of_goods_sold"]).round(2)

        df = df[columns]
        df.to_csv(SALES_FILE, index=False)
        return df
    else:
        df = pd.DataFrame(columns=columns)
        df.to_csv(SALES_FILE, index=False)
        return df

def add_sale(product_name, quantity_sold, unit_price):
    product_name = normalize_product_name(product_name)
    df_products = load_products()
    df_sales = load_sales()

    product_row = df_products[df_products["product_name"]==product_name]
    if product_row.empty:
        return False, "Product not found"

    available_qty = int(product_row["quantity"].values[0])
    unit_cost = float(product_row["unit_cost"].values[0])
    quantity_sold = int(quantity_sold)
    unit_price = round(float(unit_price),2)

    if quantity_sold <= 0:
        return False, "Quantity sold must be greater than zero"
    if unit_price < 0:
        return False, "Selling price cannot be negative"

    if quantity_sold > available_qty:
        return False, "Cannot sell more than available stock"

    total_sale = round(quantity_sold*unit_price,2)
    cogs = round(quantity_sold*unit_cost,2)
    profit = round(total_sale - cogs,2)

    new_row = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "product_name": product_name,
        "quantity_sold": quantity_sold,
        "unit_price": unit_price,
        "unit_cost": unit_cost,
        "total_sale": total_sale,
        "cost_of_goods_sold": cogs,
        "profit": profit
    }
    df_sales = pd.concat([df_sales,pd.DataFrame([new_row])], ignore_index=True)
    df_sales.to_csv(SALES_FILE, index=False)

    # Update inventory
    new_qty = available_qty - quantity_sold
    df_products.loc[df_products["product_name"]==product_name, "quantity"] = new_qty
    df_products.loc[df_products["product_name"]==product_name, "total_cost"] = round(new_qty*unit_cost,2)
    df_products.to_csv(PRODUCTS_FILE, index=False)
    return True, "Sale recorded successfully"

# -------------------------
# SESSION STATE
# -------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# -------------------------
# LOGIN PAGE
# -------------------------
if not st.session_state.logged_in:
    st.subheader("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if check_login(username, password):
            st.session_state.logged_in = True
            st.success("Logged in successfully!")
            st.rerun()
        else:
            st.error("Invalid username or password")

# -------------------------
# MAIN APP
# -------------------------
else:

    tab_dashboard, tab_add, tab_assets, tab_sales = st.tabs(
        ["📊 Dashboard", "➕ Add Product", "📦 Assets Summary", "💰 Sales Entry"]
    )

    # -------- DASHBOARD --------
    with tab_dashboard:
        df_products = load_products()
        df_sales = load_sales()

        total_assets = df_products["total_cost"].sum() if not df_products.empty else 0
        total_items = df_products["quantity"].sum() if not df_products.empty else 0
        total_revenue = df_sales["total_sale"].sum() if not df_sales.empty else 0
        total_profit = df_sales["profit"].sum() if not df_sales.empty else 0

        avg_margin = round((total_profit/total_revenue)*100,2) if total_revenue>0 else 0

        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Total Asset Value", f"${total_assets:,.2f}")
        col2.metric("Stock Units", total_items)
        col3.metric("Sales Revenue", f"${total_revenue:,.2f}")
        col4.metric("Total Profit", f"${total_profit:,.2f}")
        col5.metric("Average Margin", f"{avg_margin}%")

        st.markdown("---")
        st.info("⚠ Demo system limitations: Single-user, CSV-based, no FIFO, not tax-compliant, not multi-user safe.")

        if not df_products.empty:
            fig_assets = px.bar(df_products, x="product_name", y="total_cost", title="Asset Value per Product")
            st.plotly_chart(fig_assets, use_container_width=True)

        if not df_sales.empty:
            fig_sales = px.bar(df_sales.groupby("product_name")["total_sale"].sum().reset_index(),
                               x="product_name", y="total_sale", title="Sales Revenue per Product")
            st.plotly_chart(fig_sales, use_container_width=True)

            fig_profit = px.bar(df_sales.groupby("product_name")["profit"].sum().reset_index(),
                               x="product_name", y="profit", title="Profit per Product")
            st.plotly_chart(fig_profit, use_container_width=True)

    # -------- ADD PRODUCT --------
    with tab_add:
        with st.form("add_product_form", clear_on_submit=True):
            product_name = st.text_input("Product Name")
            quantity = st.number_input("Quantity", min_value=1, step=1)
            unit_cost = st.number_input("Unit Cost", min_value=0.0, step=0.01)
            submitted = st.form_submit_button("Add Product")
            if submitted:
                if product_name:
                    ok, message = add_product(product_name, quantity, unit_cost)
                    if ok:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.error("Enter product name")

    # -------- ASSETS SUMMARY --------
    with tab_assets:
        df = load_products()
        if not df.empty:
            st.dataframe(df.style.format({"unit_cost":"${:.2f}","total_cost":"${:.2f}"}))
            st.write("Total Asset Value:", f"${df['total_cost'].sum():,.2f}")
        else:
            st.info("No products available.")

    # -------- SALES ENTRY --------
    with tab_sales:
        df_products = load_products()
        df_instock = df_products[df_products["quantity"]>0]

        if df_instock.empty:
            st.warning("No stock available.")
        else:
            with st.form("sales_form", clear_on_submit=True):
                product_name = st.selectbox("Product", df_instock["product_name"])
                product_row = df_instock[df_instock["product_name"]==product_name]
                available_qty = int(product_row["quantity"].values[0])
                unit_cost = float(product_row["unit_cost"].values[0])

                st.write(f"Available Stock: {available_qty}")
                st.write(f"Purchase Cost: ${unit_cost:.2f}")

                quantity_sold = st.number_input("Quantity Sold", min_value=1, max_value=available_qty, step=1)
                unit_price = st.number_input("Selling Price", min_value=0.0, step=0.01)

                # Calculate profit for this entry
                profit_per_unit = round(unit_price - unit_cost,2)
                total_profit_sale = round(profit_per_unit * quantity_sold,2)
                st.write(f"Profit per Unit: ${profit_per_unit:.2f}")
                st.write(f"Total Profit for this Sale: ${total_profit_sale:.2f}")

                # Show average margin from previous sales
                df_sales = load_sales()
                total_prev_revenue = df_sales["total_sale"].sum()
                total_prev_profit = df_sales["profit"].sum()
                avg_margin = round((total_prev_profit/total_prev_revenue)*100,2) if total_prev_revenue>0 else 0
                st.write(f"Average Margin Based on Previous Sales: {avg_margin}%")

                if profit_per_unit<0:
                    st.error("⚠ Selling below cost!")

                submitted = st.form_submit_button("Record Sale")
                if submitted:
                    ok, message = add_sale(product_name, quantity_sold, unit_price)
                    if ok:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)

    # -------- LOGOUT --------
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()
