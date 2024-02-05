
# Please run the following code only with your Paper Trading Account!!!
# Check the Regular Trading Hours!!!

from ib_insync import * 
import pandas as pd
import numpy as np
import datetime as dt
import os

ib = IB()
ib.connect()

# strategy parameters
freq = "1 min"
window = 1
units = 1000
end_time = (dt.datetime.utcnow() + dt.timedelta(seconds = 330)).time() # stop condition (5.5 mins from now)
sl_perc = 0.1
tp_perc = 0.1
contract = Forex('EURUSD') 
ib.qualifyContracts(contract)
cfd = CFD("EUR", currency = "USD")
ib.qualifyContracts(cfd)
conID = cfd.conId

def start_session():
    global last_update, session_start, exp_pos, current_pos
    
    exp_pos = 0 
    current_pos = 0 
    last_update = dt.datetime.utcnow()
    session_start = pd.to_datetime(last_update).tz_localize("utc")
    
    initialize_stream()  
    stop_session()

def initialize_stream(): 
    global bars, last_bar
    
    bars = ib.reqHistoricalData(
            contract,
            endDateTime='',
            durationStr='1 D',
            barSizeSetting=freq,
            whatToShow='MIDPOINT',
            useRTH=True,
            formatDate=2,
            keepUpToDate=True)
    last_bar = bars[-1].date
    bars.updateEvent += onBarUpdate 
    
def onBarUpdate(bars, hasNewBar):  
    global df, last_bar, last_update
    
    last_update = dt.datetime.utcnow()
    
    if bars[-1].date > last_bar: 
        last_bar = bars[-1].date
    
        # Data Processing
        df = pd.DataFrame(bars)[["date", "open", "high", "low", "close"]].iloc[:-1] 
        df.set_index("date", inplace = True)
        
        ####################### Trading Strategy ###########################
        df = df[["close"]].copy()
        df["returns"] = np.log(df["close"] / df["close"].shift())
        df["position"] = -np.sign(df.returns.rolling(window).mean())
        ####################################################################
        
        # Trading
        target = df["position"][-1] * units
        execute_trade(target = target)
        
        # Display
        os.system('cls')
        print(df)
    else:
        try:
            trade_reporting()
        except:
            pass

def execute_trade(target):
    global exp_pos
         
    # 1. identify required trades
    trades = target - exp_pos
    
    # 2. determine SL Price and TP Price
    current_price = df.close.iloc[-1]

    if sl_perc:
        if target > 0: # LONG
            sl_price = round(current_price * (1 - sl_perc), 4) 
        elif target < 0: # SHORT
            sl_price = round(current_price * (1 + sl_perc), 4)      
    else: 
        sl_price = None

    if tp_perc:
        if target > 0: # LONG
            tp_price = round(current_price * (1 + tp_perc), 4) 
        elif target < 0: # SHORT
            tp_price = round(current_price * (1 - tp_perc), 4)      
    else: 
        tp_price = None
        
    # 3. trade execution
    if target > 0: # GOING LONG
        if current_pos == 0: # from NEUTRAL
            go_long_short(side = "BUY", target = target, sl_price = sl_price, tp_price = tp_price) 
        elif current_pos < 0: # from SHORT:
            cancel_orders() # cancel sl/tp orders
            go_neutral(side = "BUY", trades = current_pos)
            go_long_short(side = "BUY", target = target, sl_price = sl_price, tp_price = tp_price)
    elif target < 0: # GOING SHORT
        if current_pos == 0: # from NEUTRAL  
            go_long_short(side = "SELL", target = abs(target), sl_price = sl_price, tp_price = tp_price) 
        elif current_pos > 0: # from LONG
            cancel_orders() # cancel sl/tp orders
            go_neutral(side = "SELL", trades = current_pos)
            go_long_short(side = "SELL", target = abs(target), sl_price = sl_price, tp_price = tp_price)
    else: # GOING NEUTRAL
        if current_pos < 0: # from SHORT
            cancel_orders() # cancel sl/tp orders
            go_neutral(side = "BUY", trades = current_pos)
        elif current_pos > 0: # from LONG:
            cancel_orders() # cancel sl/tp orders
            go_neutral(side = "SELL", trades = current_pos)
    exp_pos = target

def go_long_short(side, target, sl_price, tp_price): # NEW Go Long/Short starting from Neutral posistion
    bracket = BracketOrder(parentOrderId = ib.client.getReqId(), 
                           childOrderId1 = ib.client.getReqId(), 
                            childOrderId2 = ib.client.getReqId(),
                            action = side,
                            quantity = target,
                            stopLossPrice = sl_price, 
                            takeProfitPrice = tp_price,
                          )
    for o in bracket:
        order = ib.placeOrder(cfd, o)
    
