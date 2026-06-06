# Import relevant dependencies
import pandas as pd
import numpy as np

from sqlalchemy import create_engine

from statsmodels.tsa.stattools import acf, pacf, adfuller
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tools.sm_exceptions import ConvergenceWarning

from sklearn.metrics import mean_absolute_error, mean_squared_error
from dotenv import load_dotenv
from itertools import product
import warnings
import pickle
import os

warnings.filterwarnings("ignore", category=ConvergenceWarning)

# Find a way to integrate into main dashboard and make it dynamic per user input.
region_name = 'Greater_accra'
city = 'Accra'
crop = 'Maize'

# Automating p, d, q: Option One

# 1. Automatically Determine d (Differencing Order)


def find_d(series: pd.Series, max_diff=4) -> int:
    """
    Determine the order of differencing (d) needed to make a time series stationary using the Augmented Dickey-Fuller test.

    Parameters:
    series (pd.Series): The time series data to be tested for stationarity.
    max_diff (int): The maximum number of differencing attempts to find stationarity. Default is 4.
    """

    d = 0
    temp = series.copy()

    while d <= max_diff:
        p_value = adfuller(temp.dropna())[1]

        if p_value < 0.05:
            return d

        temp = temp.diff()
        d += 1

    return max_diff


# 2. After differencing, automatically calculate PACF for p

def find_p(series: pd.Series) -> int:
    """
    Determine the order of the autoregressive term (p) using the Partial Autocorrelation Function (PACF) after differencing the series.

    Parameters:
    series (pd.Series): The differenced time series data for which to calculate the PACF and determine the order of the autoregressive term (p).
    """

    if find_d(series) > 0:
        series = series.diff(find_d(series)).dropna()
        pacf_values = pacf(series.dropna(), nlags=20)
        N = len(series.dropna())

        confidence_limit = 1.96 / np.sqrt(N)

        significant_p = [lag for lag, value in enumerate(
            pacf_values[1:], start=1) if abs(value) > confidence_limit]
        p = max(significant_p) if significant_p else 0

    else:
        pacf_values = pacf(series.dropna(), nlags=20)
        N = len(series.dropna())

        confidence_limit = 1.96 / np.sqrt(N)

        significant_p = [lag for lag, value in enumerate(
            pacf_values[1:], start=1) if abs(value) > confidence_limit]
        p = max(significant_p) if significant_p else 0

    return p


# 3. Automatically Calculate ACF for q

def find_q(series: pd.Series) -> int:
    """
    Determine the order of the moving average term (q) using the Autocorrelation Function (ACF) after differencing the series.

    Parameters:
    series (pd.Series): The differenced time series data for which to calculate the ACF and determine the order of the moving average term (q).
    """

    if find_d(series) > 0:
        series = series.diff(find_d(series)).dropna()

        acf_values = acf(series.dropna(), nlags=20)
        N = len(series.dropna())

        confidence_limit = 1.96 / np.sqrt(N)

        significant_q = [lag for lag, value in enumerate(
            acf_values[1:], start=1) if abs(value) > confidence_limit]

        q = max(significant_q) if significant_q else 0

    else:
        acf_values = acf(series.dropna(), nlags=20)
        N = len(series.dropna())

        confidence_limit = 1.96 / np.sqrt(N)

        significant_q = [lag for lag, value in enumerate(
            acf_values[1:], start=1) if abs(value) > confidence_limit]

        q = max(significant_q) if significant_q else 0

    return q

# 4. Dynamic ARIMA order


def dynamic_order(y: pd.Series) -> tuple:

    order = find_p(y), find_d(y), find_q(y)

    return order

# Automating p, d, q: Option Two

# Hyperparameter approach of ACF and PACF


def find_best_arima(series: pd.Series, d: int, p_range=range(0, 10), q_range=range(0, 10)) -> tuple:
    """
    Find the best ARIMA model order (p, d, q) based on the lowest AIC value by iterating through specified ranges of p and q while keeping d fixed.

    Parameters:
    series (pd.Series): The time series data for which to find the best ARIMA model order.
    d (int): The order of differencing to be used in the ARIMA model.
    p_range (range): The range of values for the autoregressive term (p) to be tested. Default is range(0, 10).
    q_range (range): The range of values for the moving average term (q) to be tested. Default is range(0, 10).    
    """

    d = find_d(series)

    best_aic = float('inf')
    best_order = None

    for p, q in product(p_range, q_range):

        try:
            model = ARIMA(series, order=(p, d, q))
            result = model.fit()

            if result.aic < best_aic:
                best_aic = result.aic
                best_order = (p, d, q)

        except:
            continue

    return best_order, best_aic

# Automating p, d, q: Option Three (SARIMA)

# 4. Automatically Determine Seasonality (s)


def find_s(series: pd.Series, max_seasonal_period=24) -> int:
    """
    Determine the seasonal period (s) of a time series by analyzing the autocorrelation function (ACF) and identifying significant peaks that indicate seasonality.

    Parameters:
    series (pd.Series): The time series data for which to determine the seasonal period.
    max_seasonal_period (int): The maximum seasonal period to consider when analyzing the ACF for significant peaks. Default is 24.
    """

    acf_values = acf(series.dropna(), nlags=max_seasonal_period)
    N = len(series.dropna())

    confidence_limit = 1.96 / np.sqrt(N)

    significant_peaks = [lag for lag, value in enumerate(
        acf_values[1:], start=1) if abs(value) > confidence_limit]

    s = min(significant_peaks) if significant_peaks else 0

    return s

# Model Building

# Function to retrieve credentials from dotenv to initialize MySQL database


