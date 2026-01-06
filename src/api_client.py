import hashlib
import hmac
import time

import requests

from .config import API_KEY, API_SECRET, BASE_URL, EXCHANGE_INFO_PATH, BOOK_TICKER_PATH, ACCOUNT_INFORMATION


def _get_timestamp():
    return int(round(time.time() * 1000))


class APIClient:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'X-MBX-APIKEY': API_KEY})

    def get_exchange_info(self):
        return self.session.get(f"{BASE_URL}{EXCHANGE_INFO_PATH}").json()

    def get_book_ticker(self):
        return self.session.get(f"{BASE_URL}{BOOK_TICKER_PATH}").json()

    def get_account(self, params=None):
        if params is None:
            params = {}
        params['timestamp'] = _get_timestamp()
        params['signature'] = self._generate_signature(params=params)
        self.session.params = params

        return self.session.get(f"{BASE_URL}{ACCOUNT_INFORMATION}").json()

    def place_order(self, params=None):
        if params is None:
            params = {}
        params['timestamp'] = _get_timestamp()
        params['signature'] = self._generate_signature(params=params)
        self.session.params = params
        return self.session.post(f"{BASE_URL}/api/v1/order").json()

    def get_order(self, order_id, symbol):
        return self.session.get(f"{BASE_URL}/api/v1/order", params={"orderId": order_id, "symbol": symbol}).json()

    def get_open_orders(self, params=None):
        if params is None:
            params = {}
        params['timestamp'] = _get_timestamp()
        params['signature'] = self._generate_signature(params=params)
        self.session.params = params
        return self.session.get(f"{BASE_URL}/api/v1/openOrders").json()

    def _generate_signature(self, params=None):
        msg = ""
        for key, value in params.items():
            if key == "signature":
                continue
            else:
                msg += f"&{key}={value}"

        msg = msg[1:] if msg.startswith("&") else msg
        hash_ = hmac.new(API_SECRET.encode(), msg.encode(), hashlib.sha256)
        signature = hash_.hexdigest()
        return signature
