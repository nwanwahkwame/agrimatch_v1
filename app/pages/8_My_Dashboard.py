import streamlit as st
from utils import inject_css, init_session, logo

st.set_page_config(
    page_title="My Dashboard — AgriMatch",
    page_icon="👤",
    layout="wide",
    initial_sidebar_state="collapsed",
)

logo()
inject_css()
init_session()

if not st.session_state.logged_in:
    st.warning("Please sign in to view your dashboard.")
    if st.button("Sign In", type="primary"):
        st.switch_page("pages/9_Sign_In.py")
    st.stop()

st.markdown(f"""
<div class="page-header">
    <div class="page-header-title">👤 My Dashboard</div>
    <div class="page-header-sub">Welcome back, {st.session_state.user_name}</div>
</div>""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["📊 Overview", "📬 Enquiries", "📝 My Listings"])

with tab1:
    metrics = [("3", "Active Listings"), ("7", "Enquiries Received"),
               ("2", "Deals Closed"),    ("GHS 1,240", "Earnings This Month")]
    for col, (val, lbl) in zip(st.columns(4), metrics):
        with col:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-num" style="font-size:1.6rem;">{val}</div>
                <div class="stat-label">{lbl}</div>
            </div>""", unsafe_allow_html=True)

with tab2:
    st.markdown("#### Recent Enquiries")
    if st.session_state.cart:
        for item in st.session_state.cart:
            st.markdown(f"""
            <div class="demand-card">
                <div style="font-weight:700;">{item['crop']}</div>
                <div style="font-size:0.82rem;color:#6b7280;">
                    From {item['farmer']} · {item['region']}</div>
                <div style="color:#16a34a;font-weight:600;margin-top:4px;">
                    GHS {item['price']:,} per {item['unit']}</div>
            </div>""", unsafe_allow_html=True)
    else:
        st.info("No enquiries yet. Browse listings and click 'Enquire' to get started.")

with tab3:
    st.info("You have no active listings. Go to 'Sell on AgriMatch' to create one.")
    if st.button("Create a Listing →", type="primary"):
        st.switch_page("pages/6_Sell_on_AgriMatch.py")
