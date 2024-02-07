import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import mplfinance as mpf
from darts import TimeSeries
from darts.models import NBEATSModel
from darts.utils import timeseries_generation as tg
import streamlit as st
from pycoingecko import CoinGeckoAPI
import datetime



# Suppressing warnings
import warnings
warnings.filterwarnings('ignore', category=FutureWarning)


# Initialize CoinGeckoAPI
cg = CoinGeckoAPI()


# Get the current date
current_date = datetime.datetime.now().date()

# Get the data
def get_data(coin, currency, days):
    data = cg.get_coin_market_chart_range_by_id(id=coin, vs_currency=currency, from_timestamp=(current_date - datetime.timedelta(days=days)).isoformat(), to_timestamp=current_date.isoformat())
    data = pd.DataFrame(data['prices'], columns=['time', 'price'])
    data['time'] = pd.to_datetime(data['time'], unit='ms')
    data.set_index('time', inplace=True)
    return data

# Create a time series
def create_time_series(coin, currency, days):
    data = get_data(coin, currency, days)
    ts = TimeSeries.from_series(data['price'])
    return ts

# Create a model
def create_model(coin, currency, days, epochs):
    ts = create_time_series(coin, currency, days)
    model = NBEATSModel(input_chunk_length=10, output_chunk_length=5, n_epochs=epochs)
    model.fit(ts, verbose=True)
    return model

# Create a forecast
def create_forecast(coin, currency, days, epochs, steps):
    model = create_model(coin, currency, days, epochs)
    ts = create_time_series(coin, currency, days)
    forecast = model.predict(steps)
    return forecast

# Plot the forecast
def plot_forecast(coin, currency, days, epochs, steps):
    ts = create_time_series(coin, currency, days)
    forecast = create_forecast(coin, currency, days, epochs, steps)
    plt.figure(figsize=(10, 6))
    ts.plot(label='actual')
    forecast.plot(label='forecast', lw=2)
    plt.title(f'Forecast for {coin.upper()}/{currency.upper()}')
    plt.legend()
    plt.show()



# Streamlit
st.title('Cryptocurrency Price Prediction')
st.markdown('This app is for educational purposes only. The predictions are not financial advice.')
st.sidebar.header('User Input')
coin = st.sidebar.text_input('Enter the name of the coin', 'bitcoin')
currency = st.sidebar.text_input('Enter the currency', 'usd')
days = st.sidebar.slider('Days', 1, 365, 30)
epochs = st.sidebar.slider('Epochs', 1, 100, 10)
steps = st.sidebar.slider('Steps', 1, 365, 30)
st.write('Data for the last', days, 'days')
st.write('Model trained for', epochs, 'epochs')
st.write('Forecast for the next', steps, 'days')
st.write('Coin:', coin.upper())
st.write('Currency:', currency.upper())

# Plot the forecast
st.write('Forecast')
plot_forecast(coin, currency, days, epochs, steps)
st.pyplot()

# Get the data
st.write('Data')
data = get_data(coin, currency, days)
st.write(data)

# Plot the data
st.write('Plot')
mpf.plot(data, type='candle', style='charles', title=f'{coin.upper()}/{currency.upper()}')
st.pyplot()