# -*- coding: utf-8 -*-
"""
IBAPI - Getting historical data for stocks from different exchanges and geographies

@author: Mayank Rasu (http://rasuquant.com/wp/)
"""


# Import libraries
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
import pandas as pd
import threading
import time

class TradeApp(EWrapper, EClient): 
    def __init__(self): 
        EClient.__init__(self, self) 
        self.data = {}
        
    def historicalData(self, reqId, bar):
        if reqId not in self.data:
            self.data[reqId] = pd.DataFrame([{"Date":bar.date,"Open":bar.open,"High":bar.high,"Low":bar.low,"Close":bar.close,"Volume":bar.volume}])
        else:
            self.data[reqId] = pd.concat((self.data[reqId],pd.DataFrame([{"Date":bar.date,"Open":bar.open,"High":bar.high,"Low":bar.low,"Close":bar.close,"Volume":bar.volume}])))
            #self.data[reqId].append({"Date":bar.date,"Open":bar.open,"High":bar.high,"Low":bar.low,"Close":bar.close,"Volume":bar.volume})
        print("reqID:{}, date:{}, open:{}, high:{}, low:{}, close:{}, volume:{}".format(reqId,bar.date,bar.open,bar.high,bar.low,bar.close,bar.volume))
        

def websocket_con():
    app.run()
    
app = TradeApp()      
app.connect("127.0.0.1", 7497, clientId=1)

# starting a separate daemon thread to execute the websocket connection
con_thread = threading.Thread(target=websocket_con, daemon=True)
con_thread.start()
time.sleep(1) # some latency added to ensure that the connection is established

#creating object of the Contract class - will be used as a parameter for other function calls
def generalStk(symbol,currency,exchange,sec_type="STK"):
    contract = Contract()
    contract.symbol = symbol
    contract.secType = sec_type
    contract.currency = currency
    contract.exchange = exchange
    return contract 

def histData(req_num,contract,duration,candle_size):
    app.reqHistoricalData(reqId=req_num, 
                          contract=contract,
                          endDateTime='',
                          durationStr=duration,
                          barSizeSetting=candle_size,
                          whatToShow='ADJUSTED_LAST',
                          useRTH=1,
                          formatDate=1,
                          keepUpToDate=0,
                          chartOptions=[])	 # EClient function to request contract details


tickers_data = {"INTC" : {"index":0,"currency":"USD","exchange":"ISLAND"},
                "BARC" : {"index":1,"currency":"GBP","exchange":"LSE"},
                "INFY" : {"index":2,"currency":"INR","exchange":"NSE"}}

for ticker in tickers_data:
    histData(tickers_data[ticker]["index"],
             generalStk(ticker,tickers_data[ticker]["currency"],tickers_data[ticker]["exchange"]),
             '1 M', '5 mins')
    time.sleep(5)  # some latency added to ensure that the contract details request has been processed

###################storing trade app object in dataframe#######################
def dataDataframe(ticker_data,TradeApp_obj):
    "returns extracted historical data in dataframe format"
    df_data = {}
    for symbol in ticker_data:
        try:
            df_data[symbol] = pd.DataFrame(TradeApp_obj.data[ticker_data[symbol]["index"]])
            df_data[symbol].set_index("Date",inplace=True)
        except:
            print("error encountered for {} data....skipping".format(symbol))
    return df_data

#extract and store historical data in dataframe
historicalData = dataDataframe(tickers_data,app)