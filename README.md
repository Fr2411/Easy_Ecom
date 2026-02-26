# SME Asset Manager Demo

A lightweight Streamlit app for small-business inventory and sales tracking with **weighted-average costing**.

## How to Run

1. Install Python 3.8+
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run Streamlit app:
   ```bash
   streamlit run app.py
   ```
4. Login with:
   - Username: `admin`
   - Password: `admin123`

## Project Flow

1. **Authentication**
   - Credentials are loaded from `users.csv`.
2. **Product ingestion and normalization**
   - `products.csv` is loaded and auto-repaired (missing columns, bad numeric values, inconsistent names).
   - Duplicate product rows are consolidated by name.
   - Inventory value is recalculated from source inputs (`quantity * unit_cost`).
3. **Stock updates (purchases)**
   - New purchases update quantity using weighted-average unit cost.
4. **Sales recording**
   - Sales are validated against available stock.
   - Revenue, COGS, and profit are computed per sale.
   - Inventory quantity and total inventory value are reduced automatically.
5. **Dashboard analytics**
   - Displays total asset value, stock units, revenue, total profit, and average margin.
   - Includes bar charts for assets, sales, and profit by product.

## Critical Logic

- **Weighted Average Cost Formula**
  ```text
  new_unit_cost = ((old_qty * old_cost) + (purchased_qty * purchase_cost)) / (old_qty + purchased_qty)
  ```
- **Sale Calculations**
  ```text
  total_sale = quantity_sold * unit_price
  cogs       = quantity_sold * unit_cost
  profit     = total_sale - cogs
  ```
- **Data Integrity Repairs**
  - Product names are normalized to lowercase/trimmed form.
  - Negative/invalid numeric values are sanitized.
  - Sales derived fields are recalculated on load to fix historical miscalculations.

## Data Files

- `products.csv`: current inventory snapshot.
- `sales.csv`: historical sales ledger.
- `users.csv`: login credentials.

## Dependencies

From `requirements.txt`:

- `streamlit`
- `pandas`
- `plotly`
