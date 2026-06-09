import streamlit as st
from utils import inject_css, init_session, logo, REGIONS, DISTRICTS

st.set_page_config(
    page_title="Transport Provider — AgriMatch",
    page_icon="🚛",
    layout="wide",
    initial_sidebar_state="collapsed",
)

logo()
inject_css()
init_session()

st.markdown("""
<div class="page-header">
    <div class="page-header-title" style="text-align: center;">🚛 Register as a Transport Provider</div>
    <div class="page-header-sub" style="text-align: center;">Join the AgriMatch logistics network and earn by moving farm produce</div>
</div>""", unsafe_allow_html=True)

VEHICLE_OPTIONS = [
    ("🛻", "Pickup Truck",  "500–1,500 kg"),
    ("🚐", "Mini Van",      "800–2,000 kg"),
    ("🚚", "Medium Truck",  "2,000–8,000 kg"),
    ("🚛", "Large Truck",   "8,000–30,000 kg"),
]

with st.form("transport_form"):
    st.markdown("#### 👤 Personal Information")
    c1, c2 = st.columns(2)
    with c1:
        full_name = st.text_input("Full name *")
        phone = st.text_input("Phone number *", placeholder="+233 …")
    with c2:
        business = st.text_input("Business name (optional)")
        email = st.text_input("Email (optional)")

    st.markdown("#### 🚛 Vehicle Information")

    # Vehicle type visual cards
    vc1, vc2, vc3, vc4 = st.columns(4)
    for col, (icon, name, cap) in zip([vc1, vc2, vc3, vc4], VEHICLE_OPTIONS):
        with col:
            st.markdown(f"""
            <div class="vehicle-card">
                <div class="vehicle-icon">{icon}</div>
                <div class="vehicle-name">{name}</div>
                <div class="vehicle-cap">{cap}</div>
            </div>""", unsafe_allow_html=True)

    vehicle_type = st.radio("Select your vehicle type",
                            [v[1] for v in VEHICLE_OPTIONS],
                            horizontal=True, label_visibility="collapsed")

    c1, c2, c3 = st.columns(3)
    with c1:
        capacity = st.number_input(
            "Capacity (kg) *", min_value=100, max_value=50000, value=1000)
    with c2:
        num_trucks = st.number_input(
            "No. of trucks", min_value=1, max_value=100, value=1)
    with c3:
        rate_per_km = st.number_input("Rate / km (GHS) optional", min_value=0.0,
                                      value=0.0, step=0.5)

    st.markdown("#### 📍 Location & Coverage")
    c1, c2 = st.columns(2)
    with c1:
        base_district = st.selectbox(
            "Base district *", ["Select district…"] + DISTRICTS)
    with c2:
        service_regions = st.multiselect("Service regions (select all you cover)",
                                         REGIONS, default=["Greater Accra"])

    st.markdown(
        '<div style="font-size:0.82rem;color:#6b7280;margin-top:8px;">'
        'Your details will be used to match you with cooperative logistics jobs across Ghana.'
        '</div>', unsafe_allow_html=True)

    submitted = st.form_submit_button("🚛 Register as Transport Provider",
                                      type="primary", use_container_width=True)
    if submitted:
        if full_name and phone and base_district != "Select district…" and service_regions:
            regions_str = ", ".join(service_regions[:2])
            suffix = "..." if len(service_regions) > 2 else ""
            st.success(
                f"✅ Thank you, {full_name}! You're registered as a transport provider "
                f"on AgriMatch. We'll match you with jobs in {regions_str}{suffix}.")
        else:
            st.warning("Please fill in all required fields.")
