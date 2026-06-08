"""Shared data, CSS, and helpers for every AgriMatch page."""
import streamlit as st

# ── Data ──────────────────────────────────────────────────────────────────────
CROPS = ['Cassava',
         'Cowpeas',
         'Cowpeas (white)',
         'Eggplants',
         'Maize',
         'Maize (yellow)',
         'Millet',
         'Onions',
         'Peppers (dried)',
         'Peppers (fresh)',
         'Rice (local)',
         'Rice (paddy)',
         'Sorghum',
         'Soybeans',
         'Tomatoes (local)',
         'Tomatoes (navrongo)',
         'Yam',
         'Yam (puna)']
# CROPS = ["Maize", "Tomato", "Cassava", "Yam", "Plantain", "Rice",
#          "Onion", "Pepper", "Cocoa", "Groundnut", "Soybean", "Cowpea"]
REGIONS = ["Greater Accra", "Ashanti", "Eastern", "Western", "Central", "Volta",
           "Northern", "Upper East", "Upper West", "Brong-Ahafo"]
DISTRICTS = ["Accra Metro", "Kumasi Metro", "Tamale Metro", "Tema Metro",
             "Cape Coast", "Bolgatanga", "Wa", "Sunyani", "Koforidua", "Ho", "Sekondi-Takoradi"]

LISTINGS = [
    {"id": 1,  "crop": "Maize",     "farmer": "Kofi Mensah",      "region": "Ashanti",     "district": "Kumasi",    "price": 420,  "unit": "bag (100kg)", "qty": 50,  "tags": [
        "verified", "ai"],       "desc": "Freshly harvested white maize, dried and graded. Ready for immediate collection.", "days": 3,  "organic": False},
    {"id": 2,  "crop": "Tomato",    "farmer": "Abena Owusu",       "region": "Brong-Ahafo", "district": "Techiman",  "price": 180,  "unit": "crate",       "qty": 120,
        "tags": ["urgent", "verified"],    "desc": "Perishable tomatoes — collect within 7 days. Premium grade, minimal blemishes.",    "days": 7,  "organic": False},
    {"id": 3,  "crop": "Cassava",   "farmer": "Kweku Asante",      "region": "Eastern",     "district": "Koforidua", "price": 260,  "unit": "bag (80kg)",  "qty": 80,  "tags": [
        "verified", "organic"],   "desc": "Organic cassava from regenerative farm. Can supply 80 bags weekly.",               "days": 5,  "organic": True},
    {"id": 4,  "crop": "Yam",       "farmer": "Ama Boateng",       "region": "Volta",       "district": "Ho",        "price": 550,  "unit": "bag (60kg)",  "qty": 30,  "tags": [
        "limited", "verified"],   "desc": "Premium puna yam from Volta region. Limited quantity — first come, first served.",  "days": 4,  "organic": False},
    {"id": 5,  "crop": "Onion",     "farmer": "Ibrahim Alhassan",  "region": "Upper East",  "district": "Bolgatanga", "price": 310,  "unit": "bag (50kg)",  "qty": 200, "tags": [
        "verified", "ai"],        "desc": "Dry onions, well-cured and bagged. AI price forecast included.",                   "days": 14, "organic": False},
    {"id": 6,  "crop": "Plantain",  "farmer": "Efua Nkrumah",      "region": "Western",     "district": "Sekondi",   "price": 140,  "unit": "bunch",       "qty": 500,
        "tags": ["verified"],              "desc": "Ripe and semi-ripe plantain. Bulk orders welcome. Own transport preferred.",        "days": 3,  "organic": False},
    {"id": 7,  "crop": "Rice",      "farmer": "Yakubu Seidu",      "region": "Northern",    "district": "Tamale",    "price": 380,  "unit": "bag (50kg)",  "qty": 100, "tags": [
        "verified", "ai"],        "desc": "Local parboiled rice, machine processed. Quality certified. AI forecast included.", "days": 10, "organic": False},
    {"id": 8,  "crop": "Pepper",    "farmer": "Adjoa Sarpong",     "region": "Central",     "district": "Cape Coast", "price": 220,  "unit": "crate",       "qty": 60,
        "tags": ["organic", "verified"],   "desc": "Fresh chili pepper from organic certified farm. 60 crates available.",             "days": 5,  "organic": True},
    {"id": 9,  "crop": "Cocoa",     "farmer": "Kwame Darko",       "region": "Western",     "district": "Juaboso",   "price": 1800, "unit": "bag (64kg)",  "qty": 25,  "tags": [
        "verified"],              "desc": "Grade-A fermented and dried cocoa beans. Suitable for export.",                   "days": 20, "organic": False},
    {"id": 10, "crop": "Groundnut", "farmer": "Fatima Issah",      "region": "Upper West",  "district": "Wa",        "price": 290,  "unit": "bag (50kg)",  "qty": 70,  "tags": [
        "verified", "organic"],   "desc": "Shelled groundnuts, organic certified. Popular for oil production.",               "days": 12, "organic": True},
    {"id": 11, "crop": "Soybean",   "farmer": "Cynthia Addo",      "region": "Brong-Ahafo", "district": "Sunyani",   "price": 340,
        "unit": "bag (50kg)",  "qty": 45,  "tags": ["verified", "ai"],        "desc": "High-protein soybean, drought-resistant variety. Good for animal feed.",           "days": 8,  "organic": False},
    {"id": 12, "crop": "Cowpea",    "farmer": "Baba Musah",        "region": "Savannah",    "district": "Damongo",   "price": 260,  "unit": "bag (50kg)",  "qty": 90,  "tags": [
        "verified"],              "desc": "Brown-eyed cowpea. Washed and dried. Transport arrangement possible.",             "days": 6,  "organic": False},
]

