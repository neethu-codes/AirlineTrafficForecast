import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.statespace.sarimax import SARIMAX

st.set_page_config(layout="wide")

# ----------- LOAD DATA ----------
@st.cache_data
def load_data():
    data = pd.read_csv('AirPassengers.csv')
    data['Month'] = pd.to_datetime(data['Month'], infer_datetime_format=True)
    data.set_index('Month', inplace=True)
    ts = data['#Passengers']
    return ts

ts = load_data()
ts_log = np.log(ts)

st.title("📈 Passenger Traffic Forecasting Dashboard")
st.markdown("A SARIMA-Based Approach (2,1,2)(1,1,1,12) to Forecasting Airline Traffic")

# ----------- USER INPUT ----------
col1, col2 = st.columns([1, 3])  # col1 (slider) is narrower than col2

with col1:
    forecast_period = st.slider("Select Forecast Period (in months)", min_value=12, max_value=240, value=24, step=12)


forecast_button = st.button("Forecast")

if forecast_button:
    # ----------- TRAIN MODEL ----------
    with st.spinner("Training SARIMA model..."):
        model = SARIMAX(ts_log, 
                        order=(2, 1, 2), 
                        seasonal_order=(1, 1, 1, 12),
                        enforce_stationarity=False, 
                        enforce_invertibility=False)
        results_sarima = model.fit(disp=False)

        # ----------- FORECAST ----------
        forecast = results_sarima.get_forecast(steps=forecast_period)
        forecast_log = forecast.predicted_mean
        forecast_index = forecast_log.index

        forecast_original = np.exp(forecast_log)

        # Combine actual and forecast
        combined_series = pd.concat([ts, forecast_original])
        forecast_df = pd.DataFrame({
            "Forecasted Value": forecast_original.round().astype(int)
        })
        forecast_df.index = forecast_df.index.strftime('%Y-%m')
        forecast_df.index.name = "Date"

    # ----------- LAYOUT: Plot and Table Side-by-Side ----------
    col1, col2, col3 = st.columns([1,1, 1])

    with col1:
        st.subheader("📉 Forecast Plot")
        fig, ax = plt.subplots(figsize=(10, 5))
        ts.plot(ax=ax, label='Actual')
        forecast_original.plot(ax=ax, color='red', label='Forecast')
        ax.set_xlabel("Date")
        ax.set_ylabel("#Passengers")
        ax.set_title("Actual vs Forecasted Passenger Count")
        ax.legend()
        st.pyplot(fig)

    with col2:
        st.subheader("📋 Forecast Table")
        st.dataframe(forecast_df.style.format("{:.0f}"), use_container_width=True)
