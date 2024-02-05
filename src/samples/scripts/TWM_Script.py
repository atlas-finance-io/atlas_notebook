from binance import ThreadedWebsocketManager
import time

def stream_data(msg):
    ''' define how to process incoming WebSocket messages '''
    print(msg)

# initialize and start the WebSocket
twm = ThreadedWebsocketManager()
twm.start()

# subscribe to the stream
twm.start_symbol_miniticker_socket(callback = stream_data, symbol = "BTCUSDT")

# stop the Websocket/Stream after 20 seconds
while True:
    time.sleep(20)
    twm.stop()
    break