"""
Crop Price Forecasting Dashboard
─────────────────────────────────
Flow:
  1. User picks a region and crop.
  2. Historical data is loaded from MySQL and shown as a chart + metrics.
  3. User sets a forecast horizon and clicks "Generate Forecast".
  4. The model (unfitted spec OR fitted results) produces a forecast.
  5. Historical and forecast prices are overlaid on one comparison chart.
"""

from utils import CROPS, REGIONS
import os
import sys
from pathlib import Path

import joblib
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine

# ── Project root on path so we can import utils.py ───────────────────────────
ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(ROOT))

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Price Forecast — AgriMatch",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Environment / DB ──────────────────────────────────────────────────────────
load_dotenv()

MODEL_DIR = ROOT / "models"
HOST = os.getenv("DB_HOST")
USERNAME = os.getenv("DB_USERNAME")
PASSWORD = os.getenv("DB_PASSWORD")
DATABASE = os.getenv("DB_DATABASE")
PORT = os.getenv("DB_PORT", "3306")

PRICE_COL = "cedi_price/(KG)"   # exact column name in the database


# ── Cached resources ──────────────────────────────────────────────────────────

@st.cache_resource
def get_engine():
    return create_engine(
        f"mysql+pymysql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"
    )


@st.cache_resource
def load_model(model_name: str):
    model_path = MODEL_DIR / f"{model_name}.pkl"
    if not model_path.exists():
        raise FileNotFoundError(
            f"No model file found at: {model_path}\n"
            f"Expected filename: {model_name}.pkl"
        )
    return joblib.load(model_path)


@st.cache_data(ttl=300)
def load_training_data(table_name: str) -> pd.DataFrame:
    query = f"SELECT * FROM `{table_name}` ORDER BY date"
    df = pd.read_sql(query, get_engine())
    df["date"] = pd.to_datetime(df["date"])
    return df


# ── Forecasting logic ─────────────────────────────────────────────────────────

def _is_statsmodels_results(obj) -> bool:
    """True when obj is a fitted statsmodels Results object."""
    try:
        from statsmodels.base.wrapper import ResultsWrapper
        from statsmodels.tsa.base.tsa_model import TimeSeriesModelResults
        return isinstance(obj, (ResultsWrapper, TimeSeriesModelResults))
    except ImportError:
        return False


def _is_statsmodels_model(obj) -> bool:
    """True when obj is an *unfitted* statsmodels Model spec."""
    try:
        from statsmodels.base.model import Model
        return isinstance(obj, Model)
    except ImportError:
        return False


def _is_pmdarima(obj) -> bool:
    """True when obj is a pmdarima ARIMA / AutoARIMA object."""
    try:
        from pmdarima.arima import ARIMA
        return isinstance(obj, ARIMA)
    except ImportError:
        return False


def get_forecast(model, training_series: pd.Series, steps: int) -> pd.Series:
    """
    Produce `steps` out-of-sample forecasts from any supported model type.

    Supported types
    ───────────────
    1. Fitted statsmodels Results object  → call .forecast(steps) directly.
    2. Unfitted statsmodels Model spec    → fit on training_series first,
                                           then call .forecast(steps).
    3. pmdarima ARIMA / AutoARIMA         → call .predict(n_periods=steps).
    4. sklearn-style                      → call .predict() with a horizon array.
    """

    # ── Case 1: already-fitted statsmodels Results ────────────────────────────
    if _is_statsmodels_results(model):
        return pd.Series(model.forecast(steps=steps))

    # ── Case 2: unfitted statsmodels Model spec ───────────────────────────────
    if _is_statsmodels_model(model):
        # The .pkl was saved before .fit() was called, so we fit it now.
        fitted = model.fit(disp=False)
        return pd.Series(fitted.forecast(steps=steps))

    # ── Case 3: pmdarima ──────────────────────────────────────────────────────
    if _is_pmdarima(model):
        return pd.Series(model.predict(n_periods=steps))

    # ── Case 4: generic fallback — try common interfaces in order ─────────────
    # Some models are saved as class instances with a custom .forecast() that
    # does NOT require params (unlike the base statsmodels Model).
    for method, kwargs in [
        ("forecast",  {"steps": steps}),
        ("forecast",  {"periods": steps}),
        ("predict",   {"n_periods": steps}),
        ("predict",   {"steps": steps}),
    ]:
        fn = getattr(model, method, None)
        if fn is None:
            continue
        try:
            result = fn(**kwargs)
            return pd.Series(result)
        except TypeError:
            continue

    raise ValueError(
        f"Cannot forecast with model of type '{type(model).__name__}'. "
        "It is neither a fitted statsmodels Results object, an unfitted "
        "statsmodels Model, nor a pmdarima model. "
        "Please save the *fitted* model (after calling .fit()) with joblib."
    )


