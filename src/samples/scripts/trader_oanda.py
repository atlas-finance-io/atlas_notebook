
#Disclaimer: 
#The following illustrative example is for general information and educational purposes only.
#It is neither investment advice nor a recommendation to trade, invest or take whatsoever actions.
#The below code should only be used in combination with an Oanda Practice/Demo Account and NOT with a Live Trading Account.


import pandas as pd
import numpy as np
import tpqoa
from datetime import datetime, timedelta
import time

class ConTrader(tpqoa.tpqoa):
    def __init__(self, conf_file, instrument, bar_length, window, units, sl_perc = None, tsl_perc = None, tp_perc = None):
        super().__init__(conf_file)
        self.instrument = instrument
        self.bar_length = pd.to_timedelta(bar_length)
        self.tick_data = pd.DataFrame()
        self.raw_data = None
        self.data = None 
        self.last_bar = None
        self.units = units
        self.position = 0
        self.profits = [] 
        self.sl_perc = sl_perc 
        self.tsl_perc = tsl_perc 
        self.tp_perc = tp_perc 
        
        #*****************add strategy-specific attributes here******************
        self.window = window
        #************************************************************************
    
    def get_most_recent(self, days = 5):
        while True:
            time.sleep(2)
            now = datetime.utcnow()
            now = now - timedelta(microseconds = now.microsecond)
            past = now - timedelta(days = days)
            df = self.get_history(instrument = self.instrument, start = past, end = now,
                                   granularity = "S5", price = "M", localize = False).c.dropna().to_frame()
            df.rename(columns = {"c":self.instrument}, inplace = True)
            df = df.resample(self.bar_length, label = "right").last().dropna().iloc[:-1]
            self.raw_data = df.copy()
            self.last_bar = self.raw_data.index[-1]
            if pd.to_datetime(datetime.utcnow()).tz_localize("UTC") - self.last_bar < self.bar_length:
                break
            
    def start_trading(self, days, max_attempts = 5, wait = 20, wait_increase = 0): # Error Handling
        attempt = 0
        success = False
        while True:
            try:
                self.get_most_recent(days)
                self.stream_data(self.instrument)
            except Exception as e:
                print(e, end = " | ")
            else:
                success = True
                break    
            finally:
                attempt +=1
                print("Attempt: {}".format(attempt), end = '\n')
                if success == False:
                    if attempt >= max_attempts:
                        print("max_attempts reached!")
                        try: # try to terminate session
                            time.sleep(wait)
                            self.terminate_session(cause = "Unexpected Session Stop (too many errors).")
                        except Exception as e:
                            print(e, end = " | ")
                            print("Could not terminate session properly!")
                        finally: 
                            break
                    else: # try again
                        time.sleep(wait)
                        wait += wait_increase
                        self.tick_data = pd.DataFrame()
        
    def on_success(self, time, bid, ask):
        print(self.ticks, end = '\r', flush = True)
        
        recent_tick = pd.to_datetime(time)
        
        # define stop
        if self.ticks >= 200:
            self.terminate_session(cause = "Scheduled Session End.")
            return
        
        # collect and store tick data
        df = pd.DataFrame({self.instrument:(ask + bid)/2}, 
                          index = [recent_tick])
        self.tick_data = pd.concat([self.tick_data, df]) 
        
        # if a time longer than the bar_lenght has elapsed between last full bar and the most recent tick
        if recent_tick - self.last_bar >= self.bar_length:
            self.resample_and_join()
            self.define_strategy()
            #self.execute_trades() now called inside self.check_positions()
            self.check_positions()
            
    def resample_and_join(self):
        self.raw_data = pd.concat([self.raw_data, self.tick_data.resample(self.bar_length, 
                                                                          label="right").last().ffill().iloc[:-1]])
        self.tick_data = self.tick_data.iloc[-1:]
        self.last_bar = self.raw_data.index[-1]
        
    def define_strategy(self): # "strategy-specific"
        df = self.raw_data.copy()
        
        #******************** define your strategy here ************************
        df["returns"] = np.log(df[self.instrument] / df[self.instrument].shift())
        df["position"] = -np.sign(df.returns.rolling(self.window).mean())
        #***********************************************************************
        
        self.data = df.copy()
        
    def execute_trades(self):
        
        # NEW - determne SL distance and TP Price
        current_price = self.data[self.instrument].iloc[-1]
        
        if self.sl_perc:
            sl_dist = round(current_price * self.sl_perc, 4) 
        else: 
            sl_dist = None
            
            
        if self.tsl_perc:
            tsl_dist = round(current_price * self.tsl_perc, 4) 
        else: 
            tsl_dist = None
            
        
        if self.tp_perc:
            if self.data["position"].iloc[-1] == 1:
                tp_price = round(current_price * (1 + self.tp_perc), 2) 
            elif self.data["position"].iloc[-1] == -1:
                tp_price = round(current_price * (1 - self.tp_perc), 2)      
        else: 
            tp_price = None
        
        if self.data["position"].iloc[-1] == 1:
            if self.position == 0:
                order = self.create_order(self.instrument, self.units, suppress = True, ret = True,
                                          sl_distance = sl_dist, tsl_distance = tsl_dist, tp_price = tp_price)
                self.report_trade(order, "GOING LONG")  
            elif self.position == -1:
                order = self.create_order(self.instrument, self.units * 2, suppress = True, ret = True,
                                          sl_distance = sl_dist, tsl_distance = tsl_dist, tp_price = tp_price) 
                self.report_trade(order, "GOING LONG")  
            self.position = 1
        elif self.data["position"].iloc[-1] == -1: 
            if self.position == 0:
                order = self.create_order(self.instrument, -self.units, suppress = True, ret = True,
                                          sl_distance = sl_dist, tsl_distance = tsl_dist, tp_price = tp_price)
                self.report_trade(order, "GOING SHORT")  
            elif self.position == 1:
                order = self.create_order(self.instrument, -self.units * 2, suppress = True, ret = True,
                                          sl_distance = sl_dist, tsl_distance = tsl_dist, tp_price = tp_price)
                self.report_trade(order, "GOING SHORT")  
            self.position = -1
        elif self.data["position"].iloc[-1] == 0: 
            if self.position == -1:
                order = self.create_order(self.instrument, self.units, suppress = True, ret = True) 
                self.report_trade(order, "GOING NEUTRAL")  
            elif self.position == 1:
                order = self.create_order(self.instrument, -self.units, suppress = True, ret = True)
                self.report_trade(order, "GOING NEUTRAL")  
            self.position = 0
    
    def report_trade(self, order, going):  
        self.order_id = order["id"] 
        time = order["time"]
        units = order["units"]
        price = order["price"]
        pl = float(order["pl"])
        self.profits.append(pl)
        cumpl = sum(self.profits)
        print("\n" + 100* "-")
        print("{} | {}".format(time, going))
        print("{} | units = {} | price = {} | P&L = {} | Cum P&L = {}".format(time, units, price, pl, cumpl))
        print(100 * "-" + "\n")  
        
    def terminate_session(self, cause):
        self.stop_stream = True
        if self.position != 0:
            close_order = self.create_order(self.instrument, units = -self.position * self.units,
                                            suppress = True, ret = True) 
            self.report_trade(close_order, "GOING NEUTRAL")
            self.position = 0
        print(cause, end = " | ")
    
    def check_positions(self): 
        exp_position = self.position*self.units # get current (exp.) position
        
        # get current actual position
        try:
            positions = self.get_positions()
            actual_position = 0
            for pos in positions:
                if pos["instrument"] == self.instrument:
                    actual_position = round(float(pos["long"]["units"]) + float(pos["short"]["units"]), 0)
        except:
            actual_position = exp_position 
        
        if actual_position != exp_position: # if mismatch (sl/tp triggered)
            self.position = actual_position / self.units # update self.position
            try:
                latest_actions = self.get_transactions(self.order_id) # get all actions since last recorded trade (excl.)
                for action in latest_actions:
                    if action["type"] == "ORDER_FILL": # last filled order/trade (sl/tp trade!) 
                        self.report_trade(action, "GOING NEUTRAL") # report sl/tp trade
            except:
                pass
            finally:
                self.terminate_session("SL/TP Event!") # stop session
        elif self.position != self.data["position"].iloc[-1]: # if no mismatch and trade required
            self.execute_trades()
        else: # if no mismatch and no trade required
            pass
        
if __name__ == "__main__":
        
    #insert the file path of your config file below!
    trader = ConTrader(r"C:\Users\hagma\AlgoTrading\Part5_Materials\oanda.cfg",
                       "EUR_USD", "1min", window = 1, units = 10000, sl_perc = 0.01, tp_perc = 0.01)
    trader.start_trading(days = 5, max_attempts =  3, wait = 20, wait_increase = 0)
    
    
    