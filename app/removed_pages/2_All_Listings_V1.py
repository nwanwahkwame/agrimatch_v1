"""
All Listings — AgriMatch
─────────────────────────
Flow:
  1. Farmer records are loaded from MySQL (farm_backend.new_farmers).
  2. User can filter by crop, region, and free-text search.
  3. Farmer cards are rendered in a 3-column grid, 30 per page.
  4. Clicking "Enquire" on a card opens an inline expander showing:
       - Full farmer details
       - A Prophet price forecast for that crop + region
"""

import os
import pickle
import sys
from pathlib import Path

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine

# utils.py lives one level up (the project root)
sys.path.append(str(Path(__file__).resolve().parent.parent))
from utils import inject_css, init_session, logo, CROPS, REGIONS  # noqa: E402

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="All Listings — AgriMatch",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="collapsed",
)

logo()
inject_css()
init_session()

st.markdown("""
<div class="page-header">
    <div class="page-header-title" style="text-align: center;">🛒 All Listings</div>
    <div class="page-header-sub" style="text-align: center;">Browse registered farmers across Ghana</div>
</div>""", unsafe_allow_html=True)

# ── Environment / DB setup ────────────────────────────────────────────────────
load_dotenv()

HOST     = os.getenv("DB_HOST")
USERNAME = os.getenv("DB_USERNAME")
PASSWORD = os.getenv("DB_PASSWORD")
PORT     = os.getenv("DB_PORT")

LISTINGS_DB  = "farm_backend"
LISTINGS_TBL = "new_farmers"

# Forecast model directory (same convention as Price_Forecast.py)
MODEL_DIR = Path(__file__).resolve().parent.parent.parent / "models"

PAGE_SIZE = 30


# ── DB / model helpers ────────────────────────────────────────────────────────

@st.cache_resource
def get_listings_engine():
    return create_engine(
        f"mysql+pymysql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{LISTINGS_DB}"
    )


@st.cache_resource
def get_forecast_engine():
    """Separate engine for the price-history DB used by the forecast models."""
    forecast_db = os.getenv("DB_DATABASE")   # same var used in Price_Forecast.py
    return create_engine(
        f"mysql+pymysql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{forecast_db}"
    )


@st.cache_data(ttl=300)
def load_farmers() -> pd.DataFrame:
    query = f"SELECT * FROM `{LISTINGS_TBL}`"
    return pd.read_sql(query, get_listings_engine())


@st.cache_resource
def load_model(model_key: str):
    model_path = MODEL_DIR / f"{model_key}.pkl"
    if not model_path.exists():
        raise FileNotFoundError(f"No model found at {model_path}")
    with open(model_path, "rb") as f:
        return pickle.load(f)


@st.cache_data(ttl=300)
def load_price_history(table_name: str) -> pd.DataFrame:
    query = f"SELECT * FROM `{table_name}` ORDER BY date"
    return pd.read_sql(query, get_forecast_engine())


def forecast_from_prophet(model, last_date: pd.Timestamp, steps: int) -> pd.DataFrame:
    """Run the Prophet model forward by `steps` months past last_date."""
    future = model.make_future_dataframe(periods=steps, freq="MS")
    forecast = model.predict(future)
    result = forecast[forecast["ds"] > last_date][
        ["ds", "yhat", "yhat_lower", "yhat_upper"]
    ].reset_index(drop=True)
    result[["yhat", "yhat_lower", "yhat_upper"]] = (
        result[["yhat", "yhat_lower", "yhat_upper"]].round(2)
    )
    return result


def make_model_key(region: str, crop: str) -> str:
    """Build the model/table lookup key from a region and crop string."""
    return (
        f"{region.replace('-', '_').replace(' ', '_')}"
        f"_{crop.replace(' ', '')}"
    ).lower()


# ── Load farmer data ──────────────────────────────────────────────────────────
try:
    df_all = load_farmers()
except Exception as e:
    st.error(f"Could not load farmer listings: {e}")
    st.stop()

if df_all.empty:
    st.info("No farmer listings are available at the moment.")
    st.stop()

