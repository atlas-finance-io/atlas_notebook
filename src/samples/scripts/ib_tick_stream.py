# -*- coding: utf-8 -*-
"""
IB API - streaming tick by tick data

@author: Mayank Rasu (http://rasuquant.com/wp/)
"""

# Import libraries
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
import datetime
import threading


class TradeApp(EWrapper, EClient): 
    def __init__(self): 
        EClient.__init__(self, self) 

    def tickByTickAllLast(self, reqId, tickType, time, price, size, tickAtrribLast, exchange, specialConditions):
        super().tickByTickAllLast(reqId, tickType, time, price, size, tickAtrribLast, exchange, specialConditions)
        if tickType == 1:
            print("Last.", end='')
        else:
            print("AllLast.", end='')
            print(" ReqId:", reqId, "Time:", datetime.datetime.fromtimestamp(time).strftime("%Y%m%d %H:%M:%S"),
                  "Price:", price, "Size:", size)
        

def usTechStk(symbol,sec_type="STK",currency="USD",exchange="ISLAND"):
    contract = Contract()
    contract.symbol = symbol
    contract.secType = sec_type
    contract.currency = currency
    contract.exchange = exchange
    return contract 

def streamData(req_num,contract):
    """stream tick leve data"""
    app.reqTickByTickData(reqId=req_num, 
                          contract=contract,
                          tickType="AllLast",
                          numberOfTicks=0,
                          ignoreSize=True)
    
def websocket_con():
    app.run()

app = TradeApp()
app.connect(host='127.0.0.1', port=7497, clientId=23) #port 4002 for ib gateway paper trading/7497 for TWS paper trading
con_thread = threading.Thread(target=websocket_con, daemon=True)
con_thread.start()

tickers = ["FB","AMZN","INTC"]
for ticker in tickers:
    streamData(tickers.index(ticker),usTechStk(ticker))