def retrieve_data_from_dot_env_to_engine():
    """
    Function to retrieve credentials from dotenv to initialize MySQL database connection using SQLAlchemy.
    """

    # Database connection parameters
    USERNAME = os.getenv("DB_USERNAME")
    PASSWORD = os.getenv("DB_PASSWORD")
    HOST = os.getenv("DB_HOST")
    PORT = os.getenv("DB_PORT")
    DATABASE = os.getenv("DB_DATABASE")

    # SQLAlchemy connection
    connection_string = (
        f"mysql+pymysql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}")

    # Create SQLAlchemy engine
    engine = create_engine(connection_string)

    return engine


# Function to retrieve data from MySQL database


def retrieve_data_from_db(region_name: str = region_name,
                          crop: str = crop) -> pd.DataFrame:
    """
    Retrieve data from MySQL database for a specific city and crop.

    Parameters:
    engine: SQLAlchemy engine object for database connection
    city_name: Name of the city (string)
    crop: Name of the crop (string)
    """

    load_dotenv()  # Load environment variables from .env file

    engine = retrieve_data_from_dot_env_to_engine()

    table_name = f"{region_name.lower()}_{crop.lower()}"
    query = f"SELECT * FROM {table_name};"
    df = pd.read_sql(query, engine)

    return df


def all_cities_and_crops() -> dict:
    """
    Retrieve data for all cities and crops from MySQL database and store them in a dictionary.
     - The keys of the dictionary are the city names and the values are the respective data frames for each city.
     - The data frames contain the data for all crops in the respective cities.
    """

    df = retrieve_data_from_db()

    # Change date type
    df['date'] = pd.to_datetime(df['date'])

    # Get unique cities
    unique_cities = df['city'].unique()

    # Initiate empty dictionary to store data frames according to cities
    df_all_cities = {}

    # Save respective cities in dictionary
    for city in unique_cities:
        df_all_cities.update({city: df[df['city'] == city]})

    return df_all_cities

# Function to perform city-specific forecast using ARIMA and SARIMA models


def city_specific_forecast(df_all_cities: dict = all_cities_and_crops(),
                           city_name: str = city) -> str:
    """
    Perform city-specific forecast using ARIMA and SARIMA models.

    Parameters:
    df_all_cities (dict): A dictionary containing data frames for each city.
    city_name (str): The name of the city for which to perform the forecast.

    Returns:
    best_model (str): The name of the best model based on error metrics.
    """

    # Find the data frame for the specified city
    city_df = df_all_cities[city_name]

    # Drop city, latitude, and longitude
    city_df = city_df.drop(
        ['city', 'latitude', 'longitude', 'year', 'month'], axis=1)

    # Set date as index (ARIMA)
    city_df = city_df.set_index('date')

    # Remove duplicate index by using tilde
    city_df = city_df[~city_df.index.duplicated(keep='first')]

    # Resample to monthly frequency and take the mean
    city_monthly = city_df.resample('M').mean()

    # Interpolate if target has missing values
    city_monthly['cedi_price/(KG)'] = city_monthly['cedi_price/(KG)'].interpolate()

    # Set target as y
    y = city_monthly['cedi_price/(KG)']

    # Train and test split (80% train, 20% test)
    train_size = int(len(city_monthly) * 0.8)
    train = city_monthly[:train_size]
    test = city_monthly[train_size:]

    # Finding the best parameters (p, d, q, s) for ARIMA and/or SARIMA models

    # Option 1: Dynamic ARIMA
    p1, d1, q1 = dynamic_order(y)

    # Option 2: Best ARIMA
    p2, d2, q2 = find_best_arima(y, find_d(y))[0]

    # Option 3: SARIMA
    s = find_s(y)

    # Create a dictionary to store the model parameters for both approaches
    model_dictionary = dict(
        zip(["Dynamic ARIMA", "Best ARIMA"], [(p1, d1, q1), (p2, d2, q2)]))

    # Fit ARIMA model with dynamic order and best order, then compare their performance on the test set using MAE and RMSE.
    error_metrics = {}

    for approach, (p, d, q) in model_dictionary.items():

        model = ARIMA(train, order=(p, d, q))
        result = model.fit()

        forecast = result.forecast(steps=len(test))

        mae = round(mean_absolute_error(test, forecast), 4)
        rmse = round(np.sqrt(mean_squared_error(test, forecast)), 4)

        error_metrics[approach] = {"MAE": mae, "RMSE": rmse}

    # Choose best model based on better error metrics.
    if error_metrics.get("Dynamic ARIMA").get("MAE") < error_metrics.get("Best ARIMA").get("MAE") or (error_metrics.get("Dynamic ARIMA").get("MAE") == error_metrics.get("Best ARIMA").get("MAE") and error_metrics.get("Dynamic ARIMA").get("RMSE") < error_metrics.get("Best ARIMA").get("RMSE")):
        p, d, q = model_dictionary.get("Dynamic ARIMA")
        best_model = ARIMA(model_dictionary.get("Dynamic ARIMA"))

        # If the seasonal period is greater than 12, fit a SARIMA model instead of ARIMA
        if find_s(y) >= 12:
            best_model = SARIMAX(train, order=(p, d, q),
                                 seasonal_order=(p, d, q, find_s(y)))

    else:
        p, d, q = model_dictionary.get("Best ARIMA")
        best_model = ARIMA(model_dictionary.get("Best ARIMA"))

        # If the seasonal period is greater than 12, fit a SARIMA model instead of ARIMA
        if find_s(y) >= 12:
            best_model = SARIMAX(train, order=(p, d, q),
                                 seasonal_order=(p, d, q, find_s(y)))

    # Dump best model
    with open('models/best_model.pkl', 'wb') as f:
        pickle.dump(best_model, f)

    return best_model


if __name__ == '__main__':
    city_specific_forecast()
