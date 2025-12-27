import os
import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
from prophet import Prophet
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.api import ExponentialSmoothing
import numpy as np
from datetime import date
from dateutil.relativedelta import relativedelta
import logging

app = Flask(__name__)

CORS(app, resources={r"/api/*": {"origins": ["http://localhost:5173", "http://127.0.0.1:5173", "https://prediksi-harga-web.onrender.com", "https://prediksiharga-web.onrender.com"]}})
logging.basicConfig(level=logging.INFO)

MODELS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'time_series_models'))

def get_commodity_list():
    """Returns a list of available commodities by scanning the model directory."""
    try:
        commodities = [f.replace('.pkl', '').replace('_', ' ') for f in os.listdir(MODELS_DIR) if f.endswith('.pkl')]
        return commodities
    except Exception as e:
        app.logger.error(f"Error scanning model directory: {e}")
        return []

def get_last_date_in_model(model, model_type, model_info=None):
    """Extracts the last date from the model's training data by relying on the 'history' key."""
    app.logger.info(f"[get_last_date_in_model] Type: {model_type}")

    if model_info is None or 'history' not in model_info:
        raise ValueError(f"Cannot determine last training date: 'history' not found in model_info for model type {model_type}")

    history = model_info['history']
    if history is None or history.empty:
        raise ValueError(f"Cannot determine last training date: 'history' is None or empty for model type {model_type}")

    if model_type == 'Prophet':
        
        return pd.to_datetime(history['ds'].max())
    elif model_type in ['SARIMA', 'Holt-Winters']:
        
        return pd.to_datetime(history.index[-1])
    
    raise ValueError(f"Could not determine last date from history for model type {model_type}. Unexpected history format.")

def predict_single_model(model_info, months_to_predict):
    """Generates predictions from a single time series model."""
    model_type = model_info.get('model_type')
    log_transformed = model_info.get('log_transformed', False)
    history = model_info.get('history')

    if history is None or history.empty:
        raise ValueError(f"Cannot make prediction: 'history' is missing or empty for model type {model_type}")

    
    if model_type == 'SARIMA':
        params = model_info.get('params')
        if not params:
            raise ValueError("SARIMA model parameters are missing.")
        model = SARIMAX(history, order=params['order'], seasonal_order=params['seasonal_order'])
        model = model.fit(disp=False)
    elif model_type == 'Holt-Winters':
        params = model_info.get('params')
        if not params:
            raise ValueError("Holt-Winters model parameters are missing.")
        # Rekonstruksi parameter yang relevan
        trend = params.get('trend', 'add')
        seasonal = params.get('seasonal', 'add')
        seasonal_periods = params.get('seasonal_periods')
        model = ExponentialSmoothing(history, trend=trend, seasonal=seasonal, seasonal_periods=seasonal_periods)
        model = model.fit()
    elif model_type == 'Prophet':
        model = model_info.get('model') 
        if model is None:
            raise ValueError("Prophet model object is missing.")
    else:
        raise ValueError(f"Unsupported model type for reconstruction: {model_type}")
    

    today = pd.to_datetime(date.today())
    last_date_in_model = get_last_date_in_model(model, model_type, model_info)

    if last_date_in_model is None:
        raise ValueError(f"Cannot determine last training date for model type {model_type}.")

    # Calculate the number of periods to forecast
    delta_months = (today.year - last_date_in_model.year) * 12 + (today.month - last_date_in_model.month)
    total_periods = delta_months + months_to_predict
    if total_periods <= 0:
        total_periods = months_to_predict

    future_dates = pd.date_range(start=last_date_in_model + pd.DateOffset(months=1), periods=total_periods, freq='MS')

    #  Generate Forecast 
    if model_type == 'Prophet':
        future_df = model.make_future_dataframe(periods=total_periods, freq='MS')
        forecast = model.predict(future_df)
        if log_transformed:
            forecast['yhat'] = np.exp(forecast['yhat'])
            forecast['yhat_lower'] = np.exp(forecast['yhat_lower'])
            forecast['yhat_upper'] = np.exp(forecast['yhat_upper'])
        # Standardize column names
        forecast = forecast.rename(columns={'ds': 'ds', 'yhat': 'yhat', 'yhat_lower': 'yhat_lower', 'yhat_upper': 'yhat_upper'})

    elif model_type == 'SARIMA':
        pred_summary = model.get_prediction(start=model.nobs, end=model.nobs + total_periods - 1).summary_frame()
        if log_transformed:
            pred_summary = np.exp(pred_summary)
        pred_summary.index = future_dates
        # Standardize column names
        forecast = pred_summary.reset_index().rename(columns={'index': 'ds', 'mean': 'yhat', 'mean_ci_lower': 'yhat_lower', 'mean_ci_upper': 'yhat_upper'})

    elif model_type == 'Holt-Winters':
        predictions_array = model.forecast(steps=total_periods)
        if log_transformed:
            predictions_array = np.exp(predictions_array)
        
        forecast = pd.DataFrame({
            'ds': future_dates,
            'yhat': predictions_array,
            'yhat_lower': predictions_array * 0.9,  
            'yhat_upper': predictions_array * 1.1   
        })

    else:
        raise ValueError(f"Unsupported model type: {model_type}")

    # Filter for the requested future months
    start_of_current_month = today.to_period('M').to_timestamp()
    future_predictions = forecast[forecast['ds'] >= start_of_current_month]
    return future_predictions.head(months_to_predict)

