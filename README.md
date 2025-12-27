# Commodity Price Prediction Web App

This project is a full-stack web application designed to predict the prices of various commodities. It features a React-based frontend for user interaction and a Python Flask backend that serves the prediction models.

## Features

- **Dynamic Commodity List**: The application automatically detects available prediction models.
- **Multiple Prediction Models**: Utilizes several time-series forecasting models to provide predictions.
- **Historical Data Visualization**: Displays the last 12 months of historical price data for the selected commodity.
- **Future Price Prediction**: Users can select a commodity and the number of future months to predict.
- **RESTful API**: A Flask-based API to handle requests for commodity lists, historical data, and predictions.

## Technologies Used

- **Frontend**:
  - React
  - Vite
  - Chart.js for data visualization
  - Axios for API requests
- **Backend**:
  - Flask
  - Pandas for data manipulation
  - Prophet, Statsmodels for time-series modeling
  - Gunicorn for production deployment

## Forecasting Models

The core of this application is its ability to forecast prices using different time-series models. The best model (or a combination of models) is chosen for each commodity based on performance during training.

### SARIMA (Seasonal Autoregressive Integrated Moving Average)

SARIMA is a powerful statistical model used for analyzing and forecasting time-series data that exhibits seasonality. It is an extension of the ARIMA model and is well-suited for data with predictable, repeating patterns over a fixed period (e.g., yearly cycles).

### Prophet

Developed by Facebook, Prophet is a forecasting procedure implemented in Python and R. It is particularly effective for time-series data that has strong seasonal effects and several seasons of historical data. Prophet is robust to missing data and shifts in the trend and typically handles outliers well.

### Holt-Winters (Triple Exponential Smoothing)

The Holt-Winters method is an exponential smoothing technique used for forecasting time-series data that displays both a trend and seasonality. It works by breaking down the data into three components: level, trend, and seasonality, and then forecasting each one.

### Ensemble Model

The Ensemble model is a meta-model that combines the predictions from SARIMA, Holt-Winters, and Prophet. It calculates a weighted average of the forecasts from these individual models. The weights are determined during the model training phase based on each model's performance (e.g., based on Mean Absolute Error). The goal of ensembling is to produce a more accurate and robust forecast than any single model could on its own.

## Project Structure

```
/
├── backend/         # Flask API and prediction logic
│   ├── app.py       # Main Flask application
│   ├── model.py     # Model training and evaluation script
│   └── ...
├── frontend/        # React user interface
│   ├── src/
│   └── ...
└── README.md
```

## Setup and Running

### Backend

1.  Navigate to the `backend` directory.
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Run the application:
    ```bash
    flask run
    ```

### Frontend

1.  Navigate to the `frontend` directory.
2.  Install dependencies:
    ```bash
    npm install
    ```
3.  Run the development server:
    ```bash
    npm run dev
    ```

## Deployment

The application is deployed on Render:

- **Frontend (Static Site)**: `https://prediksi-harga-web.onrender.com/`
- **Backend (Web Service)**: `https://prediksiharga-web.onrender.com/`
