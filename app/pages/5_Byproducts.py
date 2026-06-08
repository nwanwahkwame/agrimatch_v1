import streamlit as st
from utils import (inject_css, init_session, footer,
                   BYPRODUCTS_URGENT, BYPRODUCTS_STABLE)

st.set_page_config(
    page_title="Byproducts — AgriMatch",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

inject_css()
init_session()

st.markdown("""
<div class="page-header">
    <div class="page-header-title" style="text-align: center;">♻️ Waste to Wealth</div>
    <div class="page-header-sub" style="text-align: center;">Agricultural byproducts from Ghana's smallholder farms.
    Turn husks, stalks, and skins into additional income streams.</div>
</div>""", unsafe_allow_html=True)

# ── Urgent ────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title" style="color:#dc2626;">⚡ Urgent — Perishable Items</div>',
            unsafe_allow_html=True)
st.markdown('<div class="section-sub">These items need collection soon to avoid spoilage</div>',
            unsafe_allow_html=True)

cols = st.columns(3)
for i, b in enumerate(BYPRODUCTS_URGENT):
    with cols[i % 3]:
        st.markdown(f"""
        <div class="byproduct-card">
            <span class="urgent-badge">⚡ Urgent — {b['days']} days left</span>
            <div style="font-weight:700;font-size:1rem;">{b['name']}</div>
            <div style="font-size:0.8rem;color:#6b7280;margin-bottom:8px;">From: {b['farm']}</div>
            <div class="byproduct-price">{b['price']}</div>
            <div style="font-size:0.78rem;color:#9ca3af;">{b['qty']} available</div>
            <div style="margin-top:8px;font-size:0.78rem;color:#374151;">
                💡 <strong>Common uses:</strong> {b['use']}
            </div>
        </div>""", unsafe_allow_html=True)
        if st.button("📬 Enquire", key=f"bp_u_{b['id']}", use_container_width=True):
            st.success(f"Enquiry sent for {b['name']}!")

st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

# ── Stable ────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title" style="text-align: center;">📦 Stable Byproducts</div>',
            unsafe_allow_html=True)
st.markdown('<div class="section-sub" style="text-align: center;">Non-perishable agricultural materials available for collection</div>',
            unsafe_allow_html=True)

cols = st.columns(3)
for i, b in enumerate(BYPRODUCTS_STABLE):
    with cols[i % 3]:
        st.markdown(f"""
        <div class="byproduct-card">
            <div style="font-size:0.72rem;font-weight:600;color:#a16207;
                        text-transform:uppercase;margin-bottom:4px;">{b['source']}</div>
            <div style="font-weight:700;font-size:1rem;">{b['name']}</div>
            <div style="font-size:0.8rem;color:#6b7280;margin-bottom:8px;">From: {b['farm']}</div>
            <div class="byproduct-price">{b['price']}</div>
            <div style="font-size:0.78rem;color:#9ca3af;">{b['qty']} available</div>
            <div style="margin-top:8px;font-size:0.78rem;color:#374151;">
                💡 <strong>Common uses:</strong> {b['use']}
            </div>
        </div>""", unsafe_allow_html=True)
        if st.button("📬 Enquire", key=f"bp_s_{b['id']}", use_container_width=True):
            st.success(f"Enquiry sent for {b['name']}!")
