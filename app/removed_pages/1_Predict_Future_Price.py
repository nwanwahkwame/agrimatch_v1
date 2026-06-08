import streamlit as st
import pandas as pd
import joblib
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from pathlib import Path
from utils import CROPS, REGIONS


# -----------------------------------------------------------------------------
# CONFIG
# -----------------------------------------------------------------------------
load_dotenv()

MODEL_DIR = Path("../models")
HOST = os.getenv("DB_HOST")
USERNAME = os.getenv("DB_USERNAME")
PASSWORD = os.getenv("DB_PASSWORD")
DATABASE = os.getenv("DB_DATABASE")
PORT = os.getenv("DB_PORT")

engine = create_engine(
    f"mysql+pymysql://{USERNAME}:{PASSWORD}"
    f"@{HOST}:{PORT}/{DATABASE}"
)

# -----------------------------------------------------------------------------
# DROPDOWNS
# -----------------------------------------------------------------------------

CROPS = CROPS

REGIONS = REGIONS

st.title("Crop Price Forecasting Dashboard")

col1, col2 = st.columns(2)

with col1:
    crop = st.selectbox("Select Crop", CROPS)

with col2:
    region = st.selectbox("Select Region", REGIONS)

# -----------------------------------------------------------------------------
# CREATE KEY
# -----------------------------------------------------------------------------

model_key = (f"{region}_{crop}".lower().replace(" ", ""))

# st.info(f"Selected Dataset: {model_key}")

# -----------------------------------------------------------------------------
# LOAD MODEL
# -----------------------------------------------------------------------------


@st.cache_resource
def load_model(model_name):
    model_path = MODEL_DIR / f"{model_name}.pkl"

    if not model_path.exists():
        raise FileNotFoundError(
            f"Model not found: {model_path}"
        )

    return joblib.load(model_path)

# -----------------------------------------------------------------------------
# LOAD TRAINING DATA
# -----------------------------------------------------------------------------


@st.cache_data
def load_training_data(table_name):

    query = f"""
    SELECT *
    FROM `{table_name}`
    ORDER BY date
    """

    return pd.read_sql(query, engine)


try:

    model = load_model(model_key)

    df = load_training_data(model_key)

    st.divider()

    st.subheader(f"Historical Data for {crop} in {region} Region")

    st.dataframe(df.tail())

    st.divider()

    city_count = df['city'].nunique()
    number_of_entries, _ = df.shape
    average_price = df['cedi_price/(KG)'].mean()

    col0, col1, col2, col3 = st.columns(4)

    col0.info('Regional Metrics')
    col1.metric(label="Total Number of Cities", value=f"{city_count}")
    col2.metric(label="Total Number of Data Points",
                value=f"{number_of_entries}")
    col3.metric(label="Average Price Over Period",
                value=f"{average_price:.2f}/KG")

    st.line_chart(
        df.set_index("date")[
            "cedi_price/(KG)"], x_label=f'Monthly {crop} price per kilogram over the years'
    )

except Exception as e:
    st.error(str(e))
    st.stop()

# -----------------------------------------------------------------------------
# FORECAST OPTIONS
# -----------------------------------------------------------------------------

forecast_months = st.slider(
    "Forecast Horizon (Months)",
    min_value=1,
    max_value=12,
    value=6
)

# -----------------------------------------------------------------------------
# FORECAST
# -----------------------------------------------------------------------------

if st.button("Generate Forecast"):

    try:

        # Last date from historical data
        last_date = pd.to_datetime(df["date"]).max()

        # Generate future dates monthly
        future_dates = pd.date_range(
            start=last_date + pd.offsets.MonthBegin(1),
            periods=forecast_months,
            freq="MS"
        )

        # Fit model
        model_fitted = model.fit()

        # Forecast
        forecast = model_fitted.forecast(
            steps=forecast_months
        )

        forecast_df = pd.DataFrame({
            "Date": future_dates,
            "Forecast Price": forecast
        })

        st.subheader("Forecast")

        st.dataframe(forecast_df)

        chart_df = pd.concat([
            pd.DataFrame({
                "Date": pd.to_datetime(df["date"]),
                "Price": df["price"]
            }),
            pd.DataFrame({
                "Date": future_dates,
                "Price": forecast
            })
        ])

        chart_df = chart_df.set_index("Date")

        st.line_chart(chart_df)

    except Exception as e:
        st.error(f"Forecast failed: {e}")


def predict_future(model, steps):

    if hasattr(model, "forecast"):
        return model.forecast(steps=steps)

    elif hasattr(model, "predict"):
        return model.predict(n_periods=steps)

    else:
        raise ValueError(
            "Model does not support forecasting."
        )


forecast = predict_future(
    model=model,
    steps=forecast_months
)
