# -*- coding: utf-8 -*-
"""
IB API - fetching tick data from db and converting to candles

@author: Mayank Rasu (http://rasuquant.com/wp/)
"""
import pandas as pd
import sqlite3


db = sqlite3.connect('D:/Udemy/Interactive Brokers Python API/10_streaming_ticks/ticks.db')
tickers = ["FB","INTC","AMZN"]

def get_hist_5min(ticker,db):
    token = tickers.index(ticker)
    data = pd.read_sql('''SELECT * FROM TICKER%s WHERE time >=  date() - '12 day';''' %token, con=db)                
    data = data.set_index(['time'])
    data.index = pd.to_datetime(data.index)
    price_ohlc= data.loc[:, ['price']].resample('5min').ohlc().dropna()
    price_ohlc.columns = ['open','high','low','close']
    vol_ohlc = data.loc[:, ['volume']].resample('5min').apply({'volume': 'sum'}).dropna()
    df = price_ohlc.merge(vol_ohlc,left_index=True, right_index=True)
    return df

get_hist_5min("FB",db)