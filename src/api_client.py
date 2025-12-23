import time

import requests

from .config import API_KEY, BASE_URL, EXCHANGE_INFO_PATH, BOOK_TICKER_PATH, ACCOUNT_INFORMATION


def _get_timestamp():
    return int(round(time.time() * 1000))


class APIClient:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'X-API-KEY': API_KEY})

    def get_exchange_info(self):
        return self.session.get(f"{BASE_URL}{EXCHANGE_INFO_PATH}").json()

    def get_book_ticker(self):
        return self.session.get(f"{BASE_URL}{BOOK_TICKER_PATH}").json()

    def get_account(self):
        self.session.params = {'timestamp': _get_timestamp()}
        return self.session.get(f"{BASE_URL}{ACCOUNT_INFORMATION}").json()

    def place_order(self, data):
        return self.session.post(f"{BASE_URL}/api/v1/order", json=data).json()

    def get_order(self, order_id, symbol):
        return self.session.get(f"{BASE_URL}/api/v1/order", params={"orderId": order_id, "symbol": symbol}).json()

    def get_open_orders(self, symbol):
        return self.session.get(f"{BASE_URL}/api/v1/openOrders", params={"symbol": symbol}).json()