def go_neutral(side, trades): # Close Long/Short position
    order = MarketOrder(side, abs(trades))
    trade = ib.placeOrder(cfd, order)    
    
def cancel_orders(): # cancel SL/TP orders
    try:
        sl_cancel = ib.cancelOrder(stopLoss)
    except:
        pass
    try:
        tp_cancel = ib.cancelOrder(takeProfit)
    except:
        pass 

def BracketOrder(parentOrderId, childOrderId1, childOrderId2,
                 action, quantity, stopLossPrice, takeProfitPrice):
    global stopLoss, takeProfit
    
    # Market Order (parent) - GO LONG or GO SHORT
    parent = Order()
    parent.orderId = parentOrderId
    parent.action = action
    parent.orderType = "MKT"
    parent.totalQuantity = quantity
    if not stopLossPrice and not takeProfitPrice: 
        parent.transmit = True
    else:
        parent.transmit = False
        
    bracketOrder = [parent]

    if stopLossPrice:
        # attached Stop Loss Order (child) 
        stopLoss = Order()
        stopLoss.orderId = childOrderId1
        stopLoss.action = "SELL" if action == "BUY" else "BUY"
        stopLoss.orderType = "STP"
        stopLoss.auxPrice = stopLossPrice
        stopLoss.totalQuantity = quantity
        stopLoss.parentId = parentOrderId
        if not takeProfitPrice: 
            stopLoss.transmit = True
        else:
            stopLoss.transmit = False
        bracketOrder.append(stopLoss)
    
    if takeProfitPrice:
        # attached Take Profit Order (child)
        takeProfit = Order()
        takeProfit.orderId = childOrderId2
        takeProfit.action = "SELL" if action == "BUY" else "BUY"
        takeProfit.orderType = "LMT"
        takeProfit.totalQuantity = quantity
        takeProfit.lmtPrice = takeProfitPrice
        takeProfit.parentId = parentOrderId
        takeProfit.transmit = True
        bracketOrder.append(takeProfit)
        
    return bracketOrder 
    
def trade_reporting():
    global report
    
    fill_df = util.df([fs.execution for fs in ib.fills()])[["execId", "time", "side", "shares", "avgPrice"]].set_index("execId")
    profit_df = util.df([fs.commissionReport for fs in ib.fills()])[["execId", "realizedPNL"]].set_index("execId")
    report = pd.concat([fill_df, profit_df], axis = 1).set_index("time").loc[session_start:]
    report = report.groupby(["time", "side"]).agg({"shares":"sum", "avgPrice":"mean", "realizedPNL":"sum"}).reset_index().set_index("time")
    report["cumPNL"] = report.realizedPNL.cumsum()
        
    os.system('cls')
    print(df, report)

def stop_session():
    global current_pos
    
    while True:
        ib.sleep(5) 
        try:
            current_pos = [pos.position for pos in ib.positions() if pos.contract.conId == conID][0]
        except:
            current_pos = 0
        if dt.datetime.utcnow().time() >= end_time:
            execute_trade(target = 0) 
            ib.cancelHistoricalData(bars) 
            ib.sleep(10)
            try:
                trade_reporting() 
            except:
                pass
            print("Session Stopped (planned).")
            ib.disconnect()
            break
        elif exp_pos != current_pos: # if SL/TP Event
            ib.sleep(5)
            try:
                current_pos = [pos.position for pos in ib.positions() if pos.contract.conId == conID][0]
            except:
                current_pos = 0
            if exp_pos != current_pos:
                execute_trade(target = 0) 
                ib.cancelHistoricalData(bars) 
                ib.sleep(10)
                try:
                    trade_reporting() 
                except:
                    pass
                print("Session Stopped (SL/TP Event).")
                ib.disconnect()
                break
            else:
                pass
        elif dt.datetime.utcnow() - last_update > dt.timedelta(seconds=120):
                # if there was no streaming update in the last 120 seconds
                ib.cancelHistoricalData(bars)
                ib.sleep(5)
                try: # try to reestablish stream
                    initialize_stream()
                except: # stop session
                    ib.sleep(5)
                    try:
                        execute_trade(target = 0) # close open position 
                    except:
                        pass
                    ib.sleep(10)
                    try:
                        trade_reporting() # final reporting
                    except:
                        pass
                    print("Session Stopped - No Connection.")
                    ib.disconnect()
                    break
        else:
            pass
    
if __name__ == "__main__": # if you run trader.py as python script
    # start trading session
    start_session()
    