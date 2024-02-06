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



# Define the cryptocurrencies
crypto_id = 'bitcoin'
crypto_name = 'Bitcoin'

# Fetch the histoical data from CoinGeckoAPI
crypto_data = cg.get_coin_market_chart_by_id(id=crypto_id, vs_currency='usd', days=1825)

# Extract revelant information from the API response
crypto_price = crypto_data['prices']
crypto_market_cap = crypto_data['market_caps']
crypto_total_volume = crypto_data['total_volumes']

# Create a Dataframe for the time series analysis
crypto_price_df = pd.DataFrame(crypto_price, columns=['time', 'price'])
crypto_price_df['time'] = pd.to_datetime(crypto_price_df['time'], unit='ms')
crypto_price_df.set_index('time', inplace=True)

