# Importing necessary libraries
import streamlit as st
import streamlit.components.v1 as components
from pycoingecko import CoinGeckoAPI
import pandas as pd
import plotly.graph_objs as go
from PIL import Image
from darts import TimeSeries
from darts.models import ExponentialSmoothing
from darts.models import Prophet
from darts.utils.timeseries_generation import datetime_attribute_timeseries
import datetime

# Initializing Pycoingecko API client
cg = CoinGeckoAPI()

image = Image.open('btc.png')
st.image(image, width=100)

# Background image
background_image_url = 'https://images.unsplash.com/photo-1621631908015-5e91cb7dcac6?q=80&w=2071&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D'

# Using CSS for setting the background image
st.markdown(f"""
<style>
.stApp {{
    background-image: url({background_image_url});
    background-size: cover;
}}
</style>
""", unsafe_allow_html=True)

# Streamlit app
st.markdown(" # CryptoForecast Project :heavy_dollar_sign:")
st.markdown('''Explore :violet[historical data], forecast :red[future trends], and make :blue[informed decisions].''')

# Dropdown to select cryptocurrency
selected_crypto = st.selectbox('Select Cryptocurrency', ['bitcoin', 'ethereum', 'litecoin', 'solana', 'dogecoin', 'ripple', 'cardano', 'polygon', 'avalanche', 'chainlink', 'polkadot'])
st.write("")
st.write("")

# Fetching historical data
@st.cache_data
def fetch_data(coin):
    data = cg.get_coin_market_chart_by_id(id=coin, vs_currency='usd', days='max')
    prices = data['prices']
    df = pd.DataFrame(prices, columns=['timestamp', 'price'])
    df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('date', inplace=True)
    return df.drop('timestamp', axis=1)

# Displaying historical data
# Using interactive plotly chart for historical data
df = fetch_data(selected_crypto)
st.write(f"Displaying historical price data for {selected_crypto.capitalize()}")
fig = go.Figure()
fig.add_trace(go.Scatter(x=df.index, y=df['price'], mode='lines', name='Historical Price'))
fig.update_layout(title='Historical Price', xaxis_title='Date', yaxis_title='Price (USD)', template="plotly_white")
st.plotly_chart(fig, use_container_width=True)

# 'df' is your DataFrame containing the historical data
# Print the range of dates
print(df.index.min(), df.index.max()) 
# Check the frequency of differences between dates
print(df.index.to_series().diff().value_counts())  

# Reindex the DataFrame to ensure a continuous daily index
# This creates a new index with daily frequency covering the full range and fills missing dates with NaNs
new_index = pd.date_range(start=df.index.min(), end=df.index.max(), freq='D')
df = df.reindex(new_index)

# Simple linear interpolation to fill NaN values
df.interpolate(method='linear', inplace=True)

# Forecasting
def forecast_data(data, periods):
    data = data.iloc[-90:]
    data = data.sort_index()
    series = TimeSeries.from_dataframe(data, fill_missing_dates=False, freq='D')
    model = Prophet()
    model.fit(series)
    forecast = model.predict(periods)
    # Assuming the last row contains the most recent price
    last_price = data.iloc[-1]['price']
    return forecast, last_price

# User input for forecast horizon
forecast_horizon = st.slider('Select forecast horizon (days)', min_value=1, max_value=90, value=30)

# After forecasting
if st.button('Forecast Prices'):
    forecast, last_price = forecast_data(df, forecast_horizon)
    # Preparing forecast data for plotting
    forecast_df = forecast.pd_dataframe()
    forecast_dates = forecast.pd_dataframe().index
    
    # Creatng a plot with both historical and forecasted data for comparison
    combined_fig = go.Figure()
    
    # Add historical data to the plot
    combined_fig.add_trace(go.Scatter(x=df.index, y=df['price'], mode='lines', name='Historical Price'))
    
    # Add forecasted data to the plot
    combined_fig.add_trace(go.Scatter(x=forecast_dates, y=forecast_df.iloc[:, 0], mode='lines', name='Forecasted Price', line=dict(dash='dash')))
    
    combined_fig.update_layout(title='Historical and Forecasted Price', xaxis_title='Date', yaxis_title='Price (USD)', template="plotly_white")
    st.plotly_chart(combined_fig, use_container_width=True)
    
    # Assuming the forecast is daily and we look at the last day's forecasted price
    # Getting the last forecasted price
    forecasted_price = forecast.pd_dataframe().iloc[-1, 0]  
    
    percentage_change = ((forecasted_price - last_price) / last_price) * 100
    
    # Decision to Buy or Hold
    if forecasted_price > last_price and percentage_change > 5:
        action = "Buy"
    elif forecasted_price < last_price and percentage_change < -5:
        action = "Sell"
    else:
        action = "Hold"
    
   # Displaying Messages to Buy or Hold
    if action == "Buy":
        st.markdown("""**Buy** - The forecasted price is {} % higher than the current price :money_with_wings:.""".format(round(percentage_change, 2)))
    elif action == "Sell":
        st.markdown("""**Sell** - The forecasted price is {} % lower than the current price :money_with_wings:.""".format(round(percentage_change, 2)))
    else:
        st.markdown("""**Hold** - The forecasted price has a difference of {} % regarding the current price :gem::punch:.""".format(round(percentage_change, 2)))


# Expander for a Note
st.write("")
with st.expander("Note :memo:"):
    st.write("""
    The forecasts provided here are based on historical data patterns. 
    Please consider market volatility before making investment decisions :briefcase:.
    """)