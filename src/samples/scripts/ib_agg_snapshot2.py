# -*- coding: utf-8 -*-
"""
IB API - streaming aggregated snapshot data

@author: Mayank Rasu (http://rasuquant.com/wp/)
"""

# Import libraries
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
import threading


class TradeApp(EWrapper, EClient): 
    def __init__(self): 
        EClient.__init__(self, self) 

    def tickString(self, reqId, tickType, value):
        super().tickString(reqId, tickType, value)
        values = value.split(";")
        if tickType==48:
            print("TickString. TickerId:", reqId, "Type:", tickType,
                  "Last Price:", values[0], "Last Size:", values[1],
                  "Time:", values[2], "VWAP:", values[-2])
        
        
def usTechStk(symbol,sec_type="STK",currency="USD",exchange="ISLAND"):
    contract = Contract()
    contract.symbol = symbol
    contract.secType = sec_type
    contract.currency = currency
    contract.exchange = exchange
    return contract 

def streamSnapshotData(req_num,contract):
    """stream tick leve data"""
    app.reqMktData(reqId=req_num, 
                   contract=contract,
                   genericTickList="233",
                   snapshot=False,
                   regulatorySnapshot=False,
                   mktDataOptions=[])
    
def websocket_con():
    app.run()

app = TradeApp()
app.connect(host='127.0.0.1', port=7497, clientId=23) #port 4002 for ib gateway paper trading/7497 for TWS paper trading
con_thread = threading.Thread(target=websocket_con, daemon=True)
con_thread.start()

tickers = ["FB","AMZN","INTC"]
for ticker in tickers:
    streamSnapshotData(tickers.index(ticker),usTechStk(ticker))