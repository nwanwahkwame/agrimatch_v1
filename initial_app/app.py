"""
AgriMarket — Full Streamlit Web Application
Implements every screen from the flowchart:
  Auth → Role → Farmer (Post Produce / Manage Waste) → Buyer (Buy Produce / Buy Waste) → Admin Log
Run: streamlit run agrimarket_app.py
"""

import streamlit as st
import random
import datetime
import time

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AgriMarket",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;600;700;800&family=DM+Sans:wght@300;400;500;600&display=swap');

:root {
  --green:       #2d8c4e;
  --green-light: #e6f4eb;
  --green-mid:   #4caf72;
  --blue:        #1e5fa8;
  --blue-light:  #e3eef9;
  --blue-mid:    #3b82c4;
  --amber:       #e08c1a;
  --amber-light: #fff5e0;
  --red:         #d94040;
  --red-light:   #fdeaea;
  --purple:      #6b3fa0;
  --purple-light:#f0eaff;
  --salmon:      #e05252;
  --gray:        #f4f6f9;
  --card-shadow: 0 2px 16px rgba(0,0,0,0.09);
  --radius:      14px;
}

html, body, [class*="css"] {
  font-family: 'DM Sans', sans-serif;
  background: #f0f4f0 !important;
}

h1,h2,h3,h4 { font-family: 'Sora', sans-serif; }

/* hide streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0.5rem 1.5rem 3rem !important; max-width: 900px !important; margin: 0 auto; }

/* ── card ── */
.agri-card {
  background: #fff;
  border-radius: var(--radius);
  padding: 24px 28px;
  box-shadow: var(--card-shadow);
  margin-bottom: 18px;
}

