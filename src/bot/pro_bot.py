import json
import time

import websocket

SYMBOL = "BNBUSDT"

# Trading parameters
BUY_DROP_PCT = 0.003
TAKE_PROFIT_PCT = 0.005
STOP_LOSS_PCT = 0.003

BALANCE = 1000.0
STATE = "NO_POSITION"

entry_price = None
position_qty = 0.0

# Candle storage
candles_1s = []
candles_5s = []

current_1s = None
current_5s = None


class ProBot:
    def __init__(self, name):
        self.name = name


    def run(self):
        print("ProBot is running...")
        # SOCKET = "wss://stream.binance.com:9443/ws/bnbusdt@trade"
        SOCKET = "wss://www.binance.th/gstream"

        ws = websocket.WebSocketApp(
            SOCKET,
            on_message=self.on_message,
            on_open=self.on_open
        )

        ws.run_forever()

    # ---------- ORDER STUB ----------
    def place_buy(self, price):
        global entry_price, position_qty
        position_qty = BALANCE / price
        entry_price = price
        print(f"[BUY] {price:.2f}")

    def place_sell(self, price):
        global BALANCE, entry_price, position_qty
        pnl = (price - entry_price) * position_qty
        BALANCE += pnl
        print(f"[SELL] {price:.2f} | PnL={pnl:.2f} Balance={BALANCE:.2f}")
        entry_price = None
        position_qty = 0.0

    # ---------- CANDLE BUILDER ----------
    def update_candle(self, price, timestamp, interval, current):
        bucket = timestamp - (timestamp % interval)
        current_time_str = time.strftime("%H:%M:%S", time.localtime())
        print(f"Current Time: {current_time_str}, Interval: {interval}, Timestamp: {timestamp}, Bucket: {bucket}, Current: {current}")

        # 1767763071 - (1767763071%5) = 1767763070
        # 1767763071 % 5 = 1
        # 1767763074 - (1767763074%5) = 1767763070
        # 1767763074 % 5 = 4

        if current is None or current["start"] != bucket:
            if current:
                return (
                    {
                        "start": bucket,
                        "open": price,
                        "high": price,
                        "low": price,
                        "close": price,
                    },
                    current,
                )
            else:
                return (
                    {
                        "start": bucket,
                        "open": price,
                        "high": price,
                        "low": price,
                        "close": price,
                    },
                    None,
                )

        current["high"] = max(current["high"], price)
        current["low"] = min(current["low"], price)
        current["close"] = price

        return current, None

    # ---------- STRATEGY ----------
    def strategy_on_5s_candle(self, candles):
        global STATE

        if len(candles) < 2:
            return

        last = candles[-1]
        prev = candles[-2]

        if STATE == "NO_POSITION":
            drop_pct = (prev["close"] - last["close"]) / prev["close"]
            print(f"Drop price: {drop_pct:.2f}")
            if drop_pct >= BUY_DROP_PCT:
                self.place_buy(last["close"])
                STATE = "IN_POSITION"

        elif STATE == "IN_POSITION":
            change_pct = (last["close"] - entry_price) / entry_price
            if change_pct >= TAKE_PROFIT_PCT or change_pct <= -STOP_LOSS_PCT:
                self.place_sell(last["close"])
                STATE = "NO_POSITION"

    # ---------- WEBSOCKET ----------
    def on_message(self, ws, message):
        global current_1s, current_5s

        data = json.loads(message)

        # print(data)

        # {'u': 17882443270, 's': 'BNBUSDT', 'b': '910.21000000', 'B': '2.86300000', 'a': '910.22000000', 'A': '43.31000000'}
        # {'e': 'trade', 'E': 1767760101363, 's': 'BNBUSDT', 't': 1373912974, 'p': '910.22000000', 'q': '0.02000000', 'T': 1767760101362, 'm': False, 'M': True}

        # Binance TH bookTicker example message:
        # {'stream': 'bnbusdt@bookTicker', 'data': {'u': 17882435944, 's': 'BNBUSDT', 'b': '910.21000000', 'B': '23.31100000', 'a': '910.22000000', 'A': '13.31700000'}}

        # price = float(data["p"])
        price = float(data["data"]["b"])
        ts = int(time.time())

        # 1-second candle
        # new_1s, closed_1s = self.update_candle(price, ts, 1, current_1s)
        # if closed_1s:
        #     candles_1s.append(closed_1s)
        #     # print(f"[1s] {closed_1s}")
        # current_1s = new_1s

        # 5-second candle
        new_5s, closed_5s = self.update_candle(price, ts, 5, current_5s)
        if closed_5s:
            candles_5s.append(closed_5s)
            print(f"[5s] {closed_5s}")
            self.strategy_on_5s_candle(candles_5s)

        current_5s = new_5s

    def on_open(self, ws):
        print("WebSocket connected")

        subscription_msg = {
            "method": "SUBSCRIBE",
            "params": [
                "bnbusdt@bookTicker"
            ],
            "id": 1
        }

        ws.send(json.dumps(subscription_msg))
