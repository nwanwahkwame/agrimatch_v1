"""
Crop Price Forecasting Dashboard
A comprehensive Gradio interface for crop price prediction and analysis
using time series machine learning models and MySQL database integration.
"""

import plotly.graph_objects as go
import plotly.express as px
import gradio as gr
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sqlalchemy import create_engine, inspect, text
import numpy as np
import pandas as pd
import warnings
import traceback

warnings.filterwarnings("ignore")


# =========================================================
# DATABASE CONFIGURATION
# =========================================================
MYSQL_USER = "root"
MYSQL_PASSWORD = "root"
MYSQL_HOST = "localhost"
MYSQL_PORT = "3306"
MYSQL_DATABASE = "crop_database"

DATABASE_URL = (
    f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}"
    f"@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
)

engine = create_engine(DATABASE_URL)

# =========================================================
# HELPER FUNCTIONS
# =========================================================


def get_tables():
    """Retrieve all table names from the database."""
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        return tables
    except Exception as e:
        print(f"Error fetching tables: {e}")
        return []


def extract_regions_and_crops():
    """Extract region-crop mapping from table names."""
    tables = get_tables()
    region_crop_map = {}

    for table in tables:
        if "_" in table:
            # Split on first underscore to handle crops with multiple words
            parts = table.split("_", 1)
            region = parts[0]
            crop = parts[1]

            if region not in region_crop_map:
                region_crop_map[region] = []

            if crop not in region_crop_map[region]:
                region_crop_map[region].append(crop)

    # Sort for better UI presentation
    for region in region_crop_map:
        region_crop_map[region].sort()

    return region_crop_map


def load_crop_data(region, crop):
    """Load crop data from database."""
    try:
        table_name = f"{region}_{crop}"
        query = f"SELECT * FROM `{table_name}`"
        df = pd.read_sql(query, engine)
        return df
    except Exception as e:
        raise Exception(f"Error loading data for {region}_{crop}: {str(e)}")


def preprocess_data(df):
    """Preprocess data for time series forecasting."""
    try:
        # Identify date and price columns
        date_col = [col for col in df.columns if 'date' in col.lower()][0]
        price_col = [col for col in df.columns if 'price' in col.lower()][0]

        df_copy = df.copy()
        df_copy[date_col] = pd.to_datetime(df_copy[date_col])
        df_copy = df_copy.sort_values(date_col)

        # Create time-based features
        df_copy["year_feature"] = df_copy[date_col].dt.year
        df_copy["month_feature"] = df_copy[date_col].dt.month
        df_copy["day_feature"] = df_copy[date_col].dt.day
        df_copy["dayofweek"] = df_copy[date_col].dt.dayofweek

        # Lag features
        df_copy["lag_1"] = df_copy[price_col].shift(1)
        df_copy["lag_7"] = df_copy[price_col].shift(7)

        # Rolling mean
        df_copy["rolling_mean_7"] = df_copy[price_col].rolling(window=7).mean()

        # Drop NaN values
        df_copy = df_copy.dropna()

        return df_copy, date_col, price_col

    except Exception as e:
        raise Exception(f"Error preprocessing data: {str(e)}")


def train_model(df, price_col):
    """Train RandomForest model for price prediction."""
    try:
        features = [
            "year_feature",
            "month_feature",
            "day_feature",
            "dayofweek",
            "lag_1",
            "lag_7",
            "rolling_mean_7"
        ]

        X = df[features]
        y = df[price_col]

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, shuffle=False, test_size=0.2
        )

        model = RandomForestRegressor(
            n_estimators=200,
            random_state=42,
            n_jobs=-1
        )

        model.fit(X_train, y_train)
        predictions = model.predict(X_test)

        mae = mean_absolute_error(y_test, predictions)
        rmse = np.sqrt(mean_squared_error(y_test, predictions))
        r2 = r2_score(y_test, predictions)

        return model, mae, rmse, r2, X_test, y_test, predictions

    except Exception as e:
        raise Exception(f"Error training model: {str(e)}")


