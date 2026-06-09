"""
prophet_training.py

Sequential Prophet training pipeline for MySQL crop_database.
- Discovers all tables
- Automatic seasonality detection
- Hyperparameter tuning via grid search
- Model + metadata export (.pkl / .json)
- Single public function: train_all_prophet_models()
"""


def train_all_prophet_models():
    import os
    import json
    import pickle
    import warnings
    import numpy as np
    import pandas as pd

    from pathlib import Path
    from itertools import product

    from prophet import Prophet
    from sklearn.metrics import mean_absolute_error, mean_squared_error
    from sqlalchemy import create_engine, inspect

    warnings.filterwarnings("ignore")

    # ------------------------------------------------------------------ #
    # Configuration                                                        #
    # ------------------------------------------------------------------ #
    DB_USERNAME = os.getenv("DB_USERNAME")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST     = os.getenv("DB_HOST")
    DB_PORT     = os.getenv("DB_PORT")
    DB_DATABASE = os.getenv("DB_DATABASE")

    TARGET_COLUMN = "cedi_price/(KG)"

    MODEL_DIR      = Path("models")
    MODEL_DIR_META = Path("meta")

    # FIX 1: both output directories must exist before any table is trained
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    MODEL_DIR_META.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------ #
    # Database connection                                                  #
    # ------------------------------------------------------------------ #
    engine = create_engine(
        f"mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}"
        f"@{DB_HOST}:{DB_PORT}/{DB_DATABASE}"
    )

    inspector = inspect(engine)
    tables    = inspector.get_table_names()

    print(f"Discovered {len(tables)} tables")

    # ------------------------------------------------------------------ #
    # Per-table training function                                          #
    # ------------------------------------------------------------------ #
    def train_table(table_name):

        # --- load -------------------------------------------------------
        df = pd.read_sql(f"SELECT * FROM `{table_name}`", engine)

        required = {"year", "month", TARGET_COLUMN}
        missing  = required - set(df.columns)
        if missing:
            raise ValueError(
                f"{table_name}: missing required columns {missing}"
            )

        df = df.copy()

        # --- clean target -----------------------------------------------
        df[TARGET_COLUMN] = pd.to_numeric(df[TARGET_COLUMN], errors="coerce")

        # FIX 2: avoid deprecated chained interpolate/bfill/ffill on Series;
        # interpolate in-place then fill remaining NaNs explicitly
        df[TARGET_COLUMN] = df[TARGET_COLUMN].interpolate(method="linear")
        df[TARGET_COLUMN] = df[TARGET_COLUMN].bfill().ffill()

        # --- clean date columns -----------------------------------------
        df["year"]  = pd.to_numeric(df["year"],  errors="coerce")
        df["month"] = pd.to_numeric(df["month"], errors="coerce")

        df = df.dropna(subset=["year", "month", TARGET_COLUMN])

        df["year"]  = df["year"].astype(int)
        df["month"] = df["month"].astype(int)

        df["ds"] = pd.to_datetime(
            df["year"].astype(str) + "-" + df["month"].astype(str) + "-01"
        )

        # --- build Prophet dataframe ------------------------------------
        prophet_df = (
            df[["ds", TARGET_COLUMN]]
            .rename(columns={TARGET_COLUMN: "y"})
            .drop_duplicates(subset=["ds"])
            .sort_values("ds")
            .reset_index(drop=True)
        )

        if len(prophet_df) < 6:
            raise ValueError(
                f"{table_name}: insufficient observations ({len(prophet_df)})"
            )

        # --- seasonality flags ------------------------------------------
        n_months = len(prophet_df)

        yearly    = n_months >= 24
        quarterly = n_months >= 12
        monthly   = n_months >= 6

        # --- train / test split -----------------------------------------
        if n_months > 24:
            test_size = 12
        elif n_months > 12:
            test_size = 6
        else:
            test_size = 3

        train_df = prophet_df.iloc[:-test_size]
        test_df  = prophet_df.iloc[-test_size:]

        # --- hyperparameter grid search ---------------------------------
        cp_scales = [0.01, 0.05, 0.1, 0.5]
        sp_scales = [1.0, 10.0]
        modes     = ["additive", "multiplicative"]

        best_rmse   = np.inf
        best_params = None

        for cp, sp, mode in product(cp_scales, sp_scales, modes):
            try:
                model = Prophet(
                    yearly_seasonality=yearly,
                    weekly_seasonality=False,
                    daily_seasonality=False,
                    seasonality_mode=mode,
                    changepoint_prior_scale=cp,
                    seasonality_prior_scale=sp,
                )

                if quarterly:
                    model.add_seasonality(
                        name="quarterly", period=91.25, fourier_order=5
                    )
                if monthly:
                    model.add_seasonality(
                        name="monthly", period=30.5, fourier_order=3
                    )

                model.fit(train_df)

                future   = model.make_future_dataframe(periods=test_size, freq="MS")
                forecast = model.predict(future)

                preds  = forecast["yhat"].tail(test_size).values
                actual = test_df["y"].values
                rmse   = np.sqrt(mean_squared_error(actual, preds))

                if rmse < best_rmse:
                    best_rmse   = rmse
                    best_params = {
                        "changepoint_prior_scale": cp,
                        "seasonality_prior_scale": sp,
                        "seasonality_mode": mode,
                    }

            except Exception:
                # a single bad config is skipped; the loop continues
                continue

        if best_params is None:
            raise RuntimeError(
                f"{table_name}: no configuration could be fitted"
            )

        # --- final model trained on full data ---------------------------
        final_model = Prophet(
            yearly_seasonality=yearly,
            weekly_seasonality=False,
            daily_seasonality=False,
            seasonality_mode=best_params["seasonality_mode"],
            changepoint_prior_scale=best_params["changepoint_prior_scale"],
            seasonality_prior_scale=best_params["seasonality_prior_scale"],
        )

        if quarterly:
            final_model.add_seasonality(
                name="quarterly", period=91.25, fourier_order=5
            )
        if monthly:
            final_model.add_seasonality(
                name="monthly", period=30.5, fourier_order=3
            )

        final_model.fit(prophet_df)

        # --- persist model ----------------------------------------------
        model_path = MODEL_DIR / f"{table_name}.pkl"
        with open(model_path, "wb") as f:
            pickle.dump(final_model, f)

        # --- in-sample metrics ------------------------------------------
        forecast = final_model.predict(prophet_df[["ds"]])

        mae  = mean_absolute_error(prophet_df["y"], forecast["yhat"])
        rmse = np.sqrt(mean_squared_error(prophet_df["y"], forecast["yhat"]))
        mape = np.mean(
            np.abs(
                (prophet_df["y"] - forecast["yhat"])
                / np.maximum(np.abs(prophet_df["y"]), 1e-8)
            )
        ) * 100

        metadata = {
            "table":                table_name,
            "rows":                 int(len(prophet_df)),
            "mae":                  float(mae),
            "rmse":                 float(rmse),
            "mape":                 float(mape),
            "yearly_seasonality":   yearly,
            "quarterly_seasonality": quarterly,
            "monthly_seasonality":  monthly,
            **best_params,
        }

        meta_path = MODEL_DIR_META / f"{table_name}_meta.json"
        with open(meta_path, "w") as f:
            json.dump(metadata, f, indent=4)

        return metadata

    # ------------------------------------------------------------------ #
    # FIX 3: sequential loop replacing Parallel / delayed                 #
    # Each table is isolated in try/except so one failure never stops     #
    # the remaining 174 tables from training.                             #
    # ------------------------------------------------------------------ #
    results  = []
    failed   = []

    for i, table in enumerate(tables, start=1):
        print(f"[{i}/{len(tables)}] Training: {table}")
        try:
            meta = train_table(table)
            results.append(meta)
            print(
                f"  Done — MAE: {meta['mae']:.4f} | "
                f"RMSE: {meta['rmse']:.4f} | "
                f"MAPE: {meta['mape']:.2f}%"
            )
        except Exception as exc:
            # FIX 4: record the failure and move on rather than crashing
            print(f"  FAILED — {exc}")
            failed.append({"table": table, "error": str(exc)})

    # ------------------------------------------------------------------ #
    # Summary                                                             #
    # ------------------------------------------------------------------ #
    # FIX 5: results contains only successful dicts (no None entries),
    # so json.dump is always given a clean list
    summary = {
        "total_tables":    len(tables),
        "trained":         len(results),
        "failed":          len(failed),
        "failed_tables":   failed,
        "models":          results,
    }

    summary_file = MODEL_DIR / "training_summary.json"
    with open(summary_file, "w") as f:
        json.dump(summary, f, indent=4)

    print(f"\nTraining complete: {len(results)}/{len(tables)} models trained successfully")
    if failed:
        print(f"Failed tables ({len(failed)}): {[f['table'] for f in failed]}")
    print(f"Summary written to {summary_file}")


if __name__ == "__main__":
    train_all_prophet_models()
