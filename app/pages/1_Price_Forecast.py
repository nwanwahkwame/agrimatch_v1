"""
Crop Price Forecasting Dashboard
─────────────────────────────────
Flow:
  1. User picks a region and crop.
  2. Historical data is loaded from MySQL and displayed as a chart + metrics.
  3. User sets a forecast horizon and clicks "Generate Forecast".
  4. The pre-trained model (loaded from disk) produces a forecast.
  5. Historical and forecast prices are shown on a single comparison chart.
"""

from utils import CROPS, REGIONS
import os
from pathlib import Path

import joblib
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine

# utils.py lives one level up (the project root)
import sys
sys.path.append(str(Path(__file__).resolve().parent.parent))

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Price Forecast — AgriMatch",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Environment / DB setup ────────────────────────────────────────────────────
load_dotenv()

# Model directory is always relative to this script, not the CWD
MODEL_DIR = Path(__file__).resolve().parent.parent.parent/"models"

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
    """Load a pre-trained model (.pkl) from MODEL_DIR."""
    model_path = MODEL_DIR / f"{model_name}.pkl"
    if not model_path.exists():
        raise FileNotFoundError(f"Model not found: {model_path}")
    return joblib.load(model_path)


@st.cache_data(ttl=300)          # refresh at most every 5 minutes
def load_training_data(table_name: str) -> pd.DataFrame:
    """Pull historical price data for a region+crop combination."""
    query = f"SELECT * FROM `{table_name}` ORDER BY date"
    return pd.read_sql(query, get_engine())


def forecast_from_model(model, steps: int) -> pd.Series:
    """
    Produce a forecast regardless of whether the model is:
      - a fitted statsmodels Results object  (has .forecast())
      - a pmdarima AutoARIMA object          (has .predict())
      - something else that raises clearly
    """
    if hasattr(model, "forecast"):
        # Fitted statsmodels SARIMAX / ARIMA results — already fitted, call
        # .forecast() directly; do NOT call .fit() again.
        return model.forecast(steps=steps)
    elif hasattr(model, "predict"):
        # pmdarima / sklearn-style interface
        return model.predict(n_periods=steps)
    else:
        raise ValueError(
            f"Model type '{type(model).__name__}' does not support forecasting. "
            "Expected a fitted statsmodels Results object or a pmdarima model."
        )


# ── UI: header ────────────────────────────────────────────────────────────────
st.title("📈 Crop Price Forecasting Dashboard")
st.caption(
    "Select a region and crop to view historical prices and generate a forecast.")

# ── UI: dropdowns ─────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)
with col1:
    crop = st.selectbox("Select Crop", CROPS)
with col2:
    region = st.selectbox("Select Region", REGIONS)

# Build the key used for both the DB table name and the model filename
region = region.replace(' ', '_').lower()
crop = crop.replace(' ', '').lower()
model_key = f"{region}_{crop}"

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
    st.subheader(f"Historical Data — {crop} in {region} Region")

    st.dataframe(df.tail(10), use_container_width=True)

    st.divider()

    # Summary metrics
    price_col = "cedi_price/(KG)"   # actual column name in the DB
    city_count = df["city"].nunique() if "city" in df.columns else "N/A"
    n_entries = len(df)
    average_price = df[price_col].mean()

    c0, c1, c2, c3 = st.columns(4)
    c0.info("Regional Metrics")
    c1.metric("Cities", city_count)
    c2.metric("Data Points", n_entries)
    c3.metric("Avg Price (GHS/kg)", f"{average_price:.2f}")

    st.line_chart(
        df.set_index("date")[price_col],
        x_label="Date",
        y_label="Price (GHS/kg)",
    )

    data_ok = True

except FileNotFoundError as e:
    st.warning(f"⚠️ Model not found for **{crop}** in **{region}**. "
               f"Check that `{model_key}.pkl` exists in `{MODEL_DIR}`.")
    st.caption(str(e))

except Exception as e:
    st.error(f"Failed to load data or model: {e}")

# ── Forecast section ──────────────────────────────────────────────────────────
# Always render the controls so the UI doesn't feel broken; just disable the
# button when we don't have what we need.
st.divider()
st.subheader("Price Forecast")

forecast_months = st.slider(
    "Forecast Horizon (months)",
    min_value=1,
    max_value=12,
    value=6,
)

if st.button("Generate Forecast", type="primary", disabled=not data_ok):
    try:
        with st.spinner("Generating forecast…"):
            # ── Produce forecast ──────────────────────────────────────────────
            forecast_values = forecast_from_model(model, steps=forecast_months)

            last_date = df["date"].max()
            future_dates = pd.date_range(
                start=last_date + pd.offsets.MonthBegin(1),
                periods=forecast_months,
                freq="MS",
            )

            forecast_df = pd.DataFrame({
                "Date":           future_dates,
                "Forecast Price": forecast_values.values
                if hasattr(forecast_values, "values")
                else list(forecast_values),
            })

        # ── Show forecast table ───────────────────────────────────────────────
        st.subheader("Forecast Table")
        st.dataframe(forecast_df.style.format({"Forecast Price": "{:.2f}"}),
                     use_container_width=True)

        # ── Comparison chart: historical vs forecast ──────────────────────────
        st.subheader("Historical vs Forecast")

        historical_chart = df[["date", price_col]].rename(
            columns={"date": "Date", price_col: "Historical Price"}
        ).set_index("Date")

        forecast_chart = forecast_df.set_index("Date")

        # Align on a shared date index so both series appear on one chart
        combined = historical_chart.join(forecast_chart, how="outer")

        st.line_chart(combined)

    except Exception as e:
        st.error(f"Forecast failed: {e}")