# ── Filters ───────────────────────────────────────────────────────────────────
# Build unique crop list — crops_planted may be comma-separated (e.g. "Maize, Yam")
all_crops = sorted({
    c.strip()
    for val in df_all["crops_planted"].dropna()
    for c in str(val).split(",")
    if c.strip()
}) or CROPS

all_regions = sorted(df_all["region"].dropna().unique().tolist()) or REGIONS

c1, c2, c3 = st.columns([2, 2, 2])
with c1:
    filter_crop = st.selectbox("Crop", ["All Crops"] + all_crops)
with c2:
    filter_region = st.selectbox("Region", ["All Regions"] + all_regions)
with c3:
    sort_by = st.selectbox(
        "Sort by",
        ["Default", "Harvest: Soonest", "Harvest: Latest", "Name A→Z"],
    )

search = st.text_input(
    "🔍 Search by name, crop, district or region…",
    placeholder="e.g. Kofi, Maize, Ashanti",
)

st.markdown("<br>", unsafe_allow_html=True)

# ── Apply filters ─────────────────────────────────────────────────────────────
data = df_all.copy()

if filter_crop != "All Crops":
    data = data[
        data["crops_planted"].str.contains(filter_crop, case=False, na=False)
    ]

if filter_region != "All Regions":
    data = data[data["region"] == filter_region]

if search:
    q = search.lower()
    mask = (
        data["name"].str.lower().str.contains(q, na=False)
        | data["crops_planted"].str.lower().str.contains(q, na=False)
        | data["district"].str.lower().str.contains(q, na=False)
        | data["region"].str.lower().str.contains(q, na=False)
    )
    data = data[mask]

# ── Apply sort ────────────────────────────────────────────────────────────────
if sort_by == "Harvest: Soonest":
    data = data.sort_values("harvest_date", ascending=True, na_position="last")
elif sort_by == "Harvest: Latest":
    data = data.sort_values("harvest_date", ascending=False, na_position="last")
elif sort_by == "Name A→Z":
    data = data.sort_values("name", ascending=True)

data = data.reset_index(drop=True)

if data.empty:
    st.info("No farmers match your filters. Try adjusting your search.")
    st.stop()

