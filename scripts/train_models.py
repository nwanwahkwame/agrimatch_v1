# train_models.py
# ─────────────────────────────────────────────────────────────────────────────
# Train ARIMA or SARIMA models per region-crop table and save FITTED results.
# Handles seasonal periods of any size robustly with progressive fallbacks.
# ─────────────────────────────────────────────────────────────────────────────

import os
import pickle
import warnings
from itertools import product
from pathlib import Path

import mysql.connector
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sqlalchemy import create_engine
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.stattools import acf, adfuller, kpss, pacf
from statsmodels.tools.sm_exceptions import ConvergenceWarning

warnings.filterwarnings("ignore", category=ConvergenceWarning)
warnings.filterwarnings("ignore", category=UserWarning)

load_dotenv()

MODEL_DIR = Path("models")
MODEL_DIR.mkdir(exist_ok=True)

PRICE_COL = "cedi_price/(KG)"

# Minimum observations required per model type.
# SARIMAX needs at least 2 full seasonal cycles to estimate seasonal params.
MIN_OBS_ARIMA = 24
MIN_OBS_SARIMA_MULTIPLIER = 2   # need >= 2 * s observations


# ─────────────────────────────────────────────────────────────────────────────
# Seasonal differencing order
# ─────────────────────────────────────────────────────────────────────────────

