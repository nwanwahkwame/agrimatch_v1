import streamlit as st
from utils import inject_css, init_session, footer, CROPS, REGIONS

st.set_page_config(
    page_title="AgriMatch — Ghana's Agricultural Marketplace",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="collapsed",
)

inject_css()
init_session()

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-section">
    <div class="hero-badge">✨ Verified farmers · Real-time prices</div>
    <div class="hero-title">Ghana's<span style="color: #90EE90;"> Agricultural</span><br>Marketplace</div>
    <div class="hero-sub">Buy directly from smallholder farmers with price forecasts,
    climate risk scores, and cooperative logistics.</div>
    <div class="hero-trust">Serving Ghanaians across the country</div>
</div>
""", unsafe_allow_html=True)

st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

# ── Shop by Crop ──────────────────────────────────────────────────────────────
st.markdown('<div class="section-title" style="text-align:center;">🌽 Shop By Crop</div>',
            unsafe_allow_html=True)
crop_emojis = {
    "Maize": "", "Tomato": "🍅", "Cassava": "", "Yam": "",
    "Plantain": "🍌", "Rice": "🍚", "Onion": "🧅", "Pepper": "🌶️",
    "Cocoa": "🍫", "Groundnut": "🥜", "Soybean": "🫘", "Cowpea": "🫛",
}
cols = st.columns(5)
for i, crop in enumerate(CROPS):
    with cols[i % 5]:
        if st.button(f"{crop_emojis.get(crop, '')} {crop}",
                     key=f"crop_{crop}", use_container_width=True):
            st.switch_page("pages/2_All_Listings.py")

st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

# ── Browse by Region ──────────────────────────────────────────────────────────
st.markdown('<div class="section-title" style="text-align:center;">📍 Browse By Region</div>',
            unsafe_allow_html=True)
cols = st.columns(5)
for i, region in enumerate(REGIONS):
    with cols[i % 5]:
        if st.button(region, key=f"region_{region}", use_container_width=True):
            st.switch_page("pages/2_All_Listings.py")

st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

# ── Stats ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title" style="text-align:center;">Why Smart Buyers Choose AgriMatch</div>',
            unsafe_allow_html=True)
stats = [
    ("94%",    "AI forecast accuracy"),
    ("850+",   "Verified farmers"),
    ("32",     "Live Ghana markets"),
    ("< 4 hrs", "Average match time"),
    ("Free",   "Zero buyer fees, always"),
]
for col, (num, lbl) in zip(st.columns(5), stats):
    with col:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-num">{num}</div>
            <div class="stat-label">{lbl}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

# ── Circular Economy CTA ──────────────────────────────────────────────────────
st.markdown("""
<div style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:16px;
            padding:32px;text-align:center;margin-bottom:20px;">
    <div style="font-size:0.8rem;font-weight:600;color:#16a34a;
                text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;">
        Circular Economy</div>
    <div style="font-size:1.8rem;font-weight:800;color:#052e16;margin-bottom:10px;">
        ♻️ Waste to Wealth</div>
    <div style="font-size:0.95rem;color:#374151;max-width:500px;margin:0 auto;">
        Maize husks, cassava skins, rice bran and more — buy agricultural byproducts
        directly from farms at below-market prices.
    </div>
</div>
""", unsafe_allow_html=True)

_, mid, _ = st.columns([2, 1, 2])
with mid:
    if st.button("Browse Byproducts →", use_container_width=True, type="primary"):
        st.switch_page("pages/5_Byproducts.py")

footer()
