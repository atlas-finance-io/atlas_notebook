# -*- coding: utf-8 -*-
"""
IB API - storing tick data in sql db

@author: Mayank Rasu (http://rasuquant.com/wp/)
"""

# Import libraries
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
import datetime as dt
import threading
import sqlite3


class TradeApp(EWrapper, EClient): 
    def __init__(self): 
        EClient.__init__(self, self) 

    def tickByTickAllLast(self, reqId, tickType, time, price, size, tickAtrribLast, exchange, specialConditions):
        super().tickByTickAllLast(reqId, tickType, time, price, size, tickAtrribLast, exchange, specialConditions)
        if tickType == 1:
            pass
        else:
            c=db.cursor()
            for ms in range(100):
                try:
                    print(" ReqId:", reqId, "Time:", (dt.datetime.fromtimestamp(time)+dt.timedelta(milliseconds=ms)).strftime("%Y%m%d %H:%M:%S.%f"), "Price:", price, "Size:", size)
                    vals = [(dt.datetime.fromtimestamp(time)+dt.timedelta(milliseconds=ms)).strftime("%Y%m%d %H:%M:%S.%f"),price, size]
                    query = "INSERT INTO TICKER{}(time,price,volume) VALUES (?,?,?)".format(reqId)
                    c.execute(query,vals)
                    break
                except Exception as e:
                    print(e)
        try:
            db.commit()
        except:
            db.rollback()
        

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
    
def websocket_con(tickers):
    global db
    db = sqlite3.connect('D:/Udemy/Interactive Brokers Python API/10_streaming_ticks/ticks.db')
    c=db.cursor()
    for i in range(len(tickers)):
        c.execute("CREATE TABLE IF NOT EXISTS TICKER{} (time datetime primary key,price real(15,5), volume integer)".format(i))
    try:
        db.commit()
    except:
        db.rollback()
    app.run()

tickers = ["FB","INTC","AMZN"]
app = TradeApp()
app.connect(host='127.0.0.1', port=7497, clientId=23) #port 4002 for ib gateway paper trading/7497 for TWS paper trading
con_thread = threading.Thread(target=websocket_con, args=(tickers,), daemon=True)
con_thread.start()

for ticker in tickers:
    streamData(tickers.index(ticker),usTechStk(ticker))