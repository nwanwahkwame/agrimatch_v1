# Import relevant dependencies
import pandas as pd
import numpy as np

from sqlalchemy import create_engine
import mysql.connector

from statsmodels.tsa.stattools import acf, pacf, adfuller, kpss
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tools.sm_exceptions import ConvergenceWarning

from sklearn.metrics import mean_absolute_error, mean_squared_error
from itertools import product
import warnings
import pickle
import os

warnings.filterwarnings("ignore", category=ConvergenceWarning)


def train_region_crop_models():
    """
    Train ARIMA/SARIMA models based on p, d, q, s values.
    Dump best models to be deployed in streamlit.
    """

    # Number of trained models
    n = 0

    try:
        # 1. Database credentials
        HOST = os.getenv("DB_HOST")
        USERNAME = os.getenv("DB_USERNAME")
        PASSWORD = os.getenv("DB_PASSWORD")
        DATABASE = os.getenv("DB_DATABASE")
        PORT = os.getenv("DB_PORT")

        # 2. Establish the connection to the MySQL server
        connection = mysql.connector.connect(
            host=HOST,
            user=USERNAME,
            password=PASSWORD,
            database=DATABASE
        )

        # 3. SQLAlchemy connection
        connection_string = (
            f"mysql+pymysql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}")

        # 4. Create SQLAlchemy engine
        engine = create_engine(connection_string)

        # 5. Create a cursor object to execute SQL commands
        cursor = connection.cursor()

        # 6. Execute the command to list tables
        cursor.execute("SHOW TABLES")

        # 7. Fetch all rows from the executed command
        raw_tables = cursor.fetchall()

        # 8. Extract names from the returned tuples into a clean list
        table_names = [table[0] for table in raw_tables]

        # 9. Display the results
        print("Tables in the database:")

        # 10. Train city-specific model
        for name in table_names:
            region = name.rsplit('_', maxsplit=1)[0]
            crop = name.rsplit('_', maxsplit=1)[1]
            print(f'Region: {region}, Crop: {crop}')

            # SQL query
            if '(' in name or ')' in name:
                query = f"SELECT * FROM `{name}`;"

            else:
                query = f"SELECT * FROM {name};"

            # Region-crop dataframe
            df = pd.read_sql(query, engine)

            # Change date type
            df['date'] = pd.to_datetime(df['date'])

            # Drop city, latitude, longitude, year, and month
            df = df.drop(['city', 'latitude', 'longitude',
                         'year', 'month'], axis=1)

            # Drop duplicates after removing constraints
            df = df.drop_duplicates(['date'])

            # Subtract 14 days from every date in the column
            df['date'] = df['date'] - pd.Timedelta(days=14)

            # Set date as index (ARIMA)
            df = df.set_index('date')

            # Apply monthly frequency
            df_monthly = df.asfreq('MS')

            # Interpolate if target has missing values
            df_monthly['cedi_price/(KG)'] = df_monthly['cedi_price/(KG)'].interpolate()

            # Set target as y
            y = df_monthly['cedi_price/(KG)']

            # Train and test split (80% train, 20% test)
            train_size = int(len(df_monthly) * 0.8)
            train = df_monthly[:train_size]
            test = df_monthly[train_size:]

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
                rmse = round(
                    np.sqrt(mean_squared_error(test, forecast)), 4)

                error_metrics[approach] = {"MAE": mae, "RMSE": rmse}

            # Choose best model based on better error metrics.
            if error_metrics.get("Dynamic ARIMA").get("MAE") < error_metrics.get("Best ARIMA").get("MAE") or (error_metrics.get("Dynamic ARIMA").get("MAE") == error_metrics.get("Best ARIMA").get("MAE") and error_metrics.get("Dynamic ARIMA").get("RMSE") < error_metrics.get("Best ARIMA").get("RMSE")):
                p, d, q = model_dictionary.get("Dynamic ARIMA")
                best_model = ARIMA(model_dictionary.get("Dynamic ARIMA"))

                # If the seasonal period is greater than 12, fit a SARIMA model instead of ARIMA
                if find_s(y) >= 12:
                    best_model = SARIMAX(train, order=(p, d, q),
                                         seasonal_order=(p, d, q, s))

            else:
                p, d, q = model_dictionary.get("Best ARIMA")
                best_model = ARIMA(model_dictionary.get("Best ARIMA"))

                # If the seasonal period is greater than 12, fit a SARIMA model instead of ARIMA
                if find_s(y) >= 12:
                    best_model = SARIMAX(train, order=(p, d, q),
                                         seasonal_order=(p, d, q, find_s(y)))

            # Dump best model
            with open(f'models/{region.lower()}_{crop}.pkl', 'wb') as f:
                pickle.dump(best_model, f)

            n += 1

    except mysql.connector.Error as error:
        print(f"Failed to fetch tables: {error}")

    finally:
        # 10. Always clean up and close your connections
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals() and connection.is_connected():
            connection.close()

    print(f'{n} number of models trained.')
    return f'Done. ✅'

