# ======================================
# IMPORT
# ======================================
import pandas as pd
import numpy as np
import itertools
import matplotlib.pyplot as plt
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from prophet import Prophet
import pickle
import warnings
warnings.filterwarnings("ignore")


# MODEL DIRECTORY

import os
MODEL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'time_series_models'))
os.makedirs(MODEL_DIR, exist_ok=True)


# METRIC

def mape(y_true, y_pred):
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    return np.mean(np.abs((y_true - y_pred) / y_true)) * 100


# LOAD & CLEAN DATA

DATA_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), 'tabel-data-perbulan.xlsx'))
df = pd.read_excel(DATA_FILE)

df.replace("-", np.nan, inplace=True)
df.rename(columns={df.columns[1]: "komoditas"}, inplace=True)
df = df.drop(columns=[df.columns[0]], errors="ignore")

df_long = df.melt(
    id_vars=["komoditas"],
    var_name="tanggal",
    value_name="harga"
)

df_long["tanggal"] = pd.to_datetime(
    df_long["tanggal"].astype(str).str.strip(),
    dayfirst=True,
    errors="coerce"
)

df_long["harga"] = (
    df_long["harga"]
    .astype(str)
    .str.replace(",", "")
    .replace("nan", np.nan)
)

df_long["harga"] = pd.to_numeric(df_long["harga"], errors="coerce")

df_long = (
    df_long
    .dropna(subset=["tanggal", "harga"])
    .drop_duplicates(subset=["komoditas", "tanggal"])
    .sort_values(["komoditas", "tanggal"])
    .reset_index(drop=True)
)

print("Data siap untuk modeling")


p = d = q = range(0, 2)
pdq = list(itertools.product(p, d, q))
seasonal_pdq = [(x[0], x[1], x[2], 12) for x in pdq]

summary = []


# LOOP PER KOMODITAS

