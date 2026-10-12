from datetime import date

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Inventory & Stock Dashboard", page_icon="📦", layout="wide")

CURRENCY = "RM"
STATUS_ORDER = ["Out of Stock", "Low Stock", "In Stock"]
STATUS_COLOR = {"Out of Stock": "#c62828", "Low Stock": "#f9a825", "In Stock": "#2e7d32"}
STATUS_ICON = {"Out of Stock": "🔴", "Low Stock": "🟡", "In Stock": "🟢"}

st.markdown("""
<style>
.banner{background:linear-gradient(135deg,#0a1f44,#12346b);color:#fff;border-radius:16px;
        padding:34px 20px;text-align:center;margin-bottom:22px;box-shadow:0 6px 18px rgba(0,0,0,.25);}
.banner h1{color:#fff;margin:0 0 10px 0;font-size:2.2rem;letter-spacing:.5px;}
.banner .sub{font-size:1.1rem;font-weight:600;margin-bottom:6px;}
.banner .meta{font-size:.95rem;opacity:.9;}
.pill{display:inline-block;margin:12px 0 8px 0;padding:6px 18px;border-radius:20px;
      background:rgba(255,255,255,.15);border:1px solid rgba(255,255,255,.35);font-weight:700;font-size:.85rem;}
.kpi{background:#fff;border-left:6px solid var(--c);border-radius:10px;padding:16px 20px;
     box-shadow:0 2px 8px rgba(0,0,0,.12);}
.kpi .t{font-size:.75rem;color:#777;text-transform:uppercase;letter-spacing:.6px;}
.kpi .v{font-size:1.7rem;font-weight:700;color:#222;margin-top:6px;}
.badge{display:inline-block;padding:5px 14px;border-radius:14px;font-weight:700;font-size:.85rem;margin-right:8px;}
</style>
""", unsafe_allow_html=True)


def banner(title, subtitle, version="OFFICIAL VER 1.0", admin="System Administrator"):
    today = date.today().strftime("%A, %d %B %Y")
    st.markdown(f"""
    <div class="banner">
      <h1>{title}</h1>
      <div class="sub">{subtitle}</div>
      <div class="meta">{today}</div>
      <div class="pill">{version}</div>
      <div class="meta">Administrator: <b>{admin}</b></div>
    </div>""", unsafe_allow_html=True)


def kpi(title, value, color):
    st.markdown(f'<div class="kpi" style="--c:{color}"><div class="t">{title}</div>'
                f'<div class="v">{value}</div></div>', unsafe_allow_html=True)


@st.cache_data
def make_demo():
    rng = np.random.default_rng(7)
    items = {
        "Raw Materials": ["Steel Sheet 2mm", "Aluminium Rod 20mm", "Copper Wire 1.5mm", "PVC Granules 25kg", "Rubber Gasket Roll", "Plywood 18mm", "Epoxy Resin 5L", "Cotton Fabric Roll"],
        "Packaging": ["Carton Box Small", "Carton Box Large", "Bubble Wrap Roll", "Packing Tape 48mm", "Stretch Film 500mm", "Shipping Labels 100x150", "Plastic Pallet Wrap", "Paper Void Fill"],
        "Spare Parts": ["Ball Bearing 6204", "V-Belt A42", "Hydraulic Hose 1/2in", "Proximity Sensor M12", "Contactor 25A", "Pneumatic Cylinder 50mm", "Motor Coupling 24mm", "Gear Oil 20L"],
        "Safety & PPE": ["Safety Helmet", "Safety Gloves (pair)", "Safety Boots 9", "Ear Plugs (box)", "Face Mask N95 (box)", "Reflective Vest", "Safety Goggles", "First Aid Kit"],
        "Finished Goods": ["Product A - Standard", "Product A - Premium", "Product B - Standard", "Product B - Premium", "Product C - Mini", "Product C - Max", "Product D - Basic", "Product D - Plus"],
    }
    locations = ["Warehouse A - Rack A1", "Warehouse A - Rack A2", "Warehouse A - Rack A3",
                 "Warehouse B - Rack B1", "Warehouse B - Rack B2", "Cold Room", "Store Front"]
    suppliers = ["Maju Supplies Sdn Bhd", "Prima Industrial", "Sinar Trading", "Global Parts Co", "Bumi Packaging"]
    rows, n = [], 1
    for cat, names in items.items():
        for name in names:
            lvl = int(rng.integers(20, 120))
            roll = rng.random()
            qty = 0 if roll < 0.12 else int(rng.integers(1, lvl + 1)) if roll < 0.35 else int(rng.integers(lvl + 1, lvl * 4))
            rows.append({"sku": f"SKU-{n:04d}", "item_name": name, "category": cat,
                         "location": str(rng.choice(locations)), "supplier": str(rng.choice(suppliers)),
                         "qty_on_hand": qty, "reorder_level": lvl, "unit_cost": round(float(rng.uniform(3, 250)), 2)})
            n += 1
    return pd.DataFrame(rows)


REQUIRED = ["sku", "item_name", "category", "location", "supplier", "qty_on_hand", "reorder_level", "unit_cost"]