def predict_crop_price(region, crop, forecast_date):
    """Make crop price prediction and generate visualizations."""
    try:
        # Load and preprocess data
        df = load_crop_data(region, crop)
        df_processed, date_col, price_col = preprocess_data(df)

        # Train model
        model, mae, rmse, r2, X_test, y_test, predictions = train_model(
            df_processed, price_col
        )

        # Parse forecast date
        forecast_date = pd.to_datetime(forecast_date)

        # Get latest data point
        latest_row = df_processed.iloc[-1]

        # Create prediction features
        prediction_features = pd.DataFrame({
            "year_feature": [forecast_date.year],
            "month_feature": [forecast_date.month],
            "day_feature": [forecast_date.day],
            "dayofweek": [forecast_date.dayofweek],
            "lag_1": [latest_row[price_col]],
            "lag_7": [latest_row["lag_7"]],
            "rolling_mean_7": [latest_row["rolling_mean_7"]]
        })

        # Make prediction
        prediction = model.predict(prediction_features)[0]

        # Calculate metrics
        latest_price = df_processed[price_col].iloc[-1]
        avg_price = df_processed[price_col].mean()
        min_price = df_processed[price_col].min()
        max_price = df_processed[price_col].max()
        std_price = df_processed[price_col].std()
        table_records = len(df)
        date_range = f"{df_processed[date_col].min().date()} to {df_processed[date_col].max().date()}"

        city_col = [col for col in df.columns if 'city' in col.lower()]
        city_count = df[city_col[0]].nunique() if city_col else None

        # Create historical price chart
        historical_fig = px.line(
            df_processed,
            x=date_col,
            y=price_col,
            title=f"{crop.title()} Price History - {region.title()}",
            labels={
                date_col: "Date",
                price_col: "Price (GH₵ per K/G)"
            }
        )
        historical_fig.update_traces(line=dict(color='#1f77b4', width=2))
        historical_fig.update_layout(
            hovermode='x unified',
            template='plotly_white'
        )

        # Create prediction vs actual chart
        test_df = pd.DataFrame({
            'Actual': y_test.values,
            'Predicted': predictions
        })

        comparison_fig = go.Figure()
        comparison_fig.add_trace(go.Scatter(
            y=test_df['Actual'],
            name='Actual',
            mode='lines+markers',
            line=dict(color='#2ca02c', width=2)
        ))
        comparison_fig.add_trace(go.Scatter(
            y=test_df['Predicted'],
            name='Predicted',
            mode='lines+markers',
            line=dict(color='#ff7f0e', width=2)
        ))
        comparison_fig.update_layout(
            title=f"Model Predictions vs Actual Prices",
            xaxis_title="Test Set Samples",
            yaxis_title="Price (GH₵ per K/G)",
            hovermode='x unified',
            template='plotly_white'
        )

        # Format prediction output
        prediction_text = f"""
        ## 🎯 Price Prediction Result

        **Crop:** {crop.title()}  
        **Region:** {region.title()}  
        **Forecast Date:** {forecast_date.strftime('%B %d, %Y')}

        ---

        ### **Predicted Price: GH₵ {prediction:.2f} per K/G**

        ---

        #### Model Performance:
        - **Mean Absolute Error (MAE):** GH₵ {mae:.2f}
        - **Root Mean Squared Error (RMSE):** GH₵ {rmse:.2f}
        - **R-squared (R^{2}):** GH₵ {r2:.2f}
        """

        return prediction_text, historical_fig, comparison_fig

    except Exception as e:
        error_msg = f"Error: {str(e)}\n\n{traceback.format_exc()}"
        return error_msg, None, None


def update_crop_choices(region):
    """Update crop dropdown based on selected region."""
    try:
        region_crop_map = extract_regions_and_crops()
        crops = region_crop_map.get(region, [])
        if crops:
            return gr.update(choices=crops, value=crops[0])
        else:
            return gr.update(choices=[], value=None)
    except Exception as e:
        return gr.update(choices=[], value=None)


# =========================================================
# MAIN GRADIO INTERFACE
# =========================================================