@app.route('/api/commodities', methods=['GET'])
def commodities():
    """Endpoint to get the list of available commodities."""
    commodity_list = get_commodity_list()
    if not commodity_list:
        return jsonify({'error': 'No models found. Please train models first.'}), 404
    return jsonify(commodity_list)

@app.route('/api/history', methods=['GET'])
def get_history():
    commodity = request.args.get('commodity')
    if not commodity:
        return jsonify({"error": "Commodity parameter is required"}), 400

    
    file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'tabel-data-perbulan.xlsx'))

    try:
        df = pd.read_excel(file_path, sheet_name=0)  
        app.logger.info(f"Columns from Excel file: {df.columns.tolist()}")
        if commodity not in df.columns:
            return jsonify({"error": f"Commodity '{commodity}' not found"}), 404

        history_df = df[['Date', commodity]].rename(columns={'Date': 'ds', commodity: 'y'})
        history_df['ds'] = pd.to_datetime(history_df['ds']).dt.strftime('%Y-%m-%d')
        
        # Ambil data 12 bulan terakhir
        history_df = history_df.tail(12)
        
        return jsonify({"history": history_df.to_dict(orient='records')})
    except FileNotFoundError:
        app.logger.error(f"Historical data file not found: {file_path}")
        return jsonify({"error": "Historical data source not found."}), 500
    except Exception as e:
        app.logger.error(f"Error reading historical data: {e}")
        return jsonify({"error": "Terjadi kesalahan saat mengambil data historis."}), 500

