import asyncio
import json

import websockets


class ProBot:
    def __init__(self, name):
        self.name = name

    def run(self):
        print(f"ProBot {self.name} is now running with advanced capabilities!")
        asyncio.get_event_loop().run_until_complete(self._subscribe_binance_ws())

    async def _subscribe_binance_ws(self):
        uri = "wss://www.binance.th/gstream"
        subscription_msg = {
            "method": "SUBSCRIBE",
            "params": [
                "bnbusdt@bookTicker"
            ],
            "id": 1
        }

        async with websockets.connect(uri) as websocket:
            print("Connected to Binance Thailand WebSocket")

            # Send the subscription message
            await websocket.send(json.dumps(subscription_msg))
            print(f"Sent subscription message: {subscription_msg}")

            # Listen for incoming messages
            while True:
                try:
                    message = await websocket.recv()
                    data = json.loads(message)
                    # print(f"Received message: {data}")
                    self._process_message(data)
                except websockets.ConnectionClosed:
                    print("Connection closed")
                    break



    def _process_message(self, message=None):
        data = message.get('data', {})
        bid = float(data.get('b', 0))
        ask = float(data.get('a', 0))
        spread = ask - bid
        print(f"Best Bid: {bid}, Best Ask: {ask}, Spread: {spread:.4f}")