/* ── top banner ── */
.top-banner {
  background: linear-gradient(135deg, #1e6e2e 0%, #2d8c4e 50%, #1e5fa8 100%);
  border-radius: 0 0 24px 24px;
  padding: 18px 32px 20px;
  color: #fff;
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 24px;
  box-shadow: 0 4px 24px rgba(30,110,46,0.25);
}
.top-banner .logo { font-size: 2.2rem; }
.top-banner .title { font-family:'Sora',sans-serif; font-size:1.6rem; font-weight:800; letter-spacing:-0.5px; }
.top-banner .sub   { font-size:0.82rem; opacity:0.82; margin-top:2px; }

/* ── step indicator ── */
.step-bar {
  display: flex; align-items: center; gap: 0;
  background: #fff; border-radius: 40px;
  padding: 6px 18px; box-shadow: var(--card-shadow);
  margin-bottom: 22px; overflow-x: auto;
}
.step { display:flex; align-items:center; gap:6px; }
.step-dot {
  width:28px; height:28px; border-radius:50%;
  display:flex; align-items:center; justify-content:center;
  font-size:0.72rem; font-weight:700;
}
.step-dot.done  { background:var(--green);   color:#fff; }
.step-dot.active{ background:var(--blue);    color:#fff; box-shadow:0 0 0 3px rgba(30,95,168,0.2); }
.step-dot.todo  { background:#e5e9f0;        color:#8a94a6; }
.step-label { font-size:0.75rem; font-weight:600; color:#4a5568; white-space:nowrap; }
.step-line  { width:24px; height:2px; background:#e5e9f0; margin:0 2px; }

/* ── role cards ── */
.role-row { display:flex; gap:20px; margin-top:12px; }
.role-card {
  flex:1; border-radius:16px; padding:28px 20px;
  text-align:center; cursor:pointer;
  border:3px solid transparent;
  transition:all .2s;
  box-shadow: var(--card-shadow);
}
.role-card:hover { transform:translateY(-3px); box-shadow:0 8px 28px rgba(0,0,0,0.13); }
.role-card.farmer { background:var(--green-light); border-color:var(--green-mid); }
.role-card.buyer  { background:var(--blue-light);  border-color:var(--blue-mid); }
.role-card .emoji { font-size:3rem; display:block; margin-bottom:10px; }
.role-card h3     { font-family:'Sora',sans-serif; font-size:1.1rem; font-weight:800; margin-bottom:4px; }
.role-card p      { font-size:0.8rem; color:#5a6a7a; }

/* ── option cards (Post Produce etc) ── */
.opt-row { display:flex; gap:16px; margin-top:8px; }
.opt-card {
  flex:1; border-radius:14px; padding:22px 18px;
  cursor:pointer; border:2px solid transparent;
  transition:all .2s; box-shadow:var(--card-shadow);
}
.opt-card:hover { transform:translateY(-2px); box-shadow:0 6px 22px rgba(0,0,0,0.12); }
.opt-card.green { background:var(--green-light); border-color:var(--green-mid); }
.opt-card.blue  { background:var(--blue-light);  border-color:var(--blue-mid); }
.opt-card h4    { font-family:'Sora',sans-serif; font-size:1rem; font-weight:700; margin:8px 0 4px; }
.opt-card p     { font-size:0.78rem; color:#4a5568; }

/* ── listing card ── */
.listing-card {
  background:#fff; border-radius:12px; padding:16px 18px;
  border-left:4px solid var(--green); box-shadow:var(--card-shadow);
  margin-bottom:12px;
}
.listing-card.blue { border-left-color:var(--blue); }
.listing-card h5   { font-family:'Sora',sans-serif; font-size:0.95rem; font-weight:700; margin-bottom:4px; }
.listing-card .meta{ font-size:0.78rem; color:#6b7a8d; }
.price-tag {
  display:inline-block; background:var(--green); color:#fff;
  border-radius:20px; padding:2px 12px; font-size:0.78rem; font-weight:700;
}
.price-tag.free { background:var(--amber); }
.price-tag.blue { background:var(--blue); }

/* ── status badge ── */
.badge {
  display:inline-block; border-radius:20px; padding:3px 12px;
  font-size:0.72rem; font-weight:700; margin-right:6px;
}
.badge.green  { background:var(--green-light); color:var(--green); }
.badge.blue   { background:var(--blue-light);  color:var(--blue); }
.badge.amber  { background:var(--amber-light); color:var(--amber); }
.badge.red    { background:var(--red-light);   color:var(--red); }
.badge.purple { background:var(--purple-light);color:var(--purple); }

/* ── big action button ── */
.big-btn {
  display:block; width:100%; padding:15px;
  border-radius:12px; text-align:center;
  font-family:'Sora',sans-serif; font-size:1rem; font-weight:700;
  cursor:pointer; border:none; margin-top:12px;
  transition:all .18s; letter-spacing:0.2px;
}
.big-btn.green  { background:var(--green); color:#fff; }
.big-btn.blue   { background:var(--blue);  color:#fff; }
.big-btn.amber  { background:var(--amber); color:#fff; }
.big-btn.outline-green { background:#fff; color:var(--green); border:2px solid var(--green); }
.big-btn:hover  { opacity:0.88; transform:translateY(-1px); }

/* ── SMS notification box ── */
.sms-box {
  background: linear-gradient(135deg,#6b3fa0,#1e5fa8);
  color:#fff; border-radius:16px; padding:22px 24px;
  box-shadow:0 4px 20px rgba(107,63,160,0.3);
  margin:16px 0;
}
.sms-box h4 { font-family:'Sora',sans-serif; font-size:1.1rem; font-weight:800; margin-bottom:6px; }

/* ── admin table ── */
.admin-row {
  display:flex; align-items:center; gap:12px;
  padding:12px 16px; background:#fff; border-radius:10px;
  margin-bottom:8px; box-shadow:0 1px 8px rgba(0,0,0,0.06);
  font-size:0.82rem;
}
.admin-row .timestamp { color:#8a94a6; font-size:0.72rem; width:120px; flex-shrink:0; }

/* OTP boxes */
.otp-hint {
  background:var(--amber-light); border:1.5px solid var(--amber);
  border-radius:10px; padding:12px 16px; font-size:0.82rem;
  color:#7a4f00; margin-bottom:16px;
}

/* back link */
.back-link { font-size:0.82rem; color:var(--blue); cursor:pointer; margin-bottom:8px; display:inline-block; }
</style>
""", unsafe_allow_html=True)

# ── Session state defaults ────────────────────────────────────────────────────


def ss(key, default):
    if key not in st.session_state:
        st.session_state[key] = default


ss("screen", "welcome")          # current screen
ss("role", None)                  # "farmer" | "buyer"
ss("phone", "")
ss("otp_sent", False)
ss("otp_code", "")
ss("authenticated", False)
ss("farmer_option", None)         # "post_produce" | "manage_waste"
ss("buyer_option", None)          # "buy_produce" | "buy_waste"
ss("waste_intent", None)          # "learn" | "sell"
ss("harvested", None)             # True | False
ss("submitted_listing", None)
ss("matched_listing", None)
ss("admin_log", [])               # list of log dicts
ss("produce_db", [
    {"id": "P001", "crop": "Maize", "region": "Ashanti", "price": 280,
        "unit": "bag", "status": "Harvested", "farmer": "0244123456", "photo": "🌽"},
    {"id": "P002", "crop": "Tomato", "region": "Greater Accra", "price": 0,
        "unit": "crate", "status": "Harvested", "farmer": "0201987654", "photo": "🍅"},
    {"id": "P003", "crop": "Cassava", "region": "Eastern", "price": 150,
        "unit": "bag", "status": "2 weeks", "farmer": "0277456123", "photo": "🥔"},
    {"id": "P004", "crop": "Pepper", "region": "Volta", "price": 90,
        "unit": "bag", "status": "Harvested", "farmer": "0261334455", "photo": "🌶️"},
    {"id": "P005", "crop": "Ginger", "region": "Brong-Ahafo", "price": 340,
        "unit": "box", "status": "Harvested", "farmer": "0233678900", "photo": "🫚"},
])
ss("waste_db", [
    {"id": "W001", "type": "Maize Stalks/Cobs", "region": "Ashanti", "weight": "40 bags",
        "condition": "Dry", "price": 0, "farmer": "0244123456", "photo": "🌿"},
    {"id": "W002", "type": "Cassava Peels/Stems", "region": "Eastern", "weight": "2 tons",
        "condition": "Fresh", "price": 120, "farmer": "0277456123", "photo": "♻️"},
    {"id": "W003", "type": "Pineapple Crowns", "region": "Greater Accra", "weight": "500 kg",
        "condition": "Fresh", "price": 0, "farmer": "0201555111", "photo": "🍍"},
    {"id": "W004", "type": "Animal Manure", "region": "Northern", "weight": "1 ton",
        "condition": "Dry", "price": 200, "farmer": "0209876543", "photo": "🌱"},
])

# ── Helper: banner ────────────────────────────────────────────────────────────


def banner(subtitle="Ghana's Agricultural Marketplace"):
    role_pill = ""
    if st.session_state.role:
        icon = "🧑‍🌾" if st.session_state.role == "farmer" else "🛒"
        role_pill = f'<span style="background:rgba(255,255,255,0.2);border-radius:20px;padding:2px 12px;font-size:0.78rem;margin-left:10px;">{icon} {st.session_state.role.title()}</span>'
    st.markdown(f"""
    <div class="top-banner">
      <div class="logo">🌾</div>
      <div>
        <div class="title">AgriMarket {role_pill}</div>
        <div class="sub">{subtitle}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)


# ── Helper: step bar ──────────────────────────────────────────────────────────
STEPS = ["Welcome", "Auth", "Dashboard", "Action", "Confirm"]
SCREEN_STEP = {
    "welcome": 0, "select_role": 0,
    "phone": 1, "otp": 1,
    "farmer_dashboard": 2, "buyer_dashboard": 2,
    "post_produce": 3, "manage_waste": 3, "buy_produce": 3, "buy_waste": 3,
    "waste_learn": 3, "waste_sell": 3, "sub_route": 3,
    "confirm": 4, "sms_sent": 4, "admin": 4,
}


def step_bar():
    cur = SCREEN_STEP.get(st.session_state.screen, 0)
    html = '<div class="step-bar">'
    for i, label in enumerate(STEPS):
        if i < cur:
            dot = '<div class="step-dot done">✓</div>'
        elif i == cur:
            dot = f'<div class="step-dot active">{i+1}</div>'
        else:
            dot = f'<div class="step-dot todo">{i+1}</div>'
        html += f'<div class="step"><span>{dot}</span><span class="step-label">{label}</span></div>'
        if i < len(STEPS)-1:
            html += '<div class="step-line"></div>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


def go(screen):
    st.session_state.screen = screen
    st.rerun()


def log_event(action, detail, actor=None):
    st.session_state.admin_log.append({
        "time": datetime.datetime.now().strftime("%H:%M:%S"),
        "date": datetime.datetime.now().strftime("%d %b %Y"),
        "actor": actor or st.session_state.phone or "System",
        "action": action,
        "detail": detail,
        "status": "✅ Done",
    })

# ══════════════════════════════════════════════════════════════════════════════
# SCREENS
# ══════════════════════════════════════════════════════════════════════════════

# ── 1. Welcome ────────────────────────────────────────────────────────────────

# #4d4d4d
# #5a6a7a


def screen_welcome():
    banner("Ghana's Agricultural Marketplace")
    st.markdown("""
    <div class="agri-card" style="text-align:center;padding:40px 28px;">
      <div style="font-size:3.5rem;margin-bottom:12px;">🌾</div>
      <h2 style="font-family:Sora,sans-serif;font-size:1.8rem;font-weight:800;margin-bottom:8px;">
        Welcome to AgriMarket
      </h2>
      <p style="color:#5a6a7a;max-width:480px;margin:0 auto 24px;line-height:1.7;">
        Connect farmers directly with buyers. Trade fresh produce and agricultural 
        waste across Ghana — fast, simple, and built for the field.
      </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀  Get Started", use_container_width=True, type="primary"):
            go("select_role")
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("📊  Admin Dashboard", use_container_width=True):
            go("admin")

# ── 2. Select Role ────────────────────────────────────────────────────────────


def screen_select_role():
    banner()
    step_bar()
    st.markdown("### Select Your Role")
    st.markdown("Are you selling produce, or looking to buy?")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="role-card farmer">
          <span class="emoji">🧑‍🌾</span>
          <h3>Farmer</h3>
          <p>Post produce for sale or manage your agricultural waste</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("I'm a Farmer →", use_container_width=True, key="btn_farmer"):
            st.session_state.role = "farmer"
            go("phone")

    with col2:
        st.markdown("""
        <div class="role-card buyer">
          <span class="emoji">🛒</span>
          <h3>Buyer</h3>
          <p>Browse listings, order produce, or source agricultural waste</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("I'm a Buyer →", use_container_width=True, key="btn_buyer"):
            st.session_state.role = "buyer"
            go("phone")

# ── 3. Phone Entry ────────────────────────────────────────────────────────────


def screen_phone():
    banner()
    step_bar()
    st.markdown("### Enter Your Phone Number")

    col, _ = st.columns([1.4, 1])
    with col:
        with st.container():
            st.markdown('<div class="agri-card">', unsafe_allow_html=True)
            st.markdown("📞 **Phone Number** *(strictly 10 digits)*")
            phone = st.text_input("", placeholder="e.g. 0244123456", max_chars=10,
                                  label_visibility="collapsed", key="phone_input")

            send = st.button("Send OTP Code →",
                             use_container_width=True, type="primary")
            st.markdown('</div>', unsafe_allow_html=True)

        if send:
            if len(phone) == 10 and phone.isdigit():
                st.session_state.phone = phone
                code = str(random.randint(1000, 9999))
                st.session_state.otp_code = code
                st.session_state.otp_sent = True
                log_event("OTP Sent", f"Code {code} → {phone}")
                go("otp")
            else:
                st.error("Please enter exactly 10 digits.")

        if st.button("← Back"):
            go("select_role")

# ── 4. OTP Verify ─────────────────────────────────────────────────────────────


def screen_otp():
    banner()
    step_bar()
    st.markdown("### Verify via OTP / PIN")

    col, _ = st.columns([1.4, 1])
    with col:
        st.markdown(f"""
        <div class="otp-hint">
          📱 Demo mode — your OTP is: <strong style="font-size:1.1rem;letter-spacing:4px;">
          {st.session_state.otp_code}</strong><br>
          <span style="font-size:0.75rem;">(In production this is sent via SMS)</span>
        </div>
        """, unsafe_allow_html=True)

        with st.container():
            st.markdown('<div class="agri-card">', unsafe_allow_html=True)
            otp = st.text_input("Enter 4-digit OTP", placeholder="••••", max_chars=4,
                                type="password", key="otp_input")
            verify = st.button("🔐  Verify & Continue",
                               use_container_width=True, type="primary")
            st.markdown('</div>', unsafe_allow_html=True)

        if verify:
            if otp == st.session_state.otp_code:
                st.session_state.authenticated = True
                log_event(
                    "Authenticated", f"{st.session_state.role.title()} login", st.session_state.phone)
                dest = "farmer_dashboard" if st.session_state.role == "farmer" else "buyer_dashboard"
                go(dest)
            else:
                st.error("Incorrect OTP. Please try again.")

        if st.button("← Back"):
            go("phone")

# ── 5. Farmer Dashboard ───────────────────────────────────────────────────────


def screen_farmer_dashboard():
    banner(f"Farmer Dashboard — {st.session_state.phone}")
    step_bar()
    st.markdown("### 🌿 Farmer Dashboard")
    st.markdown("Choose an action from the marketplace below.")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="opt-card green">
          <div style="font-size:2rem;">🌽</div>
          <h4>Post Produce</h4>
          <p>List your fresh crops for sale — maize, tomato, cassava, pepper and more.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Post Produce →", use_container_width=True, key="fp"):
            go("post_produce")

    with col2:
        st.markdown("""
        <div class="opt-card green">
          <div style="font-size:2rem;">♻️</div>
          <h4>Manage Waste</h4>
          <p>Learn what to do with your agricultural waste, or sell it to interested buyers.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Manage Waste →", use_container_width=True, key="fw"):
            go("manage_waste")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚪 Logout", key="logout_f"):
        for k in ["role", "phone", "authenticated", "otp_sent", "otp_code", "farmer_option", "waste_intent", "harvested", "submitted_listing"]:
            st.session_state[k] = None if k not in ["otp_sent", "authenticated",
                                                    "otp_code"] else False if k in ["otp_sent", "authenticated"] else ""
        go("welcome")

# ── 6. Post Produce ───────────────────────────────────────────────────────────


def screen_post_produce():
    banner("Post Produce Listing")
    step_bar()

    if st.button("← Farmer Dashboard"):
        go("farmer_dashboard")

    st.markdown("### 🌽 Post Produce")

    with st.form("post_produce_form"):
        st.markdown("#### Crop Details")
        col1, col2 = st.columns(2)
        with col1:
            crop = st.selectbox("Select Crop Type", [
                                "Maize", "Pepper", "Onion", "Tomato", "Cassava", "Sorghum", "Pineapple", "Ginger"])
            region = st.selectbox("Region / District", ["Ashanti", "Greater Accra", "Eastern", "Western", "Volta", "Northern", "Upper East",
                                  "Upper West", "Brong-Ahafo", "Oti", "Savannah", "Bono East", "Ahafo", "Central", "North East", "Western North"])
        with col2:
            harvested = st.radio("Is it Harvested?", [
                                 "✅ Yes — Ready", "⏳ No — Not yet"])
            weeks_left = None
            if "No" in harvested:
                weeks_left = st.slider("Weeks until harvest", 1, 16, 4)

        price = st.number_input(
            "Price (GHS) — enter 0 for FREE pickup", min_value=0, value=150, step=10)
        unit = st.selectbox("Unit", ["bag", "crate", "kg", "box", "ton"])
        quantity = st.number_input("Quantity available", min_value=1, value=10)
        notes = st.text_area("Additional notes (optional)",
                             placeholder="e.g. Organic, no pesticides, bulk discount available...")

        submit = st.form_submit_button(
            "📤  Submit Listing", use_container_width=True, type="primary")

    if submit:
        listing = {
            "id": f"P{random.randint(100, 999)}",
            "crop": crop, "region": region,
            "price": price, "unit": unit,
            "quantity": quantity,
            "status": "Harvested" if "Yes" in harvested else f"{weeks_left} wks",
            "farmer": st.session_state.phone,
            "photo": {"Maize": "🌽", "Pepper": "🌶️", "Onion": "🧅", "Tomato": "🍅", "Cassava": "🥔", "Sorghum": "🌾", "Pineapple": "🍍", "Ginger": "🫚"}.get(crop, "🌿"),
            "notes": notes,
        }
        st.session_state.produce_db.append(listing)
        st.session_state.submitted_listing = listing
        log_event("Produce Listed",
                  f"{crop} from {region} — GHS {price}/{unit}", st.session_state.phone)
        go("confirm")

# ── 7. Manage Waste ───────────────────────────────────────────────────────────


def screen_manage_waste():
    banner("Manage Agricultural Waste")
    step_bar()

    if st.button("← Farmer Dashboard"):
        go("farmer_dashboard")

    st.markdown("### ♻️ Manage Waste")
    st.markdown("What would you like to do with your agricultural waste?")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="opt-card green" style="border-color:#1e6e2e;">
          <div style="font-size:2rem;">📖</div>
          <h4>Learn</h4>
          <p>Access guides and audio content on how to handle, repurpose, or dispose of waste responsibly.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Learn About Waste →", use_container_width=True, key="wl"):
            st.session_state.waste_intent = "learn"
            go("waste_learn")

    with col2:
        st.markdown("""
        <div class="opt-card green" style="border-color:#1e6e2e;">
          <div style="font-size:2rem;">💰</div>
          <h4>Sell Waste</h4>
          <p>List your agricultural waste for buyers looking to purchase or collect for free.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Sell My Waste →", use_container_width=True, key="ws"):
            st.session_state.waste_intent = "sell"
            go("waste_sell")


# ── 7a. Waste Learn ───────────────────────────────────────────────────────────
WASTE_GUIDES = {
    "Maize Stalks/Cobs":    ("🌽", "Use stalks as mulch or animal feed. Dry cobs make excellent biomass fuel or can be composted. Avoid burning — this releases harmful gases.", "https://example.com"),
    "Cassava Peels/Stems":  ("🥔", "Cassava peels can be processed into animal feed after detoxification. Stems are best used as planting material for next season.", "https://example.com"),
    "Rotten Bulk Produce":  ("🍅", "Composting is the best option. Mix with dry matter in a 1:3 ratio. Ready in 6–8 weeks. Excellent soil amendment.", "https://example.com"),
    "Pineapple Crowns":     ("🍍", "Pineapple crowns can be replanted directly. They're also rich in fiber and can be dried for animal feed supplement.", "https://example.com"),
    "Sorghum Straw":        ("🌾", "Excellent animal fodder, especially for cattle. Can also be used for thatching or as biomass energy source.", "https://example.com"),
    "Animal Manure":        ("🐄", "Apply directly to fields after composting (3–4 weeks). Excellent nitrogen source. Can also be converted to biogas for cooking.", "https://example.com"),
}


def screen_waste_learn():
    banner("Waste Management Guides")
    step_bar()

    if st.button("← Manage Waste"):
        go("manage_waste")

    st.markdown("### 📖 Waste Learning Guides")
    st.markdown(
        "Select your waste type to get advice, audio guides, and composting tips.")

    waste_type = st.selectbox("Select Waste Type", list(WASTE_GUIDES.keys()))

    if waste_type:
        icon, guide, _ = WASTE_GUIDES[waste_type]
        st.markdown(f"""
        <div class="agri-card" style="border-left:5px solid var(--green);padding:22px 24px;">
          <div style="font-size:2.5rem;margin-bottom:10px;">{icon}</div>
          <h4 style="font-family:Sora,sans-serif;margin-bottom:8px;">{waste_type}</h4>
          <p style="line-height:1.8;color:#2d3748;">{guide}</p>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🎧 Play Audio Guide", use_container_width=True):
                st.info("🎧 Audio guide playing... (demo)")
        with col2:
            if st.button("📄 Download PDF", use_container_width=True):
                st.info("📄 PDF guide downloaded (demo)")
        with col3:
            if st.button("🔗 Full Resource", use_container_width=True):
                st.info("🔗 Opening full resource... (demo)")

        log_event("Guide Accessed",
                  f"{waste_type} guide viewed", st.session_state.phone)

# ── 7b. Waste Sell ────────────────────────────────────────────────────────────


def screen_waste_sell():
    banner("Sell Agricultural Waste")
    step_bar()

    if st.button("← Manage Waste"):
        go("manage_waste")

    st.markdown("### ♻️ Sell Your Waste")

    with st.form("waste_sell_form"):
        col1, col2 = st.columns(2)
        with col1:
            waste_type = st.selectbox("Select Waste Type", [
                                      "Maize Stalks/Cobs", "Cassava Peels/Stems", "Rotten Bulk Produce", "Pineapple Crowns", "Sorghum Straw", "Animal Manure"])
            region = st.selectbox("Region", ["Ashanti", "Greater Accra", "Eastern",
                                  "Western", "Volta", "Northern", "Upper East", "Upper West", "Brong-Ahafo"])
        with col2:
            weight_val = st.number_input(
                "Weight / Quantity", min_value=1, value=50)
            weight_unit = st.selectbox("Unit", ["kg", "bags", "tons"])
            condition = st.radio("Condition", ["Fresh", "Dry"])

        price = st.number_input(
            "Price (GHS) — 0 for FREE pickup", min_value=0, value=0)
        location_note = st.text_input(
            "Pickup Location Details", placeholder="e.g. Ejisu-Juaben, near the Cocoa Board")

        st.markdown("#### 📸 Upload Photo")
        photo = st.file_uploader("Upload a photo of your waste (optional)", type=[
                                 "jpg", "jpeg", "png"])

        submit = st.form_submit_button(
            "📤  List Waste for Sale", use_container_width=True, type="primary")

    if submit:
        listing = {
            "id": f"W{random.randint(100, 999)}",
            "type": waste_type,
            "region": region,
            "weight": f"{weight_val} {weight_unit}",
            "condition": condition,
            "price": price,
            "farmer": st.session_state.phone,
            "photo": {"Maize Stalks/Cobs": "🌿", "Cassava Peels/Stems": "🥔", "Rotten Bulk Produce": "🍅", "Pineapple Crowns": "🍍", "Sorghum Straw": "🌾", "Animal Manure": "🌱"}.get(waste_type, "♻️"),
            "location": location_note,
        }
        st.session_state.waste_db.append(listing)
        st.session_state.submitted_listing = listing
        log_event(
            "Waste Listed", f"{waste_type} — {weight_val} {weight_unit} from {region}", st.session_state.phone)
        go("confirm")

# ── 8. Buyer Dashboard ────────────────────────────────────────────────────────


def screen_buyer_dashboard():
    banner(f"Buyer Dashboard — {st.session_state.phone}")
    step_bar()
    st.markdown("### 🛒 Buyer Dashboard")
    st.markdown("What are you looking to source today?")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="opt-card blue">
          <div style="font-size:2rem;">🌽</div>
          <h4>Buy Produce</h4>
          <p>Browse fresh crop listings from farmers across Ghana. Filter by crop type and region.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Browse Produce →", use_container_width=True, key="bbp"):
            go("buy_produce")

    with col2:
        st.markdown("""
        <div class="opt-card blue">
          <div style="font-size:2rem;">♻️</div>
          <h4>Buy Waste</h4>
          <p>Source agricultural by-products for your business — animal feed, compost, biomass and more.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Browse Waste →", use_container_width=True, key="bbw"):
            go("buy_waste")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚪 Logout", key="logout_b"):
        for k in ["role", "phone", "authenticated", "otp_sent", "otp_code", "buyer_option", "matched_listing"]:
            st.session_state[k] = None if k not in ["otp_sent", "authenticated",
                                                    "otp_code"] else False if k in ["otp_sent", "authenticated"] else ""
        go("welcome")

# ── 9. Buy Produce ────────────────────────────────────────────────────────────


def screen_buy_produce():
    banner("Browse Produce Listings")
    step_bar()

    if st.button("← Buyer Dashboard"):
        go("buyer_dashboard")

    st.markdown("### 🌽 Buy Produce")

    col1, col2, col3 = st.columns(3)
    with col1:
        crop_filter = st.selectbox("Filter by Crop", [
                                   "All"] + sorted(set(p["crop"] for p in st.session_state.produce_db)))
    with col2:
        region_filter = st.selectbox("Filter by Region", [
                                     "All"] + sorted(set(p["region"] for p in st.session_state.produce_db)))
    with col3:
        status_filter = st.selectbox(
            "Harvest Status", ["All", "Harvested", "Not yet"])

    listings = st.session_state.produce_db
    if crop_filter != "All":
        listings = [p for p in listings if p["crop"] == crop_filter]
    if region_filter != "All":
        listings = [p for p in listings if p["region"] == region_filter]
    if status_filter == "Harvested":
        listings = [p for p in listings if p["status"] == "Harvested"]
    elif status_filter == "Not yet":
        listings = [p for p in listings if p["status"] != "Harvested"]

    st.markdown(f"**{len(listings)} listing(s) found**")
    st.markdown("---")

    if not listings:
        st.info("No listings match your filters. Try adjusting them.")
        return

    for p in listings:
        price_html = f'<span class="price-tag blue">GHS {p["price"]}/{p["unit"]}</span>' if p[
            "price"] > 0 else '<span class="price-tag free">FREE Pickup</span>'
        status_col = "green" if p["status"] == "Harvested" else "amber"
        st.markdown(f"""
        <div class="listing-card blue">
          <h5>{p['photo']} {p['crop']} &nbsp; {price_html}</h5>
          <div class="meta">
            <span class="badge blue">{p['region']}</span>
            <span class="badge {status_col}">{p['status']}</span>
            &nbsp;Farmer: {p['farmer']}
          </div>
        </div>
        """, unsafe_allow_html=True)

        col_a, col_b = st.columns([3, 1])
        with col_b:
            if st.button(f"🤝 Order / Match", key=f"order_{p['id']}"):
                st.session_state.matched_listing = p
                log_event(
                    "Order Placed", f"{p['crop']} from {p['region']}", st.session_state.phone)
                go("sms_sent")

# ── 10. Buy Waste ─────────────────────────────────────────────────────────────


def screen_buy_waste():
    banner("Browse Waste Listings")
    step_bar()

    if st.button("← Buyer Dashboard"):
        go("buyer_dashboard")

    st.markdown("### ♻️ Buy Waste")

    col1, col2 = st.columns(2)
    with col1:
        type_filter = st.selectbox("Filter by Waste Type", [
                                   "All"] + sorted(set(w["type"] for w in st.session_state.waste_db)))
    with col2:
        region_filter = st.selectbox("Filter by Region", [
                                     "All"] + sorted(set(w["region"] for w in st.session_state.waste_db)))

    listings = st.session_state.waste_db
    if type_filter != "All":
        listings = [w for w in listings if w["type"] == type_filter]
    if region_filter != "All":
        listings = [w for w in listings if w["region"] == region_filter]

    st.markdown(f"**{len(listings)} listing(s) found**")
    st.markdown("---")

    if not listings:
        st.info("No waste listings match your filters.")
        return

    for w in listings:
        price_html = f'<span class="price-tag blue">GHS {w["price"]}</span>' if w[
            "price"] > 0 else '<span class="price-tag free">FREE Pickup</span>'
        cond_col = "green" if w["condition"] == "Fresh" else "amber"
        st.markdown(f"""
        <div class="listing-card">
          <h5>{w['photo']} {w['type']} &nbsp; {price_html}</h5>
          <div class="meta">
            <span class="badge green">{w['region']}</span>
            <span class="badge {cond_col}">{w['condition']}</span>
            <span class="badge blue">{w['weight']}</span>
            &nbsp;Farmer: {w['farmer']}
          </div>
        </div>
        """, unsafe_allow_html=True)

        col_a, col_b = st.columns([3, 1])
        with col_b:
            if st.button(f"🔒 Secure Waste", key=f"secure_{w['id']}"):
                st.session_state.matched_listing = w
                log_event(
                    "Waste Secured", f"{w['type']} from {w['region']}", st.session_state.phone)
                go("sms_sent")

# ── 11. Confirm (Farmer submission) ──────────────────────────────────────────


def screen_confirm():
    banner("Listing Submitted!")
    step_bar()

    listing = st.session_state.submitted_listing
    st.markdown("### ✅ Listing Submitted Successfully")

    if listing:
        is_waste = "type" in listing
        title = listing.get("type", listing.get("crop", ""))
        st.markdown(f"""
        <div class="agri-card" style="border-left:5px solid var(--green);">
          <div style="font-size:2rem;margin-bottom:8px;">{'♻️' if is_waste else '🌽'}</div>
          <h4 style="font-family:Sora,sans-serif;">{title}</h4>
          <p style="color:#4a5568;">
            Region: <strong>{listing.get('region', '')}</strong> &nbsp;|&nbsp;
            Listing ID: <strong>{listing.get('id', '')}</strong>
          </p>
          <p style="color:#4a5568;margin-top:4px;">
            {'Price: <strong>FREE Pickup</strong>' if listing.get('price', 0) == 0 else f"Price: <strong>GHS {listing.get('price', '')}</strong>"}
          </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class="sms-box">
      <h4>💬 SMS Notification Sent</h4>
      <p>The system has notified nearby buyers matching your listing. 
      You'll receive an SMS when a buyer places an order.</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("📋 View My Listings", use_container_width=True):
            go("farmer_dashboard")
    with col2:
        if st.button("➕ Post Another", use_container_width=True):
            go("farmer_dashboard")

# ── 12. SMS Sent (Buyer match) ────────────────────────────────────────────────


def screen_sms_sent():
    banner("Match Confirmed!")
    step_bar()

    listing = st.session_state.matched_listing
    st.markdown("### 🤝 Match Confirmed!")

    if listing:
        is_waste = "type" in listing
        title = listing.get("type", listing.get("crop", ""))
        farmer_phone = listing.get("farmer", "unknown")

        st.markdown(f"""
        <div class="agri-card" style="border-left:5px solid var(--blue);">
          <div style="font-size:2rem;margin-bottom:8px;">{'♻️' if is_waste else '🌽'}</div>
          <h4 style="font-family:Sora,sans-serif;">{title}</h4>
          <p style="color:#4a5568;">Region: <strong>{listing.get('region', '')}</strong></p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="sms-box">
          <h4>💬 Backend Triggered SMS</h4>
          <p style="margin-bottom:10px;">The system has connected you with the farmer.</p>
          <div style="background:rgba(255,255,255,0.15);border-radius:10px;padding:12px 16px;font-family:monospace;font-size:0.88rem;">
            📤 SMS to Buyer ({st.session_state.phone}):<br>
            <em>"Your order for {title} is confirmed. 
            Contact farmer at {farmer_phone}."</em><br><br>
            📤 SMS to Farmer ({farmer_phone}):<br>
            <em>"Buyer {st.session_state.phone} is interested in your {title} listing. 
            Expect contact soon."</em>
          </div>
        </div>
        """, unsafe_allow_html=True)

    log_event("SMS Triggered",
              f"Buyer {st.session_state.phone} ↔ Farmer {listing.get('farmer', '')}", "System")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🛒 Continue Browsing", use_container_width=True):
            go("buyer_dashboard")
    with col2:
        if st.button("📊 View Admin Log", use_container_width=True):
            go("admin")

# ── 13. Admin Dashboard ───────────────────────────────────────────────────────


def screen_admin():
    banner("Admin Dashboard — System Log")

    st.markdown("### 📊 Admin Dashboard Log")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Listings", len(
        st.session_state.produce_db) + len(st.session_state.waste_db))
    col2.metric("Produce Listings", len(st.session_state.produce_db))
    col3.metric("Waste Listings", len(st.session_state.waste_db))
    col4.metric("Events Logged", len(st.session_state.admin_log))

    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["📋 Event Log", "🌽 Produce DB", "♻️ Waste DB"])

    with tab1:
        st.markdown("#### Activity Log — Manual Verification Loop")
        if not st.session_state.admin_log:
            st.info("No events logged yet. Use the app to generate activity.")
        for entry in reversed(st.session_state.admin_log):
            status_color = "#2d8c4e"
            st.markdown(f"""
            <div class="admin-row">
              <span class="timestamp">🕐 {entry['date']}<br>{entry['time']}</span>
              <span class="badge green">{entry['action']}</span>
              <span style="flex:1;">{entry['detail']}</span>
              <span style="color:#8a94a6;font-size:0.75rem;">👤 {entry['actor']}</span>
              <span style="color:{status_color};font-weight:700;">{entry['status']}</span>
            </div>
            """, unsafe_allow_html=True)

    with tab2:
        st.markdown("#### Produce Listing Table")
        for p in st.session_state.produce_db:
            price_str = f"GHS {p['price']}/{p['unit']}" if p['price'] > 0 else "FREE Pickup"
            st.markdown(f"""
            <div class="admin-row">
              <span style="font-weight:700;width:60px;">{p['id']}</span>
              <span style="width:80px;">{p['photo']} {p['crop']}</span>
              <span class="badge green">{p['region']}</span>
              <span class="badge amber">{p['status']}</span>
              <span style="flex:1;">{price_str}</span>
              <span style="color:#8a94a6;font-size:0.75rem;">📞 {p['farmer']}</span>
            </div>
            """, unsafe_allow_html=True)

    with tab3:
        st.markdown("#### Waste Listing Table")
        for w in st.session_state.waste_db:
            price_str = f"GHS {w['price']}" if w['price'] > 0 else "FREE Pickup"
            st.markdown(f"""
            <div class="admin-row">
              <span style="font-weight:700;width:60px;">{w['id']}</span>
              <span style="width:120px;">{w['photo']} {w['type'][:18]}…</span>
              <span class="badge green">{w['region']}</span>
              <span class="badge blue">{w['weight']}</span>
              <span class="badge amber">{w['condition']}</span>
              <span style="flex:1;">{price_str}</span>
              <span style="color:#8a94a6;font-size:0.75rem;">📞 {w['farmer']}</span>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("← Back to Home"):
        go("welcome")


# ══════════════════════════════════════════════════════════════════════════════
# ROUTER
# ══════════════════════════════════════════════════════════════════════════════
SCREENS = {
    "welcome":           screen_welcome,
    "select_role":       screen_select_role,
    "phone":             screen_phone,
    "otp":               screen_otp,
    "farmer_dashboard":  screen_farmer_dashboard,
    "post_produce":      screen_post_produce,
    "manage_waste":      screen_manage_waste,
    "waste_learn":       screen_waste_learn,
    "waste_sell":        screen_waste_sell,
    "buyer_dashboard":   screen_buyer_dashboard,
    "buy_produce":       screen_buy_produce,
    "buy_waste":         screen_buy_waste,
    "confirm":           screen_confirm,
    "sms_sent":          screen_sms_sent,
    "admin":             screen_admin,
}

SCREENS.get(st.session_state.screen, screen_welcome)()
