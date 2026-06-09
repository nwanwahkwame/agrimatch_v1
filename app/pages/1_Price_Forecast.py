"""
Crop Price Forecasting Dashboard
─────────────────────────────────
Flow:
  1. User picks a region and crop.
  2. Historical data is loaded from MySQL and displayed as a chart + metrics.
  3. User sets a forecast horizon and clicks "Generate Forecast".
  4. The pre-trained Prophet model (loaded from disk) produces a forecast.
  5. Historical and forecast prices are shown on a single comparison chart.
"""

from sqlalchemy import create_engine
from dotenv import load_dotenv
import streamlit as st
import pandas as pd
import pickle
from utils import inject_css, init_session, CROPS, REGIONS
import sys
import os
from pathlib import Path

# utils.py lives one level up (the project root)
sys.path.append(str(Path(__file__).resolve().parent.parent))


# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Price Forecast — AgriMatch",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

inject_css()
init_session()

st.markdown("""
<div class="page-header">
    <div class="page-header-title" style="text-align: center;">📈 Crop Price Forecasting Dashboard</div>
    <div class="page-header-sub" style="text-align: center;">Select a region and crop to view historical prices and generate a forecast</div>
</div>""", unsafe_allow_html=True)

# ── Environment / DB setup ────────────────────────────────────────────────────
load_dotenv()

# Model directory is always relative to this script, not the CWD
MODEL_DIR = Path(__file__).resolve().parent.parent.parent / "models"

HOST = os.getenv("DB_HOST")
USERNAME = os.getenv("DB_USERNAME")
PASSWORD = os.getenv("DB_PASSWORD")
DATABASE = os.getenv("DB_DATABASE")
PORT = os.getenv("DB_PORT")


@st.cache_resource
def get_engine():
    """Create (and cache) the SQLAlchemy engine."""
    return create_engine(
        f"mysql+pymysql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"
    )


# ── Helpers ───────────────────────────────────────────────────────────────────

@st.cache_resource
def load_model(model_name: str):
    """
    Load a pre-trained Prophet model (.pkl) from MODEL_DIR.
    Prophet models are serialised with pickle, not joblib.
    """
    model_path = MODEL_DIR / f"{model_name}.pkl"
    if not model_path.exists():
        raise FileNotFoundError(f"Model not found: {model_path}")
    with open(model_path, "rb") as f:
        return pickle.load(f)


@st.cache_data(ttl=300)          # refresh at most every 5 minutes
def load_training_data(table_name: str) -> pd.DataFrame:
    """Pull historical price data for a region+crop combination."""
    query = f"SELECT * FROM `{table_name}` ORDER BY date"
    return pd.read_sql(query, get_engine())


def forecast_from_prophet(model, last_date: pd.Timestamp, steps: int) -> pd.DataFrame:
    """
    Drive a fitted Prophet model forward by `steps` months.

    Prophet requires a future DataFrame built by make_future_dataframe();
    it must include the historical dates so the model can anchor the trend
    correctly. We then slice off only the new future rows.

    Returns a DataFrame with columns:
        ds              — future month-start dates
        yhat            — point forecast
        yhat_lower      — lower uncertainty bound (80 % by default)
        yhat_upper      — upper uncertainty bound
    """
    future = model.make_future_dataframe(periods=steps, freq="MS")
    forecast = model.predict(future)

    # Keep only the rows that lie beyond the last historical date
    future_forecast = forecast[forecast["ds"] > last_date][
        ["ds", "yhat", "yhat_lower", "yhat_upper"]
    ].reset_index(drop=True)

    # Round to 2 d.p. for display
    future_forecast[["yhat", "yhat_lower", "yhat_upper"]] = (
        future_forecast[["yhat", "yhat_lower", "yhat_upper"]].round(2)
    )

    return future_forecast


# ── UI: dropdowns ─────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)
with col1:
    crop = st.selectbox("Select Crop", CROPS)
with col2:
    region = st.selectbox("Select Region", REGIONS)

# Build the key used for both the DB table name and the model filename
region = region.replace(' ', '_').replace('-', ' ')
crop = crop.replace(' ', '')
model_key = f"{region}_{crop}".lower()

st.divider()

# ── Load data & model ─────────────────────────────────────────────────────────
data_ok = False
df = pd.DataFrame()
model = None

