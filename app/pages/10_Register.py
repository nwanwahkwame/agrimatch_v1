import streamlit as st
from utils import inject_css, init_session, footer, CROPS, REGIONS, DISTRICTS

st.set_page_config(
    page_title="Register — AgriMatch",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="collapsed",
)

inject_css()
init_session()

st.markdown("<br>", unsafe_allow_html=True)
_, mid, _ = st.columns([1, 2, 1])

with mid:
    st.markdown("""
    <div class="form-card">
        <div class="form-title" style="text-align: center;"> 📝 Create your account </div>
        <div class="form-sub" style="text-align: center;">Join Ghana's agricultural marketplace</div>
    </div>""", unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Buyer", "Farmer / Seller"])

    with tab1:
        with st.form("reg_buyer"):
            c1, c2 = st.columns(2)
            with c1:
                fname = st.text_input("First name *")
            with c2:
                lname = st.text_input("Last name *")
            reg_email = st.text_input("Email address *")
            reg_phone = st.text_input("Phone number *", placeholder="+233 …")
            reg_region = st.selectbox("Region *", REGIONS)
            reg_pw = st.text_input("Password *", type="password")
            agree = st.checkbox("I agree to the Terms and Privacy Policy")
            submitted = st.form_submit_button("Create Account", type="primary",
                                              use_container_width=True)
            if submitted:
                if fname and lname and reg_email and reg_phone and agree:
                    st.session_state.logged_in = True
                    st.session_state.user_name = fname
                    st.success(f"Welcome to AgriMatch, {fname}! 🎉")
                    st.switch_page("pages/8_My_Dashboard.py")
                elif not agree:
                    st.warning("Please agree to the Terms and Privacy Policy.")
                else:
                    st.warning("Please fill in all required fields.")

    with tab2:
        with st.form("reg_farmer"):
            c1, c2 = st.columns(2)
            with c1:
                fname2 = st.text_input("First name *", key="fn2")
            with c2:
                lname2 = st.text_input("Last name *",  key="ln2")
            f_phone = st.text_input(
                "Phone number *", placeholder="+233 …", key="fp2")
            f_region = st.selectbox("Region *", REGIONS, key="fr2")
            f_district = st.selectbox("District *", DISTRICTS, key="fd2")
            f_crops = st.multiselect("Crops you grow", CROPS)
            f_pw = st.text_input("Password *", type="password", key="fpw2")
            agree2 = st.checkbox(
                "I agree to the Terms and Privacy Policy", key="ag2")
            submitted2 = st.form_submit_button("Register as Farmer", type="primary",
                                               use_container_width=True)
            if submitted2:
                if fname2 and lname2 and f_phone and agree2:
                    st.session_state.logged_in = True
                    st.session_state.user_name = fname2
                    st.success(
                        f"Welcome, Farmer {fname2}! Your account is ready. 🌾")
                    st.switch_page("pages/8_My_Dashboard.py")
                else:
                    st.warning("Please fill in all required fields.")