MARKET_PRICES = [
    {"crop": "Maize",      "market": "Kumasi Central",      "price": 4.20,
        "change":  0.15, "unit": "kg", "region": "Ashanti"},
    {"crop": "Tomato",     "market": "Accra Agbogbloshie",  "price": 3.50,
        "change": -0.30, "unit": "kg", "region": "Greater Accra"},
    {"crop": "Cassava",    "market": "Koforidua Market",    "price": 2.80,
        "change":  0.05, "unit": "kg", "region": "Eastern"},
    {"crop": "Yam",        "market": "Techiman Market",     "price": 6.50,
        "change":  0.40, "unit": "kg", "region": "Brong-Ahafo"},
    {"crop": "Onion",      "market": "Bolgatanga Market",   "price": 5.10,
        "change": -0.10, "unit": "kg", "region": "Upper East"},
    {"crop": "Rice (local)", "market": "Tamale Market",      "price": 7.20,
     "change":  0.20, "unit": "kg", "region": "Northern"},
    {"crop": "Plantain",   "market": "Takoradi Market",     "price": 1.80,
        "change":  0.00, "unit": "kg", "region": "Western"},
    {"crop": "Pepper",     "market": "Cape Coast Market",   "price": 4.80,
        "change": -0.50, "unit": "kg", "region": "Central"},
    {"crop": "Groundnut",  "market": "Wa Market",           "price": 5.60,
        "change":  0.30, "unit": "kg", "region": "Upper West"},
    {"crop": "Cocoa",      "market": "COCOBOD",             "price": 28.50,
        "change":  1.50, "unit": "kg", "region": "National"},
    {"crop": "Soybean",    "market": "Sunyani Market",      "price": 6.20,
        "change":  0.10, "unit": "kg", "region": "Brong-Ahafo"},
    {"crop": "Cowpea",     "market": "Damongo Market",      "price": 5.00,
        "change": -0.20, "unit": "kg", "region": "Savannah"},
]

DEMAND_POSTS = [
    {"id": 1, "buyer": "Accra Fresh Ltd",        "crop": "Tomato",  "qty": "500 crates",    "region": "Greater Accra",    "budget": "GHS 170–185/crate",
        "posted": "2 hours ago",  "urgent": True,  "desc": "Urgently need 500 crates of fresh tomatoes. Delivery to our cold store in Accra. Will arrange transport."},
    {"id": 2, "buyer": "KAM Foods Ghana",         "crop": "Maize",   "qty": "2,000 bags",    "region": "Anywhere in Ghana", "budget": "GHS 400–430/bag",
        "posted": "5 hours ago",  "urgent": False, "desc": "We buy directly from farmers. Long-term contract possible for reliable suppliers."},
    {"id": 3, "buyer": "NutriCorp Ghana",         "crop": "Soybean", "qty": "300 bags",      "region": "Brong-Ahafo",      "budget": "GHS 330–350/bag",
        "posted": "1 day ago",    "urgent": False, "desc": "Looking for certified organic soybean for protein supplement production."},
    {"id": 4, "buyer": "Starfish Restaurant Group", "crop": "Pepper", "qty": "20 crates/week", "region": "Greater Accra",    "budget": "GHS 210–230/crate",
        "posted": "3 hours ago",  "urgent": True,  "desc": "Ongoing weekly order. Need consistent quality. Call for tasting arrangement."},
    {"id": 5, "buyer": "Export Direct Co.",       "crop": "Cocoa",   "qty": "500 bags",      "region": "Western",          "budget": "Market rate + 5%",
        "posted": "12 hours ago", "urgent": False, "desc": "Licensed cocoa buyer. Grade A only. Export quality required. Full payment within 48hrs."},
    {"id": 6, "buyer": "Village Foods Ltd",       "crop": "Cassava", "qty": "150 bags",      "region": "Eastern",          "budget": "GHS 250–270/bag",
        "posted": "2 days ago",   "urgent": False, "desc": "Processing factory in Koforidua. Weekly supply needed. Looking for group of farmers."},
]