try:
    model = load_model(model_key)
    df = load_training_data(model_key)

    # Normalise the date column once
    df["date"] = pd.to_datetime(df["date"])

    # ── Historical section ────────────────────────────────────────────────────
    st.subheader(f"Historical Metrics — {crop} in {region} Region")

    price_col = "cedi_price/(KG)"
    city_count = df["city"].nunique() if "city" in df.columns else "N/A"
    popular_market = df["city"].mode(
    ).iloc[0] if "city" in df.columns else "N/A"
    min_year = df["year"].min()
    max_year = df["year"].max()
    n_entries = len(df)
    average_price = df[price_col].mean()

    c0, c1, c2, c3, c4 = st.columns([3, 2, 1, 2, 3])
    c0.metric("Year Span",          f"{min_year} – {max_year}")
    c1.metric("Major Market(s)",      city_count)
    c2.metric("Data Points",  n_entries)
    c3.metric("Avg Price (GHS/kg)", f"{average_price:.2f}")
    c4.metric("Popular Market",     popular_market)

    st.line_chart(
        df.set_index("date")[price_col],
        x_label="Date",
        y_label="Price (GHS/kg)",
        color="green",
    )

    data_ok = True

except FileNotFoundError as e:
    st.warning(
        f"⚠️ Model not found for **{crop}** in **{region}**. "
        f"Check that `{model_key}.pkl` exists in `{MODEL_DIR}`."
    )
    st.caption(str(e))

except Exception as e:
    st.error(f"Failed to load data or model: {e}")

# ── Forecast section ──────────────────────────────────────────────────────────
st.divider()
st.subheader("Price Forecast")

forecast_months = st.slider(
    "Forecast Horizon (months)",
    min_value=1,
    max_value=48,
    value=12,
)

if st.button("Generate Forecast", type="primary", disabled=not data_ok):
    try:
        with st.spinner("Generating forecast…"):
            last_date = df["date"].max()
            forecast_df = forecast_from_prophet(
                model, last_date, forecast_months)

        # ── Comparison chart: historical vs forecast ──────────────────────────
        st.subheader("Predicted Prices")

        # Build a unified DataFrame so both series share one x-axis
        historical_chart = (
            df[["date", price_col]]
            .rename(columns={"date": "ds", price_col: "Historical Price"})
            .set_index("ds")
        )

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

        combined = historical_chart.join(forecast_chart, how="outer")

        st.line_chart(
            combined,
            x_label="Date",
            y_label="Price (GHS/kg)",
        )

        # ── Forecast summary metrics ──────────────────────────────────────────
        st.divider()
        peak_row = forecast_df.loc[forecast_df["yhat"].idxmax()]
        trough_row = forecast_df.loc[forecast_df["yhat"].idxmin()]
        avg_fore = forecast_df["yhat"].mean()
        last_hist = df[price_col].iloc[-1]
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

        # ── Bar chart: forecast price per month ───────────────────────────────
        st.subheader(f"Monthly {crop.title()} Forecast Breakdown")
        bar_df = (
            forecast_df[["ds", "yhat"]]
            .rename(columns={"ds": "Month", "yhat": "Forecast Price (GHS/kg)"})
            .set_index("Month")
        )
        st.bar_chart(
            bar_df,
            x_label="Month",
            y_label="Price (GHS/kg)",
            color="#4CAF50",
        )

        # ── Month-on-month change chart ───────────────────────────────────────
        st.subheader("Month-on-Month Price Change")
        mom_df = (
            forecast_df[["ds", "yhat"]]
            .copy()
            .assign(MoM_Change=lambda d: d["yhat"].diff().round(2))
            .dropna()
            .rename(columns={"ds": "Month"})
            .set_index("Month")[["MoM_Change"]]
        )
        st.bar_chart(
            mom_df,
            x_label="Month",
            y_label="Change (GHS/kg)",
            color="#2196F3",
        )

        # ── Forecast table ────────────────────────────────────────────────────
        # st.subheader("Forecast Table")
        # display_df = forecast_df.rename(columns={
        #     "ds":         "Date",
        #     "yhat":       "Forecast Price (GHS/kg)",
        #     "yhat_lower": "Lower Bound",
        #     "yhat_upper": "Upper Bound",
        # })
        # st.dataframe(
        #     display_df.style.format({
        #         "Forecast Price (GHS/kg)": "{:.2f}",
        #         "Lower Bound":             "{:.2f}",
        #         "Upper Bound":             "{:.2f}",
        #     }),
        #     use_container_width=True,
        # )

    except Exception as e:
        st.error(f"Forecast failed: {e}")