banner("INVENTORY & STOCK DASHBOARD", "Real-Time Stock Control & Reorder Tracker")

# ---------------- Sidebar ----------------
st.sidebar.header("Data & Filters")
up = st.sidebar.file_uploader("Upload your inventory file (CSV / Excel)", type=["csv", "xlsx"])
if up is not None:
    df = pd.read_csv(up) if up.name.endswith(".csv") else pd.read_excel(up)
    missing = [c for c in REQUIRED if c not in df.columns]
    if missing:
        st.error(f"Missing columns: {', '.join(missing)}")
        st.stop()
else:
    df = make_demo()
    st.sidebar.caption("Using demo data. Upload a file to analyse your own stock.")

df["status"] = np.where(df["qty_on_hand"] <= 0, "Out of Stock",
                np.where(df["qty_on_hand"] <= df["reorder_level"], "Low Stock", "In Stock"))
df["stock_value"] = df["qty_on_hand"] * df["unit_cost"]

query = st.sidebar.text_input("🔍 Search item name or SKU", placeholder="Type, then press Enter")
status_f = st.sidebar.selectbox("Status", ["All Statuses"] + STATUS_ORDER)

# ---------------- Reorder report (always uses the full inventory) ----------------
rr = df[df["status"].isin(["Out of Stock", "Low Stock"])].copy()
rr["suggested_order_qty"] = (rr["reorder_level"] * 2 - rr["qty_on_hand"]).clip(lower=0)
rr["estimated_cost"] = (rr["suggested_order_qty"] * rr["unit_cost"]).round(2)
rr["_o"] = rr["status"].map({s: i for i, s in enumerate(STATUS_ORDER)})
rr = rr.sort_values(["_o", "supplier", "item_name"])
rr_cols = ["sku", "item_name", "category", "location", "supplier", "status",
           "qty_on_hand", "reorder_level", "suggested_order_qty", "unit_cost", "estimated_cost"]

st.sidebar.download_button(
    f"⬇ Export Reorder Report ({len(rr)} items)",
    data=rr[rr_cols].to_csv(index=False).encode("utf-8"),
    file_name=f"reorder_report_{date.today().isoformat()}.csv",
    mime="text/csv", disabled=rr.empty)

# ---------------- Filter ----------------
d = df.copy()
if query.strip():
    q = query.strip()
    d = d[d["item_name"].str.contains(q, case=False, regex=False) | d["sku"].str.contains(q, case=False, regex=False)]
if status_f != "All Statuses":
    d = d[d["status"] == status_f]

# ---------------- KPIs ----------------
oos = int((d["status"] == "Out of Stock").sum())
c1, c2, c3, c4 = st.columns(4)
with c1: kpi("Total Stock Value", f"{CURRENCY} {d['stock_value'].sum():,.2f}", "#1976d2")
with c2: kpi("Total Items in Hand", f"{int(d['qty_on_hand'].sum()):,} units", "#7b1fa2")
with c3: kpi("Low Stock Items", f"{int((d['status'] == 'Low Stock').sum())}", "#f9a825")
with c4: kpi("Out-of-Stock Alert", f"{oos} item(s)" if oos else "All clear ✅", "#c62828")
st.write("")

counts = d["status"].value_counts()
badges = "".join(
    f'<span class="badge" style="background:{STATUS_COLOR[s]};color:{"#212121" if s == "Low Stock" else "#fff"}">'
    f'{STATUS_ICON[s]} {s}: {int(counts.get(s, 0))}</span>' for s in STATUS_ORDER)
st.markdown(badges, unsafe_allow_html=True)
st.write("")

if d.empty:
    st.warning("No items match your search.")
    st.stop()

# ---------------- Chart ----------------
by_loc = d.groupby(["location", "status"])["qty_on_hand"].sum().reset_index()
fig = px.bar(by_loc, x="location", y="qty_on_hand", color="status",
             category_orders={"status": STATUS_ORDER}, color_discrete_map=STATUS_COLOR,
             title="Stock on Hand by Warehouse / Rack Location",
             labels={"location": "Location", "qty_on_hand": "Units on Hand", "status": "Status"})
fig.update_layout(height=420, template="plotly_white", barmode="stack")
st.plotly_chart(fig)

# ---------------- Table ----------------
st.subheader("Item List (most urgent first)")
view = d.assign(_o=d["status"].map({s: i for i, s in enumerate(STATUS_ORDER)})).sort_values(["_o", "qty_on_hand"])
view = view[["sku", "item_name", "category", "location", "qty_on_hand", "reorder_level", "stock_value", "status"]]
view.columns = ["SKU", "Item", "Category", "Location", "On Hand", "Reorder Level", "Stock Value (RM)", "Status"]


def color_status(v):
    bg = STATUS_COLOR[v]
    return f"background-color:{bg};color:{'#212121' if v == 'Low Stock' else '#fff'};font-weight:700"


styler = view.style.format({"Stock Value (RM)": "{:,.2f}"})
styler = (styler.map if hasattr(styler, "map") else styler.applymap)(color_status, subset=["Status"])
st.dataframe(styler, hide_index=True)