def main():
    # Extract region-crop mapping
    region_crop_map = extract_regions_and_crops()
    regions = sorted(list(region_crop_map.keys()))

    if not regions:
        print("❌ Error: No regions found in database. Please ensure the database is properly configured.")
        return

    initial_crops = sorted(region_crop_map.get(regions[0], []))

    # Create Gradio interface with custom theme
    with gr.Blocks(
        title="Crop Price Forecasting Dashboard",
        theme=gr.themes.Soft(
            primary_hue="orange",
            font=["Inter", "system-ui"],
            text_size="md",
            spacing_size="md"
        ),
        css="""
            body {
                background-color: #121212;
                color: #f4f4f4;
            }
            .gradio-container {
                background-color: #121212;
            }
            .gr-box, .gr-row {
                background: #1f1f1f;
                border: 1px solid rgba(255,138,0,0.2);
                border-radius: 24px;
                box-shadow: 0 20px 45px rgba(0,0,0,0.35);
            }
            .gr-column {
                gap: 18px;
            }
            .gr-markdown h1,
            .gr-markdown h2 {
                color: #ffb74d;
            }
            .gr-markdown p {
                color: #dcdcdc;
            }
            .gr-button {
                background: #fb8c00;
                color: #ffffff;
                border: none;
                box-shadow: 0 12px 26px rgba(251,140,0,0.3);
                border-radius: 14px;
            }
            .gr-button:hover {
                background: #ff9800;
            }
            .gr-input,
            .gr-dropdown,
            .gr-textbox,
            .gr-number {
                border-radius: 14px;
                box-shadow: 0 8px 24px rgba(0,0,0,0.35);
                border: 1px solid rgba(255,255,255,0.12);
                background: #232323;
                color: #f4f4f4;
            }
            .gradio-container .gr-block {
                padding: 22px;
            }
            .gr-block {
                border: none;
            }
            .gr-markdown table {
                color: #f4f4f4;
            }
            .gr-markdown table th,
            .gr-markdown table td {
                border-color: rgba(255,255,255,0.12);
            }
        """
    ) as demo:

        # ========== HEADER ==========
        gr.Markdown(
            "# 🌾 Crop Price Forecasting Dashboard"
        )
        gr.Markdown(
            "Predict crop prices using advanced time series machine learning models "
            "and view historical market analytics from our agricultural database."
        )

        # ========== MAIN CONTENT ==========
        with gr.Row():

            # ========== LEFT PANEL: INPUT CONTROLS ==========
            with gr.Column(scale=1, min_width=300):
                gr.Markdown("### ⚙️ Forecasting Parameters")

                region_dropdown = gr.Dropdown(
                    choices=regions,
                    value=regions[0],
                    label="📍 Select Region",
                    info="Choose an agricultural region"
                )

                crop_dropdown = gr.Dropdown(
                    choices=initial_crops,
                    value=initial_crops[0] if initial_crops else None,
                    label="🌱 Select Crop",
                    info="Choose a crop to forecast"
                )

                prediction_date = gr.Textbox(
                    label="📅 Forecast Date",
                    placeholder="2026-12-01",
                    info="Enter date in YYYY-MM-DD format"
                )

                predict_button = gr.Button(
                    "🔮 Predict Price",
                    variant="primary",
                    size="lg"
                )

            # ========== RIGHT PANEL: OUTPUTS ==========
            with gr.Column(scale=2):

                # Prediction Result
                # gr.Markdown("### 🎯 Prediction Results")
                prediction_output = gr.Markdown(
                    value="Select parameters and click 'Predict Price' to see results."
                )

        # ========== VISUALIZATIONS ==========
        gr.Markdown("### 📈 Price Visualizations")
        with gr.Row():
            with gr.Column():
                price_history_chart = gr.Plot(
                    label="Historical Prices"
                )
            with gr.Column():
                prediction_comparison_chart = gr.Plot(
                    label="Model Performance"
                )

        # ========== EVENT HANDLERS ==========
        # Update crops when region changes
        region_dropdown.change(
            fn=update_crop_choices,
            inputs=region_dropdown,
            outputs=crop_dropdown
        )

        # Make prediction when button is clicked
        predict_button.click(
            fn=predict_crop_price,
            inputs=[
                region_dropdown,
                crop_dropdown,
                prediction_date
            ],
            outputs=[
                prediction_output,
                price_history_chart,
                prediction_comparison_chart
            ]
        )

        # ========== FOOTER ==========
        gr.Markdown("---")
        gr.Markdown(
            "**Database:** crop_database | "
            "**Model:** Random Forest Regressor | "
            "**Data Source:** MySQL Agricultural Database"
        )

    return demo


if __name__ == "__main__":
    demo = main()
    if demo:
        demo.launch(share=False, server_name="127.0.0.1", server_port=7860)
