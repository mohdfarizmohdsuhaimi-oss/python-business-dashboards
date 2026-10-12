from datetime import date

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="E-Commerce Sales Dashboard", page_icon="🛒", layout="wide")

CURRENCY = "RM"

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
    rng = np.random.default_rng(42)
    catalog = {
        "Electronics": {"Wireless Earbuds": 79, "Power Bank 10000mAh": 59, "Smart Watch": 149, "Bluetooth Speaker": 99},
        "Fashion": {"T-Shirt Basic": 29, "Jeans Slim Fit": 89, "Instant Hijab": 25, "Sneakers": 129},
        "Beauty": {"Vitamin C Serum": 55, "Sunscreen SPF50": 39, "Matte Lipstick": 35},
        "Home & Kitchen": {"Air Fryer": 199, "Food Container Set": 45, "Queen Bedsheet": 69},
    }
    dates = pd.date_range("2026-01-01", "2026-09-30", freq="D")
    rows = []
    for i in range(4000):
        cat = rng.choice(list(catalog), p=[0.32, 0.28, 0.2, 0.2])
        prod = rng.choice(list(catalog[cat]))
        rows.append({
            "order_id": f"ORD{100000 + i}", "date": rng.choice(dates), "product": prod, "category": cat,
            "channel": rng.choice(["Shopee", "Lazada", "TikTok Shop", "Website"], p=[0.42, 0.25, 0.23, 0.10]),
            "quantity": int(rng.choice([1, 1, 1, 2, 2, 3])), "unit_price": catalog[cat][prod],
        })
    return pd.DataFrame(rows)


REQUIRED = ["order_id", "date", "product", "category", "channel", "quantity", "unit_price"]

banner("E-COMMERCE SALES DASHBOARD", "Sales Performance & Channel Analytics Tracker")

# ---------------- Sidebar ----------------
st.sidebar.header("Data & Filters")
up = st.sidebar.file_uploader("Upload your sales file (CSV / Excel)", type=["csv", "xlsx"])
if up is not None:
    df = pd.read_csv(up) if up.name.endswith(".csv") else pd.read_excel(up)
    missing = [c for c in REQUIRED if c not in df.columns]
    if missing:
        st.error(f"Missing columns: {', '.join(missing)}")
        st.stop()
else:
    df = make_demo()
    st.sidebar.caption("Using demo data. Upload a file to analyse your own sales.")

df["date"] = pd.to_datetime(df["date"])
df["revenue"] = df["quantity"] * df["unit_price"]

category = st.sidebar.selectbox("Product category", ["All Categories"] + sorted(df["category"].unique()))
dr = st.sidebar.date_input("Date range", value=(df["date"].min().date(), df["date"].max().date()),
                           min_value=df["date"].min().date(), max_value=df["date"].max().date())
gran = st.sidebar.selectbox("Trend view", ["Daily", "Weekly", "Monthly"])

if not isinstance(dr, tuple) or len(dr) != 2:
    st.info("Select both a start and an end date.")
    st.stop()

d = df[(df["date"] >= pd.Timestamp(dr[0])) & (df["date"] < pd.Timestamp(dr[1]) + pd.Timedelta(days=1))]
if category != "All Categories":
    d = d[d["category"] == category]
if d.empty:
    st.warning("No data for the selected filters.")
    st.stop()

# ---------------- KPIs ----------------
rev = d["revenue"].sum()
orders = d["order_id"].nunique()
by_prod = d.groupby("product").agg(revenue=("revenue", "sum"), qty=("quantity", "sum")).reset_index()
top_product = by_prod.sort_values("revenue", ascending=False).iloc[0]["product"]

c1, c2, c3, c4 = st.columns(4)
with c1: kpi("Total Revenue", f"{CURRENCY} {rev:,.2f}", "#1976d2")
with c2: kpi("Total Orders", f"{orders:,}", "#f57c00")
with c3: kpi("Average Order Value", f"{CURRENCY} {rev / orders:,.2f}", "#7b1fa2")
with c4: kpi("Top Selling Product", top_product, "#2e7d32")
st.write("")

# ---------------- Charts ----------------
freq = {"Daily": "D", "Weekly": "W", "Monthly": "MS"}[gran]
trend = d.set_index("date")["revenue"].resample(freq).sum().reset_index()
fig1 = px.line(trend, x="date", y="revenue", markers=True, title=f"Sales Trend ({gran})",
               labels={"date": "Date", "revenue": f"Sales ({CURRENCY})"})
fig1.update_traces(line_color="#1976d2")
fig1.update_layout(height=380, template="plotly_white")
st.plotly_chart(fig1)

left, right = st.columns(2)
with left:
    n = min(5, max(1, len(by_prod) // 2))
    ranked = by_prod.sort_values("qty", ascending=False)
    bar_df = pd.concat([ranked.head(n).assign(Group="Best Sellers"),
                        ranked.tail(n).assign(Group="Worst Sellers")]).drop_duplicates("product")
    fig2 = px.bar(bar_df.sort_values("qty"), x="qty", y="product", orientation="h", color="Group", text="qty",
                  color_discrete_map={"Best Sellers": "#2e7d32", "Worst Sellers": "#c62828"},
                  title="Best vs Worst Selling Products (units sold)", labels={"qty": "Units Sold", "product": ""})
    fig2.update_layout(height=420, template="plotly_white")
    st.plotly_chart(fig2)
with right:
    ch = d.groupby("channel")["revenue"].sum().reset_index()
    fig3 = px.pie(ch, names="channel", values="revenue", hole=0.4, title="Sales Share by Channel")
    fig3.update_traces(textinfo="percent+label")
    fig3.update_layout(height=420)
    st.plotly_chart(fig3)