@app.route('/api/predict', methods=['POST'])
def predict():
    """Endpoint to generate price predictions."""
    data = request.get_json()
    commodity = data.get('commodity')
    try:
        months = int(data.get('months', 1))
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid number of months specified.'}), 400

    if not commodity:
        return jsonify({'error': 'Commodity not specified.'}), 400

    
    available_commodities = get_commodity_list()
    if commodity not in available_commodities:
        app.logger.warning(f"Invalid commodity '{commodity}' requested.")
        return jsonify({'error': f'Invalid commodity specified: {commodity}'}), 400
  

    model_filename = f"{commodity.replace(' ', '_')}.pkl"
    model_path = os.path.join(MODELS_DIR, model_filename)

    app.logger.info(f"Attempting to predict for commodity: {commodity} with model path: {model_path}")

    if not os.path.exists(model_path):
        app.logger.error(f"Model file not found at {model_path}")
        return jsonify({'error': f'Model for {commodity} not found.'}), 404

    try:
        with open(model_path, 'rb') as f:
            loaded_object = pickle.load(f)
        app.logger.info(f"Successfully loaded model from {model_path}")
    except Exception as e:
        app.logger.error(f"Error loading pickle file {model_path}: {e}")
        return jsonify({'error': f'Could not load model file: {e}'}), 500

    try:
        model_type = loaded_object.get('model_type')
        app.logger.info(f"Model type for {commodity}: {model_type}")
        
        if model_type == 'Ensemble':
            ensemble_predictions = pd.DataFrame()
            weights = loaded_object.get('weights', [])
            sub_models_info = [loaded_object.get(m) for m in ['sarima', 'holt_winters', 'prophet'] if loaded_object.get(m)]

            if not sub_models_info or not weights or len(sub_models_info) != len(weights):
                 app.logger.error(f"Invalid Ensemble configuration for {commodity}")
                 return jsonify({'error': 'Invalid Ensemble model configuration.'}), 500

            app.logger.info(f"Processing Ensemble model for {commodity} with {len(sub_models_info)} sub-models.")
            for i, (model_info, weight) in enumerate(zip(sub_models_info, weights)):
                sub_model_type = model_info.get('model_type')
                app.logger.info(f"Processing sub-model {i+1}/{len(sub_models_info)}: {sub_model_type} with weight {weight}")
                
                if not sub_model_type:
                    app.logger.error("Sub-model type is missing in Ensemble configuration.")
                    return jsonify({'error': 'Sub-model type is missing in Ensemble configuration.'}), 500

                try:
                    sub_preds = predict_single_model(model_info, months)
                    app.logger.info(f"Generated {len(sub_preds)} predictions from {sub_model_type}.")

                    if sub_preds.empty:
                        app.logger.warning(f"Sub-model {sub_model_type} produced no predictions.")
                        continue

                    weighted_preds = sub_preds.copy()
                    for col in ['yhat', 'yhat_lower', 'yhat_upper']:
                        if col in weighted_preds.columns:
                            weighted_preds[col] *= weight
                    
                    if ensemble_predictions.empty:
                        ensemble_predictions = weighted_preds.set_index('ds')
                    else:
                        ensemble_predictions = ensemble_predictions.add(weighted_preds.set_index('ds'), fill_value=0)
                except Exception as e:
                    app.logger.error(f"Error processing sub-model {sub_model_type} for {commodity}: {e}", exc_info=True)
                    # Continue to next sub-model if one fails
                    continue
            
            if ensemble_predictions.empty:
                app.logger.error(f"Ensemble prediction failed for {commodity} because all sub-models failed or produced no predictions.")
                return jsonify({'error': 'Ensemble prediction failed for all sub-models.'}), 500

            final_predictions = ensemble_predictions.reset_index()

        else: # Single model
            app.logger.info(f"Processing single model prediction for {commodity}")
            final_predictions = predict_single_model(loaded_object, months)
            app.logger.info(f"Generated {len(final_predictions)} predictions for single model {commodity}.")

        if final_predictions.empty:
            app.logger.warning(f"No future predictions were generated for {commodity}.")
            return jsonify({'commodity': commodity, 'predictions': []})

        # Final processing and response
        final_predictions['yhat_lower'] = final_predictions['yhat_lower'].clip(lower=0)
        predictions_list = final_predictions.to_dict('records')

        app.logger.info(f"Successfully generated {len(predictions_list)} predictions for {commodity}.")
        # If only one prediction, return a single object as before
        if len(predictions_list) == 1:
             return jsonify({'commodity': commodity, 'predictions': predictions_list[0]})

        return jsonify({'commodity': commodity, 'predictions': predictions_list})

    except Exception as e:
        app.logger.error(f"Error during prediction for {commodity}: {e}", exc_info=True)
        return jsonify({'error': 'Terjadi kesalahan tak terduga saat membuat prediksi.'}), 500

if __name__ == '__main__':
  
    app.run(debug=False, host='0.0.0.0')