def find_seasonal_d(series: pd.Series, s: int, alpha: float = 0.05) -> int:
    """
    Determine seasonal differencing order (D) for a given period s.
    Tests whether the seasonally-differenced series is stationary.
    Returns 0 or 1 — higher seasonal differencing is rarely beneficial.
    """
    if s <= 1:
        return 0

    # Test original series for seasonal unit root via KPSS
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            kpss_stat, kpss_p, *_ = kpss(series.dropna(), regression="c",
                                         nlags=max(1, len(series) // 4))
        if kpss_p > alpha:
            # Already stationary — no seasonal differencing needed
            return 0
    except Exception:
        pass

    # Apply one seasonal difference and re-test
    try:
        s_diff = series.diff(s).dropna()
        if len(s_diff) < 10:
            return 0
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            kpss_stat, kpss_p, *_ = kpss(s_diff, regression="c",
                                         nlags=max(1, len(s_diff) // 4))
        return 0 if kpss_p > alpha else 1
    except Exception:
        return 0


# ─────────────────────────────────────────────────────────────────────────────
# Seasonal order grid search
# ─────────────────────────────────────────────────────────────────────────────

def find_best_sarima_seasonal_order(
    train: pd.Series,
    p: int, d: int, q: int,
    s: int,
    P_range=(0, 1),
    Q_range=(0, 1),
) -> tuple:
    """
    Grid-search seasonal (P, D, Q) for a fixed (p,d,q,s).
    D is determined analytically; P and Q are searched over small ranges
    to keep training fast and avoid over-parameterisation with large s.

    Returns the best (P, D, Q) tuple found, or (1, 0, 0) as a safe default.
    """
    D = find_seasonal_d(train, s)
    best_aic = float("inf")
    best_order = (1, D, 0)   # safe default if nothing converges

    for P, Q in product(P_range, Q_range):
        # Skip (0,0,0) — that's just ARIMA, already evaluated separately
        if P == 0 and Q == 0:
            continue
        try:
            result = SARIMAX(
                train,
                order=(p, d, q),
                seasonal_order=(P, D, Q, s),
                enforce_stationarity=False,
                enforce_invertibility=False,
            ).fit(disp=False)
            if result.aic < best_aic:
                best_aic = result.aic
                best_order = (P, D, Q)
        except Exception:
            continue

    return best_order


# ─────────────────────────────────────────────────────────────────────────────
# Robust model fitter with progressive fallback
# ─────────────────────────────────────────────────────────────────────────────

def fit_best_model(train: pd.Series, p: int, d: int, q: int, s: int):
    """
    Attempt to fit models in preference order, falling back gracefully:

      Level 1 — SARIMAX with grid-searched (P, D, Q, s)
                 Requires >= 2*s observations.
      Level 2 — SARIMAX with minimal seasonal order (1, D, 1, s)
                 Still requires >= 2*s observations.
      Level 3 — SARIMAX with (1, 0, 0, s)  [AR-only seasonal, no differencing]
                 More lenient data requirement.
      Level 4 — Plain ARIMA(p, d, q)  [ignores seasonality]
      Level 5 — ARIMA(1, 1, 0)        [simplest possible model, last resort]

    Each level is tried; on any exception we drop down to the next.
    Returns (fitted_results, description_string).
    """
    n = len(train)
    use_sarima = s > 1 and n >= MIN_OBS_SARIMA_MULTIPLIER * s

    # ── Level 1: SARIMAX with searched seasonal order ─────────────────────────
    if use_sarima:
        try:
            P, D, Q = find_best_sarima_seasonal_order(train, p, d, q, s)
            fitted = SARIMAX(
                train,
                order=(p, d, q),
                seasonal_order=(P, D, Q, s),
                enforce_stationarity=False,
                enforce_invertibility=False,
            ).fit(disp=False)
            return fitted, f"SARIMAX({p},{d},{q})×({P},{D},{Q})[{s}]"
        except Exception as e:
            print(f"      Level 1 SARIMAX failed ({e}) — trying Level 2.")

    # ── Level 2: SARIMAX with minimal seasonal order ──────────────────────────
    if use_sarima:
        try:
            D = find_seasonal_d(train, s)
            fitted = SARIMAX(
                train,
                order=(p, d, q),
                seasonal_order=(1, D, 1, s),
                enforce_stationarity=False,
                enforce_invertibility=False,
            ).fit(disp=False)
            return fitted, f"SARIMAX({p},{d},{q})×(1,{D},1)[{s}]"
        except Exception as e:
            print(f"      Level 2 SARIMAX failed ({e}) — trying Level 3.")

    # ── Level 3: SARIMAX AR-only seasonal (no seasonal differencing) ──────────
    if s > 1 and n >= s + 10:   # relaxed data requirement
        try:
            fitted = SARIMAX(
                train,
                order=(p, d, q),
                seasonal_order=(1, 0, 0, s),
                enforce_stationarity=False,
                enforce_invertibility=False,
            ).fit(disp=False)
            return fitted, f"SARIMAX({p},{d},{q})×(1,0,0)[{s}]"
        except Exception as e:
            print(f"      Level 3 SARIMAX failed ({e}) — trying Level 4.")

    # ── Level 4: plain ARIMA ───────────────────────────────────────────────────
    try:
        fitted = ARIMA(train, order=(p, d, q)).fit()
        return fitted, f"ARIMA({p},{d},{q})"
    except Exception as e:
        print(f"      Level 4 ARIMA failed ({e}) — trying Level 5 (fallback).")

    # ── Level 5: simplest possible model ─────────────────────────────────────
    fitted = ARIMA(train, order=(1, 1, 0)).fit()
    return fitted, "ARIMA(1,1,0) [fallback]"


# ─────────────────────────────────────────────────────────────────────────────
# Main training loop
# ─────────────────────────────────────────────────────────────────────────────

def train_region_crop_models():
    """
    For every table in the database:
      1. Load and clean the data.
      2. Find best ARIMA order using two strategies; pick the lower-MAE one.
      3. Detect seasonal period s; select appropriate SARIMA or ARIMA.
      4. Fit with progressive fallback so no table is ever skipped due to
         large s or insufficient data.
      5. Save the FITTED results object to disk.
    """
    n = 0

    try:
        HOST = os.getenv("DB_HOST")
        USERNAME = os.getenv("DB_USERNAME")
        PASSWORD = os.getenv("DB_PASSWORD")
        DATABASE = os.getenv("DB_DATABASE")
        PORT = os.getenv("DB_PORT", "3306")

        connection = mysql.connector.connect(
            host=HOST, user=USERNAME, password=PASSWORD, database=DATABASE
        )
        engine = create_engine(
            f"mysql+pymysql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"
        )
        cursor = connection.cursor()
        cursor.execute("SHOW TABLES")
        table_names = [row[0] for row in cursor.fetchall()]

        print(f"Found {len(table_names)} table(s).\n")

        for name in table_names:
            print(f"── Training: {name}")

            try:
                # ── Load & clean ──────────────────────────────────────────────
                df = pd.read_sql(f"SELECT * FROM `{name}`", engine)
                df["date"] = pd.to_datetime(df["date"])

                drop_cols = [c for c in
                             ["city", "latitude", "longitude", "year", "month"]
                             if c in df.columns]
                df = df.drop(columns=drop_cols)
                df = df.drop_duplicates("date")
                df["date"] = df["date"] - pd.Timedelta(days=14)
                df = df.set_index("date").sort_index().asfreq("MS")

                if PRICE_COL not in df.columns:
                    print(
                        f"   ⚠  Column '{PRICE_COL}' not found — skipping.\n")
                    continue

                df[PRICE_COL] = df[PRICE_COL].interpolate()
                y = df[PRICE_COL].astype(float)

                if len(y) < MIN_OBS_ARIMA:
                    print(
                        f"   ⚠  Only {len(y)} rows — need {MIN_OBS_ARIMA} minimum. Skipping.\n")
                    continue

                # ── Train / test split ────────────────────────────────────────
                split = int(len(y) * 0.8)
                train, test = y.iloc[:split], y.iloc[split:]

                # ── Detect seasonal period ────────────────────────────────────
                s = find_s(y)
                print(f"   Seasonal period detected: s={s} "
                      f"({'will use SARIMA' if s > 1 and len(train) >= MIN_OBS_SARIMA_MULTIPLIER * s else 'ARIMA (insufficient data for SARIMA)' if s > 1 else 'no seasonality → ARIMA'})")

                # ── Find best non-seasonal order ──────────────────────────────
                p1, d1, q1 = dynamic_order(y)

                best_order_2 = find_best_arima(train, find_d(y))
                p2, d2, q2 = best_order_2 if best_order_2 else (p1, d1, q1)

                def eval_order(p, d, q):
                    try:
                        res = ARIMA(train, order=(p, d, q)).fit()
                        fc = res.forecast(steps=len(test))
                        return (round(mean_absolute_error(test, fc), 4),
                                round(np.sqrt(mean_squared_error(test, fc)), 4))
                    except Exception:
                        return float("inf"), float("inf")

                mae1, rmse1 = eval_order(p1, d1, q1)
                mae2, rmse2 = eval_order(p2, d2, q2)

                print(
                    f"   Dynamic ARIMA({p1},{d1},{q1})  MAE={mae1}  RMSE={rmse1}")
                print(
                    f"   Best    ARIMA({p2},{d2},{q2})  MAE={mae2}  RMSE={rmse2}")

                if (mae1, rmse1) <= (mae2, rmse2):
                    p, d, q = p1, d1, q1
                else:
                    p, d, q = p2, d2, q2

                print(f"   → Non-seasonal order chosen: ({p},{d},{q})")

                # ── Fit with progressive fallback ─────────────────────────────
                fitted, model_desc = fit_best_model(train, p, d, q, s)
                print(f"   ✔  Fitted: {model_desc}")

                # ── Save fitted results ───────────────────────────────────────
                out_path = MODEL_DIR / f"{name.lower()}.pkl"
                with open(out_path, "wb") as f:
                    pickle.dump(fitted, f)

                print(f"   ✅ Saved → {out_path}\n")
                n += 1

            except Exception as e:
                print(f"   ❌ Unexpected failure for '{name}': {e}\n")
                continue

    except mysql.connector.Error as error:
        print(f"Database connection failed: {error}")

    finally:
        if "cursor" in locals():
            cursor.close()
        if "connection" in locals() and connection.is_connected():
            connection.close()

    print(f"{n} model(s) trained and saved to '{MODEL_DIR}/'.")
    return "Done. ✅"


# ─────────────────────────────────────────────────────────────────────────────
# Order-finding helpers
# ─────────────────────────────────────────────────────────────────────────────

def find_d(series: pd.Series, max_diff: int = 2, alpha: float = 0.05,
           min_samples: int = 20, nlags: int = 8) -> int:
    """Minimum differencing order via ADF + KPSS."""
    series = series.dropna()
    if series.nunique() <= 1:
        return 0

    temp = series.copy()
    for d in range(max_diff + 1):
        if len(temp) < min_samples:
            break
        safe_nlags = max(0, min(nlags, len(temp) // 2 - 1))
        current_nlags = safe_nlags
        while current_nlags >= 0:
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    adf_p = adfuller(temp, autolag="AIC")[1]
                    kpss_p = kpss(temp, regression="c", nlags=current_nlags)[1]
                if adf_p < alpha and kpss_p > alpha:
                    return d
                break
            except Exception:
                current_nlags -= 1
        temp = temp.diff().dropna()
    return max_diff


def find_p(series: pd.Series, nlags: int = 8) -> int:
    """AR order (p) from PACF."""
    d = find_d(series)
    series = series.diff(d).dropna() if d > 0 else series.dropna()
    N = len(series)
    if N < 3:
        return 0
    safe_nlags = max(1, min(nlags, N // 2 - 1))
    while safe_nlags >= 1:
        try:
            vals = pacf(series, nlags=safe_nlags)
            limit = 1.96 / np.sqrt(N)
            sig = [i for i, v in enumerate(vals[1:], 1) if abs(v) > limit]
            return max(sig) if sig else 0
        except Exception:
            safe_nlags -= 1
    return 0


def find_q(series: pd.Series, nlags: int = 8) -> int:
    """MA order (q) from ACF."""
    d = find_d(series)
    series = series.diff(d).dropna() if d > 0 else series.dropna()
    N = len(series)
    if N < 3:
        return 0
    safe_nlags = max(1, min(nlags, N // 2 - 1))
    while safe_nlags >= 1:
        try:
            vals = acf(series, nlags=safe_nlags)
            limit = 1.96 / np.sqrt(N)
            sig = [i for i, v in enumerate(vals[1:], 1) if abs(v) > limit]
            return max(sig) if sig else 0
        except Exception:
            safe_nlags -= 1
    return 0


def dynamic_order(y: pd.Series) -> tuple:
    """Return (p, d, q) from ACF/PACF."""
    return find_p(y), find_d(y), find_q(y)


def find_best_arima(series: pd.Series, d: int,
                    p_range=range(0, 5), q_range=range(0, 5)):
    """
    Grid-search (p, q) for lowest AIC with fixed d.
    Returns best (p, d, q) or None if nothing converged.
    """
    best_aic = float("inf")
    best_order = None
    for p, q in product(p_range, q_range):
        try:
            result = ARIMA(series, order=(p, d, q)).fit()
            if result.aic < best_aic:
                best_aic = result.aic
                best_order = (p, d, q)
        except Exception:
            continue
    return best_order


def find_s(series: pd.Series, max_seasonal_period: int = 24) -> int:
    """
    Detect the dominant seasonal period from the ACF.

    Strategy: find all significant ACF lags, then identify the smallest
    lag >= 2 that also has a harmonic (2× or 3× the lag) present —
    this distinguishes a true seasonal period from short-range autocorrelation.
    Falls back to the first significant lag if no harmonic pattern is found.
    Returns 0 if no significant periodicity exists.
    """
    series = series.dropna()
    N = len(series)
    if N < 3:
        return 0

    safe_nlags = max(1, min(max_seasonal_period, N // 2 - 1))

    while safe_nlags >= 1:
        try:
            vals = acf(series, nlags=safe_nlags)
            limit = 1.96 / np.sqrt(N)

            # All lags with significant autocorrelation (skip lag 0)
            sig_lags = {i for i, v in enumerate(vals[1:], 1) if abs(v) > limit}

            if not sig_lags:
                return 0

            # Prefer a lag that has at least one harmonic also significant
            # — this is the hallmark of true periodicity
            candidates = sorted(sig_lags)
            for lag in candidates:
                if lag < 2:
                    continue
                has_harmonic = any(
                    (lag * k) in sig_lags
                    for k in (2, 3)
                    if lag * k <= safe_nlags
                )
                if has_harmonic:
                    return lag

            # No harmonic found — return smallest significant lag >= 2
            for lag in candidates:
                if lag >= 2:
                    return lag

            return 0

        except Exception:
            safe_nlags -= 1

    return 0


# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    train_region_crop_models()