BYPRODUCTS_URGENT = [
    {"id": 1, "name": "Fresh Maize Husks",   "source": "Maize",   "farm": "Asante Farms, Ashanti",
        "price": "GHS 40/bag",   "qty": "200 bags",  "days": 3, "use": "Animal feed, biogas"},
    {"id": 2, "name": "Tomato Pulp & Seeds", "source": "Tomato",  "farm": "Owusu Farm, Techiman",
        "price": "GHS 25/crate", "qty": "80 crates", "days": 2, "use": "Compost, livestock feed"},
    {"id": 3, "name": "Plantain Peels",      "source": "Plantain", "farm": "Nkrumah Estate, Western",
        "price": "GHS 15/bag",   "qty": "150 bags",  "days": 3, "use": "Animal feed, organic fertiliser"},
]

BYPRODUCTS_STABLE = [
    {"id": 4, "name": "Rice Bran",        "source": "Rice",      "farm": "Seidu Farm, Tamale",
        "price": "GHS 60/50kg", "qty": "100 bags", "use": "Animal feed, cooking oil"},
    {"id": 5, "name": "Cassava Skins",    "source": "Cassava",   "farm": "Asante Group, Eastern",
        "price": "GHS 30/bag",  "qty": "300 bags", "use": "Biogas, animal feed"},
    {"id": 6, "name": "Groundnut Shells", "source": "Groundnut", "farm": "Issah Farm, Upper West",
        "price": "GHS 45/bag",  "qty": "50 bags",  "use": "Biomass fuel, mulch"},
    {"id": 7, "name": "Cocoa Pod Husks",  "source": "Cocoa",     "farm": "Darko Farms, Western",
        "price": "GHS 55/bag",  "qty": "80 bags",  "use": "Potash fertiliser, biogas"},
    {"id": 8, "name": "Yam Peelings",     "source": "Yam",       "farm": "Boateng Farm, Volta",
        "price": "GHS 20/bag",  "qty": "60 bags",  "use": "Animal feed, biogas"},
]

# ── Shared CSS ────────────────────────────────────────────────────────────────
SHARED_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
#MainMenu, footer { visibility: hidden; }
.block-container { padding-top: 1rem !important; max-width: 1200px; }