# Automating p, d, q: Option One

# 1. Automatically Determine d (Differencing Order)


def find_d(
    series: pd.Series,
    max_diff: int = 2,
    alpha: float = 0.05,
    min_samples: int = 20,
    nlags: int = 8
) -> int:
    """
    Determine the minimum differencing order (d)
    required to achieve stationarity using both
    ADF and KPSS tests.
    """

    series = series.dropna()

    if series.nunique() <= 1:
        return 0

    temp = series.copy()

    for d in range(max_diff + 1):

        if len(temp) < min_samples:
            break

        safe_nlags = max(
            0,
            min(nlags, len(temp) // 2 - 1)
        )

        current_nlags = safe_nlags

        while current_nlags >= 0:

            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")

                    adf_p = adfuller(
                        temp,
                        autolag="AIC"
                    )[1]

                    kpss_p = kpss(
                        temp,
                        regression="c",
                        nlags=current_nlags
                    )[1]

                if adf_p < alpha and kpss_p > alpha:
                    return d

                break

            except Exception:
                current_nlags -= 1

        temp = temp.diff().dropna()

    return max_diff


# 2. After differencing, automatically calculate PACF for p

def find_p(series: pd.Series, nlags: int = 8) -> int:
    """
    Determine AR order (p) using PACF.
    """

    d = find_d(series)

    if d > 0:
        series = series.diff(d).dropna()
    else:
        series = series.dropna()

    N = len(series)

    if N < 3:
        return 0

    # PACF requires nlags < nobs/2
    safe_nlags = max(
        1,
        min(nlags, N // 2 - 1)
    )

    current_nlags = safe_nlags

    while current_nlags >= 1:

        try:
            pacf_values = pacf(
                series,
                nlags=current_nlags
            )

            confidence_limit = 1.96 / np.sqrt(N)

            significant_p = [
                lag
                for lag, value in enumerate(
                    pacf_values[1:],
                    start=1
                )
                if abs(value) > confidence_limit
            ]

            return max(significant_p) if significant_p else 0

        except Exception:
            current_nlags -= 1

    return 0


# 3. Automatically Calculate ACF for q

def find_q(series: pd.Series, nlags: int = 8) -> int:

    d = find_d(series)

    if d > 0:
        series = series.diff(d).dropna()
    else:
        series = series.dropna()

    N = len(series)

    if N < 3:
        return 0

    safe_nlags = max(
        1,
        min(nlags, N // 2 - 1)
    )

    current_nlags = safe_nlags

    while current_nlags >= 1:

        try:
            acf_values = acf(
                series,
                nlags=current_nlags
            )

            confidence_limit = 1.96 / np.sqrt(N)

            significant_q = [
                lag
                for lag, value in enumerate(
                    acf_values[1:],
                    start=1
                )
                if abs(value) > confidence_limit
            ]

            return max(significant_q) if significant_q else 0

        except Exception:
            current_nlags -= 1

    return 0


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


def find_s(
    series: pd.Series,
    max_seasonal_period: int = 24
) -> int:

    series = series.dropna()

    N = len(series)

    if N < 3:
        return 0

    safe_nlags = max(
        1,
        min(max_seasonal_period, N // 2 - 1)
    )

    current_nlags = safe_nlags

    while current_nlags >= 1:

        try:
            acf_values = acf(
                series,
                nlags=current_nlags
            )

            confidence_limit = 1.96 / np.sqrt(N)

            significant_peaks = [
                lag
                for lag, value in enumerate(
                    acf_values[1:],
                    start=1
                )
                if abs(value) > confidence_limit
            ]

            return (
                min(significant_peaks)
                if significant_peaks
                else 0
            )

        except Exception:
            current_nlags -= 1

    return 0


if __name__ == '__main__':
    train_region_crop_models()