# ── UI ────────────────────────────────────────────────────────────────────────

st.title("📈 Crop Price Forecasting Dashboard")
st.caption("Select a region and crop to view historical prices and run a forecast.")

col1, col2 = st.columns(2)
with col1:
    crop = st.selectbox("Select Crop", CROPS)
with col2:
    region = st.selectbox("Select Region", REGIONS)

model_key = f"{region}_{crop}".lower().replace(" ", "_")

st.divider()

# ── Load data & model ─────────────────────────────────────────────────────────
data_ok = False
df = pd.DataFrame()
model = None
training_series = pd.Series(dtype=float)

try:
    model = load_model(model_key)
    df = load_training_data(model_key)

    if PRICE_COL not in df.columns:
        available = ", ".join(df.columns.tolist())
        raise KeyError(
            f"Expected column '{PRICE_COL}' not found in table '{model_key}'.\n"
            f"Available columns: {available}"
        )

    training_series = df.set_index("date")[PRICE_COL].astype(float)

    # ── Historical section ────────────────────────────────────────────────────
    st.subheader(f"Historical Data — {crop} in {region} Region")
    st.dataframe(df.tail(10), use_container_width=True)
    st.divider()

    city_count = df["city"].nunique() if "city" in df.columns else "N/A"
    n_entries = len(df)
    average_price = df[PRICE_COL].mean()

    c0, c1, c2, c3 = st.columns(4)
    c0.info("Regional Metrics")
    c1.metric("Cities", city_count)
    c2.metric("Data Points", n_entries)
    c3.metric("Avg Price (GHS/kg)", f"{average_price:.2f}")

    st.line_chart(
        training_series,
        x_label="Date",
        y_label="Price (GHS/kg)",
    )

    data_ok = True

except FileNotFoundError as e:
    st.warning(
        f"⚠️ No model found for **{crop}** in **{region}**. "
        f"Make sure `{model_key}.pkl` exists inside `{MODEL_DIR}`."
    )
    st.caption(str(e))

except KeyError as e:
    st.error(f"Column error: {e}")

except Exception as e:
    st.error(f"Failed to load data or model: {e}")

# ── Forecast controls (always visible) ───────────────────────────────────────
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
            forecast_values = get_forecast(
                model=model,
                training_series=training_series,
                steps=forecast_months,
            )

            last_date = df["date"].max()
            future_dates = pd.date_range(
                start=last_date + pd.offsets.MonthBegin(1),
                periods=forecast_months,
                freq="MS",
            )

            forecast_df = pd.DataFrame(
                {"Forecast Price (GHS/kg)": forecast_values.values},
                index=pd.Index(future_dates, name="Date"),
            )

        # ── Forecast table ────────────────────────────────────────────────────
        st.subheader("Forecast Table")
        st.dataframe(
            forecast_df.style.format({"Forecast Price (GHS/kg)": "{:.2f}"}),
            use_container_width=True,
        )

        # ── Comparison chart ──────────────────────────────────────────────────
        st.subheader("Historical vs Forecast")

        historical_df = training_series.rename(
            "Historical Price (GHS/kg)").to_frame()

        combined = pd.concat([historical_df, forecast_df], axis=0)
        # Ensure the forecast line starts where history ends (no gap)
        combined.loc[last_date, "Forecast Price (GHS/kg)"] = float(
            historical_df.loc[last_date] if last_date in historical_df.index
            else historical_df.iloc[-1]
        )
        combined = combined.sort_index()

        st.line_chart(combined)

    except Exception as e:
        st.error(f"Forecast failed: {e}")
        st.caption(
            "If you see 'missing required positional argument: params', your .pkl "
            "file contains an *unfitted* statsmodels model. Either:\n"
            "- Re-save after calling model.fit(), or\n"
            "- The auto-fit path above should have handled it — check the traceback."
        )
