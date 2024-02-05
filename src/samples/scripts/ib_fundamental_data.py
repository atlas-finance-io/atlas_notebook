# -*- coding: utf-8 -*-
"""
IB API - Fetch Fundamental Data (stock)

@author: Mayank Rasu (http://rasuquant.com/wp/)
"""


from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
import time
import threading
import os

os.chdir("D:\\Udemy\\Interactive Brokers Python API\\11_fundamental_data")

class TradeApp(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self) 
    
    def fundamentalData(self, reqId, data):
        super().fundamentalData(reqId, data)
        print("FundamentalData. ReqId:", reqId, "Data:", data)
        f = open("ticker{}_fundamental.xml".format(reqId),"w")
        f.write(data)
        f.close()


def usTechStk(symbol,sec_type="STK",currency="USD",exchange="ISLAND"):
    contract = Contract()
    contract.symbol = symbol
    contract.secType = sec_type
    contract.currency = currency
    contract.exchange = exchange
    return contract 

def histData(req_num,contract):
    """extracts historical data"""
    app.reqFundamentalData(reqId=req_num, 
                           contract=contract,
                           reportType='ReportsFinStatements',
                           fundamentalDataOptions=[])	 # EClient function to request fundamental data        

def websocket_con():
    app.run()
    
app = TradeApp()
app.connect(host='127.0.0.1', port=7497, clientId=23) #port 4002 for ib gateway paper trading/7497 for TWS paper trading
con_thread = threading.Thread(target=websocket_con, daemon=True)
con_thread.start()
time.sleep(1) # some latency added to ensure that the connection is established

tickers = ["AAPL","AMZN","INTC"]
for ticker in tickers:
    histData(tickers.index(ticker),usTechStk(ticker))
    time.sleep(5)