import streamlit as st
import pandas as pd
import random
from datetime import datetime, timedelta
import plotly.express as px
from utils import inject_css, init_session, footer, CROPS, REGIONS, MARKET_PRICES

st.set_page_config(
    page_title="Market Prices — AgriMatch",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

inject_css()
init_session()

st.markdown("""
<div class="page-header">
    <div class="page-header-title" style="text-align: center;">📊 Market Prices</div>
    <div class="page-header-sub" style="text-align: center;">Live commodity prices across Ghana</div>
</div>""", unsafe_allow_html=True)

# ── Filters ───────────────────────────────────────────────────────────────────
c1, c2 = st.columns(2)
with c1:
    filter_crop = st.selectbox("Filter by Crop", ["All Crops"] + CROPS)
with c2:
    filter_region = st.selectbox("Filter by Region",
                                 ["All Regions"] + REGIONS + ["National"])

data = MARKET_PRICES.copy()
if filter_crop != "All Crops":
    data = [m for m in data if m["crop"].split(
        " ")[0] == filter_crop.split(" ")[0]]
if filter_region != "All Regions":
    data = [m for m in data if m["region"] == filter_region]

st.markdown("<br>", unsafe_allow_html=True)

# ── Price cards ───────────────────────────────────────────────────────────────
if data:
    for i in range(0, len(data), 3):
        cols = st.columns(3)
        for j in range(3):
            if i + j >= len(data):
                break
            m = data[i + j]
            chg = m["change"]
            chg_class = "price-up" if chg > 0 else (
                "price-down" if chg < 0 else "price-flat")
            chg_icon = "▲" if chg > 0 else ("▼" if chg < 0 else "—")
            with cols[j]:
                st.markdown(f"""
                <div class="market-card">
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <div>
                            <div style="font-weight:700;font-size:1rem;">{m['crop']}</div>
                            <div style="font-size:0.78rem;color:#6b7280;">📍 {m['market']}</div>
                        </div>
                        <div style="text-align:right;">
                            <div style="font-size:1.3rem;font-weight:800;color:#111827;">
                                GHS {m['price']:.2f}</div>
                            <div style="font-size:0.78rem;">per {m['unit']}</div>
                        </div>
                    </div>
                    <div style="margin-top:10px;font-size:0.82rem;" class="{chg_class}">
                        {chg_icon} GHS {abs(chg):.2f} from yesterday
                    </div>
                </div>""", unsafe_allow_html=True)
else:
    st.info("No price data found for that filter combination.")

# ── Trend chart ───────────────────────────────────────────────────────────────
st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
st.markdown('<div class="section-title" style="text-align: center;">📈 Price Trends (30-day)</div>',
            unsafe_allow_html=True)

selected_crop = st.selectbox("Select crop to view trend", CROPS[:8])
base_list = [m["price"]
             for m in MARKET_PRICES if m["crop"].startswith(selected_crop)]
base_p = base_list[0] if base_list else 5.0
days = [datetime.now() - timedelta(days=i) for i in range(30, -1, -1)]
prices = [round(base_p + random.uniform(-0.4, 0.4) * (i / 10) + i * 0.02, 2)
          for i in range(31)]
trend_df = pd.DataFrame({"Date": days, "Price (GHS/kg)": prices})
fig = px.line(trend_df, x="Date", y="Price (GHS/kg)",
              title=f"{selected_crop} — 30-day Price Trend",
              color_discrete_sequence=["#16a34a"])
fig.update_layout(plot_bgcolor="#fff", paper_bgcolor="#fff",
                  font_family="Inter", title_font_size=14,
                  margin=dict(l=10, r=10, t=40, b=10))
st.plotly_chart(fig, use_container_width=True)
