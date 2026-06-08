import streamlit as st
from utils import inject_css, init_session, footer, CROPS, REGIONS, LISTINGS

st.set_page_config(
    page_title="All Listings — AgriMatch",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="collapsed",
)

inject_css()
init_session()

st.markdown("""
<div class="page-header">
    <div class="page-header-title" style="text-align: center;">🛒 All Listings</div>
    <div class="page-header-sub" style="text-align: center;">Fresh produce from verified Ghana farmers</div>
</div>""", unsafe_allow_html=True)

# ── Filters ───────────────────────────────────────────────────────────────────
c1, c2, c3 = st.columns([2, 2, 2])
with c1:
    filter_crop = st.selectbox("Crop", ["All Crops"] + CROPS)
with c2:
    filter_region = st.selectbox("Region", ["All Regions"] + REGIONS)
with c3:
    sort_by = st.selectbox("Sort by",
                           ["Newest", "Price: Low→High", "Price: High→Low", "Quantity"])

search = st.text_input("🔍 Search by crop, farmer or region…",
                       placeholder="e.g. maize, Kumasi, Kofi")

st.markdown("<br>", unsafe_allow_html=True)

# ── Filter & sort ─────────────────────────────────────────────────────────────
data = LISTINGS.copy()
if filter_crop != "All Crops":
    data = [l for l in data if l["crop"] == filter_crop]
if filter_region != "All Regions":
    data = [l for l in data if l["region"] == filter_region]
if search:
    q = search.lower()
    data = [l for l in data
            if q in l["crop"].lower() or q in l["farmer"].lower() or q in l["region"].lower()]
if sort_by == "Price: Low→High":
    data.sort(key=lambda x: x["price"])
elif sort_by == "Price: High→Low":
    data.sort(key=lambda x: x["price"], reverse=True)
elif sort_by == "Quantity":
    data.sort(key=lambda x: x["qty"], reverse=True)

if not data:
    st.info("No listings match your filters. Try adjusting your search.")
    st.stop()

st.markdown(
    f'<div style="font-size:0.85rem;color:#6b7280;margin-bottom:16px;">'
    f'{len(data)} listings found</div>',
    unsafe_allow_html=True)

# ── Grid ──────────────────────────────────────────────────────────────────────
TAG_CSS = {"verified": "tag-verified", "organic": "tag-organic",
           "urgent": "tag-urgent",     "ai": "tag-ai", "limited": "tag-limited"}
TAG_LABEL = {"verified": "✓ Verified",  "organic": "🌿 Organic",
             "urgent": "⚡ Urgent",      "ai": "🤖 AI Forecast", "limited": "📦 Limited"}

for i in range(0, len(data), 3):
    cols = st.columns(3)
    for j, col in enumerate(cols):
        if i + j >= len(data):
            break
        l = data[i + j]
        with col:
            tag_html = "".join(
                f'<span class="listing-tag {TAG_CSS.get(t, "")}">{TAG_LABEL.get(t, t)}</span>'
                for t in l["tags"]
            )
            st.markdown(f"""
            <div class="listing-card">
                <div class="listing-crop">{l['crop']}</div>
                <div class="listing-farmer">👤 {l['farmer']} · 📍 {l['region']}</div>
                <div class="listing-price">GHS {l['price']:,}</div>
                <div class="listing-price-sub">per {l['unit']} · {l['qty']} available</div>
                <div style="margin:10px 0 8px;">{tag_html}</div>
                <div style="font-size:0.8rem;color:#6b7280;line-height:1.5;">{l['desc']}</div>
                <div style="margin-top:10px;font-size:0.75rem;color:#9ca3af;">
                    ⏱ Collect within {l['days']} days</div>
            </div>""", unsafe_allow_html=True)

            if st.button("📬 Enquire", key=f"enq_{l['id']}_{i}", use_container_width=True):
                if l not in st.session_state.cart:
                    st.session_state.cart.append(l)
                st.success(f"Enquiry sent for {l['crop']} from {l['farmer']}!")
