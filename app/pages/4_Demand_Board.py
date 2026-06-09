import streamlit as st
from utils import inject_css, init_session, logo, CROPS, REGIONS, DEMAND_POSTS

st.set_page_config(
    page_title="Demand Board — AgriMatch",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="collapsed",
)

logo()
inject_css()
init_session()

st.markdown("""
<div class="page-header">
    <div class="page-header-title" style="text-align: center;">📋 Buyer Demand Board</div>
    <div class="page-header-sub" style="text-align: center;">See what buyers are looking for — or post your own request</div>
</div>""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📋 View Requests", "➕ Post a Request"])

# ── View Requests ─────────────────────────────────────────────────────────────
with tab1:
    c1, c2 = st.columns(2)
    with c1:
        filter_crop = st.selectbox("All crops", ["All crops"] + CROPS)
    with c2:
        filter_region = st.selectbox("All regions", ["All regions"] + REGIONS)

    data = DEMAND_POSTS.copy()
    if filter_crop != "All crops":
        data = [d for d in data if d["crop"] == filter_crop]
    if filter_region != "All regions":
        data = [d for d in data if filter_region.lower() in d["region"].lower()]

    st.markdown("<br>", unsafe_allow_html=True)

    for d in data:
        urgent_html = '<span class="urgent-badge">⚡ URGENT</span>' if d["urgent"] else ""
        st.markdown(f"""
        <div class="demand-card">
            {urgent_html}
            <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                <div>
                    <div class="demand-qty">{d['qty']} of {d['crop']}</div>
                    <div class="demand-buyer">👤 {d['buyer']} · 📍 {d['region']}</div>
                </div>
                <div style="text-align:right;">
                    <div style="font-weight:700;color:#16a34a;">{d['budget']}</div>
                    <div style="font-size:0.75rem;color:#9ca3af;">Posted {d['posted']}</div>
                </div>
            </div>
            <div style="margin-top:10px;font-size:0.82rem;color:#374151;">{d['desc']}</div>
        </div>""", unsafe_allow_html=True)
        if st.button("📩 Respond to Request", key=f"respond_{d['id']}"):
            st.success(f"Your response has been sent to {d['buyer']}!")

# ── Post a Request ────────────────────────────────────────────────────────────
with tab2:
    st.markdown('<div class="form-sub">Fill in the details below to post your procurement request</div>',
                unsafe_allow_html=True)
    with st.form("post_demand"):
        col1, col2 = st.columns(2)
        with col1:
            req_crop = st.selectbox("Crop needed *", CROPS)
            req_qty = st.text_input(
                "Quantity needed *", placeholder="e.g. 500 bags")
        with col2:
            req_region = st.selectbox(
                "Preferred region", ["Anywhere in Ghana"] + REGIONS)
            req_budget = st.text_input(
                "Budget range (GHS)", placeholder="e.g. 400–430/bag")
        req_desc = st.text_area("Description",
                                placeholder="Add any quality requirements, delivery preferences…")
        req_urgent = st.checkbox("Mark as Urgent")
        submitted = st.form_submit_button("Post Request", type="primary",
                                          use_container_width=True)
        if submitted:
            if req_crop and req_qty:
                st.success(
                    f"✅ Your request for {req_qty} of {req_crop} has been posted!")
            else:
                st.warning("Please fill in the required fields.")