.hero-section {
    background: linear-gradient(135deg, #052e16 0%, #14532d 60%, #166534 100%);
    color: white; padding: 72px 40px 64px; text-align: center;
}
.hero-badge {
    display: inline-block; background: rgba(255,255,255,0.15);
    border: 1px solid rgba(255,255,255,0.25); border-radius: 100px;
    padding: 5px 16px; font-size: 0.78rem; font-weight: 500;
    margin-bottom: 20px; color: #bbf7d0;
}
.hero-title { font-size: 3rem; font-weight: 800; line-height: 1.15; margin-bottom: 18px; color: #fff; }
.hero-sub { font-size: 1.05rem; color: #d1fae5; max-width: 540px; margin: 0 auto 30px; line-height: 1.6; }
.hero-trust { margin-top: 28px; font-size: 0.8rem; color: #86efac; }

.section-title { font-size: 1.5rem; font-weight: 700; color: #111827; margin-bottom: 6px; }
.section-sub { font-size: 0.9rem; color: #6b7280; margin-bottom: 20px; }
.section-divider { border: none; border-top: 1px solid #f3f4f6; margin: 32px 0; }

.page-header { background: #f0fdf4; border-bottom: 1px solid #e5e7eb; padding: 32px 40px 24px; margin-bottom: 28px; }
.page-header-title { font-size: 2rem; font-weight: 800; color: #111827; margin-bottom: 4px; }
.page-header-sub { font-size: 0.9rem; color: #6b7280; }

.listing-card { background: #fff; border: 1px solid #e5e7eb; border-radius: 14px; padding: 18px; margin-bottom: 14px; transition: box-shadow 0.2s; }
.listing-card:hover { box-shadow: 0 4px 20px rgba(0,0,0,0.09); }
.listing-crop { font-size: 1rem; font-weight: 700; color: #111827; }
.listing-farmer { font-size: 0.82rem; color: #6b7280; margin-bottom: 8px; }
.listing-price { font-size: 1.4rem; font-weight: 800; color: #15803d; }
.listing-price-sub { font-size: 0.75rem; color: #9ca3af; }
.listing-tag { display: inline-block; font-size: 0.7rem; font-weight: 600; padding: 2px 8px; border-radius: 100px; margin: 2px; }
.tag-verified { background: #f0fdf4; color: #16a34a; border: 1px solid #bbf7d0; }
.tag-organic  { background: #fefce8; color: #a16207; border: 1px solid #fde68a; }
.tag-urgent   { background: #fff1f2; color: #be123c; border: 1px solid #fecdd3; }
.tag-ai       { background: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe; }
.tag-limited  { background: #fdf4ff; color: #7e22ce; border: 1px solid #e9d5ff; }

.market-card { background: #fff; border: 1px solid #e5e7eb; border-radius: 12px; padding: 16px; margin-bottom: 10px; }
.price-up   { color: #16a34a; font-weight: 600; }
.price-down { color: #dc2626; font-weight: 600; }
.price-flat { color: #6b7280; font-weight: 600; }

.demand-card { background: #fff; border: 1px solid #e5e7eb; border-radius: 12px; padding: 18px; margin-bottom: 12px; }
.demand-qty  { font-size: 1.2rem; font-weight: 700; color: #111827; }
.demand-buyer { font-size: 0.82rem; color: #6b7280; }

.byproduct-card  { background: #fff; border: 1px solid #e5e7eb; border-radius: 12px; padding: 18px; margin-bottom: 12px; }
.byproduct-price { font-size: 1.2rem; font-weight: 700; color: #a16207; }
.urgent-badge {
    background: #fff1f2; color: #be123c; border: 1px solid #fecdd3;
    display: inline-block; padding: 2px 10px; border-radius: 100px;
    font-size: 0.72rem; font-weight: 700; margin-bottom: 6px;
}

.stat-card  { background: #f9fafb; border: 1px solid #f3f4f6; border-radius: 12px; padding: 20px; text-align: center; }
.stat-num   { font-size: 2rem; font-weight: 800; color: #15803d; }
.stat-label { font-size: 0.8rem; color: #6b7280; margin-top: 4px; }

.vehicle-card { border: 2px solid #e5e7eb; border-radius: 10px; padding: 14px; text-align: center; }
.vehicle-icon { font-size: 2rem; margin-bottom: 6px; }
.vehicle-name { font-size: 0.85rem; font-weight: 600; color: #111827; }
.vehicle-cap  { font-size: 0.72rem; color: #6b7280; }

.form-card  { background: #fff; border: 1px solid #e5e7eb; border-radius: 16px; padding: 32px; max-width: 480px; margin: 0 auto; box-shadow: 0 4px 24px rgba(0,0,0,0.08); }
.form-title { font-size: 1.5rem; font-weight: 700; color: #111827; margin-bottom: 6px; }
.form-sub   { font-size: 0.85rem; color: #6b7280; margin-bottom: 24px; }

.agri-footer { background: #052e16; color: #d1fae5; text-align: center; padding: 28px 20px; margin-top: 60px; font-size: 0.82rem; }
.agri-footer a { color: #86efac; text-decoration: none; }
</style>
"""


def inject_css():
    st.markdown(SHARED_CSS, unsafe_allow_html=True)


def init_session():
    if "cart" not in st.session_state:
        st.session_state.cart = []
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "user_name" not in st.session_state:
        st.session_state.user_name = ""


def footer():
    st.markdown("""
    <div class="agri-footer">
        <div style="font-size:1.1rem;font-weight:800;color:#fff;margin-bottom:4px;">🌾 AgriMatch</div>
        <div style="color:#86efac;margin-bottom:8px;">Ghana's Agricultural Intelligence Platform · Powered by AI price forecasting</div>
        <div style="margin-top:12px;color:#4ade80;">© 2026 AgriMatch Ghana. All rights reserved.</div>
    </div>""", unsafe_allow_html=True)
