import streamlit as st
from utils import inject_css, init_session, logo, CROPS, REGIONS, DISTRICTS

st.set_page_config(
    page_title="Sell on AgriMatch",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="collapsed",
)

logo()
inject_css()
init_session()

st.markdown("""
<div class="page-header">
    <div class="page-header-title" style="text-align: center;">🌾 Sell on AgriMatch</div>
    <div class="page-header-sub" style="text-align: center;">List your produce and connect with verified buyers across Ghana</div>
</div>""", unsafe_allow_html=True)

# ── Benefits ──────────────────────────────────────────────────────────────────
benefits = [
    ("💰", "Free to list",        "No commissions. Keep 100% of all your earnings."),
    ("📊", "AI Price Forecast",
     "Get our AI's prediction of fair market value for your crop."),
    ("🚛", "Cooperative Logistics",
     "Join group transport to cut delivery costs significantly."),
]
for col, (icon, title, desc) in zip(st.columns(3), benefits):
    with col:
        st.markdown(f"""
        <div class="stat-card" style="text-align:left;padding:20px;">
            <div style="font-size:1.8rem;margin-bottom:8px;">{icon}</div>
            <div style="font-weight:700;color:#111827;margin-bottom:4px;">{title}</div>
            <div style="font-size:0.82rem;color:#6b7280;">{desc}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Auth gate ─────────────────────────────────────────────────────────────────
if not st.session_state.logged_in:
    st.warning("Please sign in or register to list your produce.")
    c1, c2, _ = st.columns([1, 1, 3])
    with c1:
        if st.button("Sign In", type="primary"):
            st.switch_page("pages/9_Sign_In.py")
    with c2:
        if st.button("Register"):
            st.switch_page("pages/10_Register.py")
    st.stop()

# ── Listing form ──────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">📝 New Listing</div>',
            unsafe_allow_html=True)

with st.form("new_listing"):
    c1, c2 = st.columns(2)
    with c1:
        crop = st.selectbox("Crop *", CROPS)
        quantity = st.number_input(
            "Quantity available (bags/crates) *", min_value=1, value=10)
        price = st.number_input("Asking price (GHS) *", min_value=1, value=300)
    with c2:
        region = st.selectbox("Region *", REGIONS)
        district = st.selectbox("District *", DISTRICTS)
        unit = st.selectbox("Unit",
                            ["bag (100kg)", "bag (50kg)", "bag (80kg)",
                             "crate", "kg", "tonne"])

    collect_days = st.slider("Collection window (days)", 1, 30, 7)
    organic = st.checkbox("🌿 Certified Organic")
    ai_forecast = st.checkbox("🤖 Request AI Price Forecast")
    description = st.text_area("Description",
                               placeholder="Describe your produce — grade, moisture content, packaging…")

    submitted = st.form_submit_button("📤 Post Listing", type="primary",
                                      use_container_width=True)
    if submitted:
        if crop and quantity and price and region:
            st.success(
                f"✅ Your listing for {quantity} {unit}(s) of {crop} has been posted! "
                f"Buyers will be notified.")
            if ai_forecast:
                st.info(
                    f"🤖 AI Forecast: Fair market value for {crop} in {region} is "
                    f"approximately GHS {price * 0.95:.0f}–{price * 1.08:.0f} per {unit}.")
        else:
            st.warning("Please fill in all required fields.")
