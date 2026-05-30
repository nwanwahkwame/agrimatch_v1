# Install relevant dependencies
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.stattools import adfuller, kpss
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from sklearn.metrics import mean_absolute_error, mean_squared_error

from sqlalchemy import select, Table, MetaData, create_engine
from glob import glob
import pickle
import warnings

warnings.filterwarnings('ignore')

# Step 5 ----------------------------------------------------------------------------


def crop_forecaster():
    """
    Predict future cost of selected crop based on region.
    """

    USERNAME = "root"
    PASSWORD = "root"
    HOST = "localhost"
    PORT = "3306"
    DATABASE = "crop_database"

    # SQLAlchemy connection
    connection_string = (
        f"mysql+pymysql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}")

    # Create SQLAlchemy engine
    engine = create_engine(connection_string)

    print('-'*50)
    print('Step 5 initiated: Predicting crop prices ✅\n')
    # print(f"Connected to {DATABASE} successfully.\n")

    df = pd.read_sql_table("ashanti_cassava", engine)

    # Examine dataset structure
    # print('\nMissing Values:\n')
    # print(df.isnull().sum())

    # Convert date column
    date_col = [col for col in df.columns if 'date' in col.lower()][0]
    price_col = [col for col in df.columns if 'price' in col.lower()][0]

    df[date_col] = pd.to_datetime(df[date_col])

    # Sort data
    df = df.sort_values(by=date_col)

    # Set index
    df.set_index(date_col, inplace=True)

    # Create monthly average price series
    monthly_prices = df[price_col].resample('M').mean()
    monthly_prices = monthly_prices.interpolate()

    # Plot time series
    plt.figure(figsize=(12, 6))

    plt.plot(monthly_prices)
    plt.title('Monthly Cowpea Prices in Ashanti Region')
    plt.xlabel('Date')
    plt.ylabel('Average Price')
    plt.grid(True)
    plt.savefig('outputs/crop_time_series.jpg')
    plt.close()

    # ADF test
    adfuller_result = adfuller(monthly_prices.dropna())

    # print('ADF Statistic:', adfuller_result[0])
    # print('p-value:', adfuller_result[1])
    # print('lags:', adfuller_result[2])
    # print('critical values:', adfuller_result[3])

    # if adfuller_result[1] < 0.05:
    #     print('The series is stationary')
    # else:
    #     print('The series is NOT stationary')

    # KPSS test
    stat, p_value, lags, crit = kpss(monthly_prices, regression='c')

    # print('KPSS Statistic:', stat)
    # print('p-value:', p_value)
    # print('lags:', lags)
    # print('critical values:', crit)

    # if p_value < 0.05:
    #     print('The series is NOT stationary')
    # else:
    #     print('The series is stationary')

    # ACF & PACF plot
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    plot_acf(monthly_prices, ax=axes[0])
    plot_pacf(monthly_prices, ax=axes[1])
    plt.savefig('outputs/crop_ACF_PACF.jpg')
    plt.close()

    # Train-Test Split
    train = monthly_prices[:-6]
    test = monthly_prices[-6:]

    # print('Training observations:', len(train))
    # print('Testing observations:', len(test))

    # Plot the train and test data
    plt.figure(figsize=(12, 5))

    plt.plot(train, label='Train')
    plt.plot(test, label='Test')
    plt.legend()
    plt.title("Train-Test Split")
    plt.savefig('outputs/crop_train_test_split.jpg')
    plt.close()

    # Build SARIMA Model
    model = SARIMAX(train, order=(1, 1, 1), seasonal_order=(
        1, 1, 1, 12), enforce_stationarity=False, enforce_invertibility=False)
    results = model.fit()

    print('Prediction Results')
    print(results.summary())

    # Forecast on test data
    forecast = results.forecast(steps=len(test))
    forecast_df = pd.DataFrame(
        {'Actual': test.values, 'Predicted': forecast.values}, index=test.index)

    # Evaluate model
    mae = mean_absolute_error(test, forecast)
    rmse = np.sqrt(mean_squared_error(test, forecast))

    # print(f'MAE: {mae:.2f}')
    # print(f'RMSE: {rmse:.2f}')

    # Visualize predictions
    plt.figure(figsize=(12, 6))

    plt.plot(train.index, train, label='Training Data')
    plt.plot(test.index, test, label='Actual Prices')
    plt.plot(test.index, forecast, label='Predicted Prices')

    plt.title('Crop Price Forecasting')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.grid(True)
    plt.savefig('outputs/crop_price_forecasting.jpg')
    plt.close()

    # Future prediction

    future_forecast = results.forecast(steps=12)

    future_dates = pd.date_range(
        start=monthly_prices.index[-1] + pd.offsets.MonthEnd(), periods=12, freq='M')

    future_df = pd.DataFrame(
        {'Date': future_dates, 'Predicted Price': future_forecast.values})

    # Plot future forecast
    plt.figure(figsize=(12, 6))

    plt.plot(monthly_prices.index, monthly_prices, label='Historical Prices')
    plt.plot(future_dates, future_forecast, label='Future Forecast')

    plt.title('Future Cowpea Price Forecast')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.grid(True)
    plt.savefig('outputs/crop_price_future_forecast.jpg')
    plt.close()

    # save the best model
    with open('models/sarimax_model.pkl', 'wb') as f:
        pickle.dump(results, f)

    print('Model saved.')
