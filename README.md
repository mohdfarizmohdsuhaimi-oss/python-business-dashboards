# 📊 Business Dashboards with Python & Streamlit

Two interactive dashboards built with **Python, Streamlit, Pandas and Plotly**. Both run on demo data out of the box, and you can upload your own CSV or Excel file to analyse real data.

## 🛒 1. E-Commerce Sales Performance Dashboard
Track monthly sales for Shopee, Lazada, TikTok Shop or your own website.

- **KPI cards:** Total Revenue, Total Orders, Average Order Value, Top Selling Product
- **Line chart:** sales trend (daily / weekly / monthly)
- **Bar chart:** best vs worst selling products
- **Pie chart:** sales share by channel
- **Filters:** product category and date range

🔗 **Live demo:**https://fariz-sales-dashboard.streamlit.app/

## 📦 2. Inventory & Stock Management Dashboard
Stock control for factories, warehouses and retail stores.

- **KPI cards:** Total Stock Value, Total Items in Hand, Low Stock Items, Out-of-Stock Alert
- **Alert badges:** 🔴 Out of Stock, 🟡 Low Stock, 🟢 In Stock
- **Bar chart:** stock on hand by warehouse / rack location
- **Search:** find items by name or SKU
- **Export:** download a Reorder Report as CSV

🔗 **Live demo:** https://fariz-inventory-dashboard.streamlit.app/

## 🚀 Run locally

```bash
pip install -r requirements.txt
streamlit run sales_app.py
streamlit run inventory_app.py
```

## 📁 Using your own data

Upload a CSV or Excel file from the sidebar. Required columns:

| Dashboard | Columns |
|-----------|---------|
| Sales | `order_id`, `date`, `product`, `category`, `channel`, `quantity`, `unit_price` |
| Inventory | `sku`, `item_name`, `category`, `location`, `supplier`, `qty_on_hand`, `reorder_level`, `unit_cost` |

## 🛠 Built with
Python • Streamlit • Pandas • NumPy • Plotly

## 📬 Need a custom dashboard?
Contact me on Fiverr:https://www.fiverr.com/sellers/farizsuhaimi/edit