total       = len(data)
total_pages = max(1, -(-total // PAGE_SIZE))   # ceiling division

st.markdown(
    f'<div style="font-size:0.85rem;color:#6b7280;margin-bottom:16px;">'
    f'{total} farmer{"s" if total != 1 else ""} found</div>',
    unsafe_allow_html=True,
)

# ── Pagination state ──────────────────────────────────────────────────────────
if "listings_page" not in st.session_state:
    st.session_state.listings_page = 1

# Reset to page 1 when filters change
filter_key = (filter_crop, filter_region, sort_by, search)
if st.session_state.get("_last_filter_key") != filter_key:
    st.session_state.listings_page = 1
    st.session_state["_last_filter_key"] = filter_key


def page_slice(page: int) -> pd.DataFrame:
    start = (page - 1) * PAGE_SIZE
    return data.iloc[start: start + PAGE_SIZE]


def pagination_controls(key_suffix: str):
    if total_pages <= 1:
        return
    pg_cols = st.columns([1, 3, 1])
    with pg_cols[0]:
        if st.button("← Prev", key=f"prev_{key_suffix}",
                     disabled=st.session_state.listings_page <= 1):
            st.session_state.listings_page -= 1
            st.rerun()
    with pg_cols[1]:
        st.markdown(
            f'<div style="text-align:center;padding-top:6px;font-size:0.9rem;">'
            f'Page {st.session_state.listings_page} of {total_pages}</div>',
            unsafe_allow_html=True,
        )
    with pg_cols[2]:
        if st.button("Next →", key=f"next_{key_suffix}",
                     disabled=st.session_state.listings_page >= total_pages):
            st.session_state.listings_page += 1
            st.rerun()


pagination_controls("top")

page_data = page_slice(st.session_state.listings_page)

# ── Enquiry expander state ────────────────────────────────────────────────────
# Tracks which farmer row index (within `data`) is currently expanded.
if "enquiry_open" not in st.session_state:
    st.session_state.enquiry_open = None


# ── Grid ──────────────────────────────────────────────────────────────────────
for i in range(0, len(page_data), 3):
    cols = st.columns(3)
    for j, col in enumerate(cols):
        idx = i + j
        if idx >= len(page_data):
            break

        row   = page_data.iloc[idx]
        row_i = page_data.index[idx]   # index in the full filtered `data` df

        # Format harvest date
        try:
            harvest_display = pd.to_datetime(row["harvest_date"]).strftime("%d %b %Y")
        except Exception:
            harvest_display = str(row.get("harvest_date", "—"))

        # Crops — normalise to a tidy comma-separated string
        crops_raw    = str(row.get("crops_planted", "—"))
        yet_to_plant = str(row.get("yet_to_plant", ""))

        with col:
            st.markdown(f"""
            <div class="listing-card">
                <div class="listing-crop">{crops_raw}</div>

                <div class="listing-farmer" style="margin-bottom:6px;">
                    👤 <strong>{row.get('name', '—')}</strong>
                </div>

                <div style="font-size:0.82rem;color:#374151;line-height:1.8;">
                    📞 {row.get('telephone_no', '—')}<br>
                    📍 {row.get('location', '—')}, {row.get('district', '—')}<br>
                    🗺️ {row.get('region', '—')} Region
                </div>

                <div style="margin-top:10px;font-size:0.8rem;color:#6b7280;line-height:1.7;">
                    🌾 <strong>Planted:</strong> {crops_raw}<br>
                    🌱 <strong>Yet to plant:</strong> {yet_to_plant if yet_to_plant and yet_to_plant != 'nan' else '—'}<br>
                    📅 <strong>Harvest date:</strong> {harvest_display}
                </div>
            </div>""", unsafe_allow_html=True)

            if st.button(
                "📬 Enquire & View Forecast",
                key=f"enq_{row_i}",
                use_container_width=True,
            ):
                # Toggle: clicking again collapses the panel
                st.session_state.enquiry_open = (
                    None if st.session_state.enquiry_open == row_i else row_i
                )
                st.rerun()

    # ── Inline enquiry / forecast panel ──────────────────────────────────────
    # Rendered after each row of 3 so it appears directly below the clicked card.
    row_indices_in_this_row = [
        page_data.index[i + k]
        for k in range(3)
        if (i + k) < len(page_data)
    ]

    if st.session_state.enquiry_open in row_indices_in_this_row:
        sel     = data.loc[st.session_state.enquiry_open]
        crop    = sel.get("crops_planted", "")
        region  = sel.get("region", "")

        # If farmer grows multiple crops, take the first one for the forecast
        primary_crop = str(crop).split(",")[0].strip()

        with st.expander(
            f"📋 Enquiry Details — {sel.get('name', '')}  ·  "
            f"Crop: {primary_crop}  ·  Region: {region}",
            expanded=True,
        ):
            # ── Farmer detail summary ─────────────────────────────────────
            st.subheader("Farmer Details")
            d1, d2, d3 = st.columns(3)
            d1.markdown(f"**Name** \n{sel.get('name', '—')}")
            d2.markdown(f"**Phone** \n{sel.get('telephone_no', '—')}")
            d3.markdown(f"**Location** \n{sel.get('location', '—')}, {sel.get('district', '—')}")

            d4, d5, d6 = st.columns(3)
            d4.markdown(f"**Region** \n{region} Region")
            d5.markdown(f"**Crops Planted** \n{crop}")
            d6.markdown(f"**Yet to Plant** \n{sel.get('yet_to_plant', '—') or '—'}")

            try:
                hd = pd.to_datetime(sel["harvest_date"]).strftime("%d %B %Y")
            except Exception:
                hd = str(sel.get("harvest_date", "—"))
            st.markdown(f"**Expected Harvest Date:** {hd}")

            st.divider()

            # ── Price forecast ────────────────────────────────────────────
            st.subheader(f"📈 Price Forecast — {primary_crop} in {region}")

            model_key = make_model_key(region, primary_crop)

            forecast_months = st.slider(
                "Forecast Horizon (months)",
                min_value=1, max_value=48, value=12,
                key=f"slider_{st.session_state.enquiry_open}",
            )

            try:
                model    = load_model(model_key)
                hist_df  = load_price_history(model_key)
                hist_df["date"] = pd.to_datetime(hist_df["date"])
                price_col = "cedi_price/(KG)"

                # Historical metrics
                m1, m2, m3 = st.columns(3)
                m1.metric("Avg Historical Price (GHS/kg)",
                          f"{hist_df[price_col].mean():.2f}")
                m2.metric("Latest Price (GHS/kg)",
                          f"{hist_df[price_col].iloc[-1]:.2f}")
                m3.metric("Data Range",
                          f"{hist_df['year'].min()} – {hist_df['year'].max()}")

                if st.button(
                    "Generate Forecast",
                    type="primary",
                    key=f"forecast_btn_{st.session_state.enquiry_open}",
                ):
                    with st.spinner("Generating forecast…"):
                        last_date   = hist_df["date"].max()
                        forecast_df = forecast_from_prophet(
                            model, last_date, forecast_months
                        )

                    # Forecast chart
                    forecast_chart = (
                        forecast_df[["ds", "yhat", "yhat_lower", "yhat_upper"]]
                        .rename(columns={
                            "ds":         "ds",
                            "yhat":       "Forecast Price",
                            "yhat_lower": "Lower Bound",
                            "yhat_upper": "Upper Bound",
                        })
                        .set_index("ds")
                    )
                    st.line_chart(
                        forecast_chart,
                        x_label="Date",
                        y_label="Price (GHS/kg)",
                    )

                    # Summary metrics
                    peak_row   = forecast_df.loc[forecast_df["yhat"].idxmax()]
                    trough_row = forecast_df.loc[forecast_df["yhat"].idxmin()]
                    avg_fore   = forecast_df["yhat"].mean()
                    last_hist  = hist_df[price_col].iloc[-1]
                    pct_change = ((avg_fore - last_hist) / last_hist) * 100

                    fm0, fm1, fm2, fm3 = st.columns(4)
                    fm0.metric("Avg Forecast Price",  f"GHS {avg_fore:.2f}")
                    fm1.metric("vs Last Known Price", f"{pct_change:+.1f}%")
                    fm2.metric(
                        "Peak Month",
                        peak_row["ds"].strftime("%b %Y"),
                        delta=f"GHS {peak_row['yhat']:.2f}",
                    )
                    fm3.metric(
                        "Trough Month",
                        trough_row["ds"].strftime("%b %Y"),
                        delta=f"GHS {trough_row['yhat']:.2f}",
                        delta_color="inverse",
                    )

                    # Monthly bar breakdown
                    st.subheader(f"Monthly {primary_crop.title()} Price Forecast")
                    bar_df = (
                        forecast_df[["ds", "yhat"]]
                        .rename(columns={"ds": "Month",
                                         "yhat": "Forecast Price (GHS/kg)"})
                        .set_index("Month")
                    )
                    st.bar_chart(bar_df, x_label="Month",
                                 y_label="Price (GHS/kg)", color="#4CAF50")

                    # Month-on-month change
                    st.subheader("Month-on-Month Price Change")
                    mom_df = (
                        forecast_df[["ds", "yhat"]]
                        .copy()
                        .assign(MoM_Change=lambda d: d["yhat"].diff().round(2))
                        .dropna()
                        .rename(columns={"ds": "Month"})
                        .set_index("Month")[["MoM_Change"]]
                    )
                    st.bar_chart(mom_df, x_label="Month",
                                 y_label="Change (GHS/kg)", color="#2196F3")

            except FileNotFoundError:
                st.warning(
                    f"⚠️ No forecast model found for **{primary_crop}** in the "
                    f"**{region}** region (`{model_key}.pkl`). "
                    "You can still contact the farmer directly."
                )
            except Exception as e:
                st.error(f"Forecast error: {e}")

            st.divider()
            if st.button(
                "✖ Close",
                key=f"close_{st.session_state.enquiry_open}",
            ):
                st.session_state.enquiry_open = None
                st.rerun()

# ── Pagination (bottom) ───────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
pagination_controls("bottom")
