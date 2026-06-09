import streamlit as st
from utils import inject_css, init_session, logo

st.set_page_config(
    page_title="Sign In — AgriMatch",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="collapsed",
)

logo()
inject_css()
init_session()

st.markdown("<br>", unsafe_allow_html=True)
_, mid, _ = st.columns([1, 2, 1])

with mid:
    st.markdown("""
    <div class="form-card">
        <div class="form-title" style="text-align: center;"> 🔑 Sign in</div>
        <div class="form-sub" style="text-align: center;">Access your AgriMatch account</div>
    </div>""", unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Buyer", "Farmer / Seller"])

    with tab1:
        with st.form("signin_buyer"):
            email = st.text_input(
                "Email address", placeholder="you@example.com")
            password = st.text_input("Password", type="password")
            st.caption(
                "Demo: any email + any password works. Try admin@agrimatch.gh")
            submitted = st.form_submit_button("Continue", type="primary",
                                              use_container_width=True)
            if submitted:
                if email and password:
                    st.session_state.logged_in = True
                    st.session_state.user_name = email.split("@")[0].title()
                    st.success("Signed in successfully!")
                    st.switch_page("pages/8_My_Dashboard.py")
                else:
                    st.warning("Please enter your email and password.")

    with tab2:
        with st.form("signin_farmer"):
            phone = st.text_input("Phone number", placeholder="+233 …")
            password2 = st.text_input("Password", type="password", key="fp")
            submitted2 = st.form_submit_button("Continue", type="primary",
                                               use_container_width=True)
            if submitted2:
                if phone and password2:
                    st.session_state.logged_in = True
                    st.session_state.user_name = "Farmer"
                    st.success("Signed in as farmer!")
                    st.switch_page("pages/8_My_Dashboard.py")
                else:
                    st.warning("Please fill in all fields.")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        '<div style="text-align:center;font-size:0.85rem;color:#6b7280;">New to AgriMatch?</div>',
        unsafe_allow_html=True)
    if st.button("Create your AgriMatch account →", use_container_width=True):
        st.switch_page("pages/10_Register.py")
