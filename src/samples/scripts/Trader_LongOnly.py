# Disclaimer:
# The following illustrative examples are for general information and educational purposes only.
# It is neither investment advice nor a recommendation to trade, invest or take whatsoever actions.
# The below code should only be used in combination with the Binance Spot Testnet and NOT with a Live Trading Account.


from binance.client import Client
from binance import ThreadedWebsocketManager
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time

class LongOnlyTrader(): # optimized for TWM
    
    def __init__(self, symbol, bar_length, return_thresh, volume_thresh, units, position = 0):
        
        self.symbol = symbol
        self.bar_length = bar_length
        self.available_intervals = ["1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d", "3d", "1w", "1M"]
        self.units = units
        self.position = position
        self.trades = 0 
        self.trade_values = [] 
        
        #*****************add strategy-specific attributes here******************
        self.return_thresh = return_thresh
        self.volume_thresh = volume_thresh
        #************************************************************************
    
    def start_trading(self, historical_days):
        
        self.twm = ThreadedWebsocketManager()
        self.twm.start()
        
        if self.bar_length in self.available_intervals:
            self.get_most_recent(symbol = self.symbol, interval = self.bar_length,
                                 days = historical_days)
            self.twm.start_kline_socket(callback = self.stream_candles,
                                        symbol = self.symbol, interval = self.bar_length)
            self.twm.join() # required in script!
        # "else" to be added later in the course 
    
    def get_most_recent(self, symbol, interval, days):
    
        now = datetime.utcnow()
        past = str(now - timedelta(days = days))
    
        bars = client.get_historical_klines(symbol = symbol, interval = interval,
                                            start_str = past, end_str = None, limit = 1000)
        df = pd.DataFrame(bars)
        df["Date"] = pd.to_datetime(df.iloc[:,0], unit = "ms")
        df.columns = ["Open Time", "Open", "High", "Low", "Close", "Volume",
                      "Clos Time", "Quote Asset Volume", "Number of Trades",
                      "Taker Buy Base Asset Volume", "Taker Buy Quote Asset Volume", "Ignore", "Date"]
        df = df[["Date", "Open", "High", "Low", "Close", "Volume"]].copy()
        df.set_index("Date", inplace = True)
        for column in df.columns:
            df[column] = pd.to_numeric(df[column], errors = "coerce")
        df["Complete"] = [True for row in range(len(df)-1)] + [False]
        
        self.data = df
    
    def stream_candles(self, msg):
        
        # extract the required items from msg
        event_time = pd.to_datetime(msg["E"], unit = "ms")
        start_time = pd.to_datetime(msg["k"]["t"], unit = "ms")
        first   = float(msg["k"]["o"])
        high    = float(msg["k"]["h"])
        low     = float(msg["k"]["l"])
        close   = float(msg["k"]["c"])
        volume  = float(msg["k"]["v"])
        complete=       msg["k"]["x"]
    
        # stop trading session
        if event_time >= datetime(2023, 8, 21, 12, 16):
            self.twm.stop()
            if self.position != 0:
                order = client.create_order(symbol = self.symbol, side = "SELL", type = "MARKET", quantity = self.units)
                self.report_trade(order, "GOING NEUTRAL AND STOP") 
                self.position = 0
            else: 
                print("STOP")
        
        #more stop examples:
        # if self.trades >= xyz
        # if self.cum_profits <> xyz
        
        else:    
            # print out
            print(".", end = "", flush = True) # just print something to get a feedback (everything OK) 
    
            # feed df (add new bar / update latest bar)
            self.data.loc[start_time] = [first, high, low, close, volume, complete]
        
            # prepare features and define strategy/trading positions whenever the latest bar is complete
            if complete == True:
                self.define_strategy()
                self.execute_trades()
        
    def define_strategy(self):
        
        df = self.data.copy()
        
        #******************** define your strategy here ************************
        df = df[["Close", "Volume"]].copy()
        df["returns"] = np.log(df.Close / df.Close.shift())
        df["vol_ch"] = np.log(df.Volume.div(df.Volume.shift(1)))
        df.loc[df.vol_ch > 3, "vol_ch"] = np.nan
        df.loc[df.vol_ch < -3, "vol_ch"] = np.nan  
        
        cond1 = df.returns >= self.return_thresh
        cond2 = df.vol_ch.between(self.volume_thresh[0], self.volume_thresh[1])
        
        df["position"] = 1
        df.loc[cond1 & cond2, "position"] = 0
        #***********************************************************************
        
        self.prepared_data = df.copy()
    
    def execute_trades(self): 
        if self.prepared_data["position"].iloc[-1] == 1: # if position is long -> go/stay long
            if self.position == 0:
                order = client.create_order(symbol = self.symbol, side = "BUY", type = "MARKET", quantity = self.units)
                self.report_trade(order, "GOING LONG")  
            self.position = 1
        elif self.prepared_data["position"].iloc[-1] == 0: # if position is neutral -> go/stay neutral
            if self.position == 1:
                order = client.create_order(symbol = self.symbol, side = "SELL", type = "MARKET", quantity = self.units)
                self.report_trade(order, "GOING NEUTRAL")  
            self.position = 0
    
    def report_trade(self, order, going):
        
        # extract data from order object
        side = order["side"]
        time = pd.to_datetime(order["transactTime"], unit = "ms")
        base_units = float(order["executedQty"])
        quote_units = float(order["cummulativeQuoteQty"])
        price = round(quote_units / base_units, 5)
        
        # calculate trading profits
        self.trades += 1
        if side == "BUY":
            self.trade_values.append(-quote_units)
        elif side == "SELL":
            self.trade_values.append(quote_units) 
        
        if self.trades % 2 == 0:
            real_profit = round(np.sum(self.trade_values[-2:]), 3) 
            self.cum_profits = round(np.sum(self.trade_values), 3)
        else: 
            real_profit = 0
            self.cum_profits = round(np.sum(self.trade_values[:-1]), 3)
        
        # print trade report
        print(2 * "\n" + 100* "-")
        print("{} | {}".format(time, going)) 
        print("{} | Base_Units = {} | Quote_Units = {} | Price = {} ".format(time, base_units, quote_units, price))
        print("{} | Profit = {} | CumProfits = {} ".format(time, real_profit, self.cum_profits))
        print(100 * "-" + "\n")
        
if __name__ == "__main__": # only if we run trader.py as a script, please do the following:

    api_key = "insert here"
    secret_key = "insert here"

    client = Client(api_key = api_key, api_secret = secret_key, tld = "com", testnet = True)
    
    symbol = "BTCUSDT"
    bar_length = "1m"
    return_thresh = 0
    volume_thresh = [-3, 3]
    units = 0.01
    position = 0

    trader = LongOnlyTrader(symbol = symbol, bar_length = bar_length, return_thresh = return_thresh, 
                             volume_thresh = volume_thresh, units = units, position = position)

    trader.start_trading(historical_days = 1/24)