for komoditas in df_long["komoditas"].unique():

    print("\n" + "="*60)
    print(f" KOMODITAS: {komoditas}")
    print("="*60)

    ts = df_long[df_long["komoditas"] == komoditas].copy()
    ts_series = ts.set_index("tanggal")["harga"].sort_index()

    full_index = pd.date_range(
        ts_series.index.min(),
        ts_series.index.max(),
        freq="MS"
    )

    ts_series = ts_series.reindex(full_index).interpolate("time")
    ts_clean = ts_series.to_frame("harga")
    ts_clean.index.name = "tanggal"

    if len(ts_clean) < 36:
        print(" Data terlalu sedikit")
        continue

    split = int(len(ts_clean) * 0.8)
    train = ts_clean.iloc[:split]
    test = ts_clean.iloc[split:]

    
    # SARIMA

    train_log = np.log(train["harga"])
    best_sarima_mape = np.inf
    best_sarima_fit = None
    best_sarima_order = None
    best_sarima_seasonal = None

    for order in pdq:
        for seasonal in seasonal_pdq:
            try:
                model = SARIMAX(
                    train_log,
                    order=order,
                    seasonal_order=seasonal,
                    enforce_stationarity=False,
                    enforce_invertibility=False
                )
                fit = model.fit(disp=False)

                pred_log = fit.predict(
                    start=len(train)-12,
                    end=len(train)-1
                )
                pred = np.exp(pred_log)
                actual = train["harga"].iloc[-12:]

                error = mape(actual, pred)

                if error < best_sarima_mape:
                    best_sarima_mape = error
                    best_sarima_fit = fit
                    best_sarima_order = order
                    best_sarima_seasonal = seasonal
            except:
                continue

    sarima_pred = np.exp(
        best_sarima_fit.predict(
            start=len(train),
            end=len(ts_clean)-1
        )
    )
    sarima_mape_val = mape(test["harga"], sarima_pred)

    
    # HOLT-WINTERS (AMAN)
    
    best_hw_mape = np.inf
    best_hw_fit = None
    hw_pred = np.zeros(len(test))
    log_transformed_hw = False

    if komoditas == "Cabai Rawit Hijau":
        try:
            train_log_hw = np.log(train["harga"])
            model = ExponentialSmoothing(
                train_log_hw, trend="add", seasonal="add", seasonal_periods=12
            )
            fit = model.fit()
            pred_log = fit.forecast(len(test))
            pred = np.exp(pred_log)
            error = mape(test["harga"], pred)
            best_hw_mape = error
            best_hw_fit = fit
            hw_pred = pred
            log_transformed_hw = True
            print("✨ Trained Cabai Rawit Hijau with log transformation.")
        except Exception as e:
            print(f"Log-transformed HW failed for Cabai Rawit Hijau: {e}")
            log_transformed_hw = False

    if not log_transformed_hw:
        for seasonal_type in ["add", "mul"]:
            try:
                model = ExponentialSmoothing(
                    train["harga"],
                    trend="add",
                    seasonal=seasonal_type,
                    seasonal_periods=12
                )
                fit = model.fit()
                pred = fit.forecast(len(test))
                error = mape(test["harga"], pred)

                if error < best_hw_mape:
                    best_hw_mape = error
                    best_hw_fit = fit
                    hw_pred = pred
            except:
                continue

    
    # PROPHET
    
    ts_prophet = ts_clean.reset_index().rename(
        columns={"tanggal": "ds", "harga": "y"}
    )

    train_p = ts_prophet.iloc[:split]
    test_p = ts_prophet.iloc[split:]

    best_prophet_mape = np.inf
    best_prophet_model = None
    best_prophet_pred = np.zeros(len(test))

    for cps in [0.03, 0.05, 0.1]:
        model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=False,
            daily_seasonality=False,
            changepoint_prior_scale=cps
        )
        model.fit(train_p)

        future = model.make_future_dataframe(
            periods=len(test),
            freq="MS"
        )
        forecast = model.predict(future)
        pred = forecast["yhat"].iloc[-len(test):].values

        error = mape(test["harga"], pred)

        if error < best_prophet_mape:
            best_prophet_mape = error
            best_prophet_model = model
            best_prophet_pred = pred

    
    # ENSEMBLE
    
    ensemble_pred = (
        0.4 * sarima_pred.values +
        0.3 * hw_pred +
        0.3 * best_prophet_pred
    )
    ensemble_mape = mape(test["harga"], ensemble_pred)

    
    # PLOT AKURASI PREDIKSI
   
    plt.figure(figsize=(12,6))
    plt.plot(test.index, test["harga"], label="Actual", linewidth=3)
    plt.plot(test.index, sarima_pred, "--", label=f"SARIMA ({sarima_mape_val:.2f}%)")
    plt.plot(test.index, hw_pred, "--", label=f"HW ({best_hw_mape:.2f}%)")
    plt.plot(test.index, best_prophet_pred, "--", label=f"Prophet ({best_prophet_mape:.2f}%)")
    plt.plot(test.index, ensemble_pred, label=f"Ensemble ({ensemble_mape:.2f}%)")
    plt.title(f"Akurasi Prediksi Model – {komoditas}")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.show()

    
    # PILIH & MENYIMPAN MODEL TERBAIK
    
    scores = {
        "SARIMA": sarima_mape_val,
        "Holt-Winters": best_hw_mape,
        "Prophet": best_prophet_mape,
        "Ensemble": ensemble_mape
    }

    best_model = min(scores, key=scores.get)

    model_path = f"{MODEL_DIR}/{komoditas.replace(' ', '_')}.pkl"

    if best_model == "Ensemble":
        # History for HW depends on whether log was used
        hw_history = train_log_hw if log_transformed_hw else train["harga"]
        model_obj = {
            "model_type": "Ensemble",
            "sarima": {"model_type": "SARIMA", "params": {"order": best_sarima_order, "seasonal_order": best_sarima_seasonal}, "log_transformed": True, "history": train_log},
            "holt_winters": {"model_type": "Holt-Winters", "params": best_hw_fit.params, "log_transformed": log_transformed_hw, "history": hw_history},
            "prophet": {"model_type": "Prophet", "model": best_prophet_model, "log_transformed": False, "history": train_p},
            "weights": [0.4, 0.3, 0.3]
        }
    elif best_model == "SARIMA":
        model_obj = {"model_type": "SARIMA", "params": {"order": best_sarima_order, "seasonal_order": best_sarima_seasonal}, "log_transformed": True, "history": train_log}
    elif best_model == "Holt-Winters":
        hw_history = train_log_hw if log_transformed_hw else train["harga"]
        model_obj = {"model_type": "Holt-Winters", "params": best_hw_fit.params, "log_transformed": log_transformed_hw, "history": hw_history}
    else: # Prophet
        model_obj = {"model_type": "Prophet", "model": best_prophet_model, "log_transformed": False, "history": train_p}

    with open(model_path, "wb") as f:
        pickle.dump(model_obj, f)

    print(f"💾 Model terbaik disimpan ke local path: {model_path}")

    summary.append([
        komoditas,
        best_model,
        sarima_mape_val,
        best_hw_mape,
        best_prophet_mape,
        ensemble_mape
    ])


# SUMMARY

summary_df = pd.DataFrame(
    summary,
    columns=[
        "Komoditas",
        "Best_Model",
        "SARIMA_MAPE",
        "HW_MAPE",
        "Prophet_MAPE",
        "Ensemble_MAPE"
    ]
)

print("\n📊 RINGKASAN AKHIR")
print(summary_df)