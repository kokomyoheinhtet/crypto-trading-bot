from src.client.api_client import APIClient


class BasicVersionService:
    def __init__(self):
        self.api = APIClient()

    def get_exchange_info(self):
        return self.api.get_exchange_info()

    def get_book_ticker(self):
        return self.api.get_book_ticker()

    def get_account(self):
        return self.api.get_account()

    def get_open_orders(self, params):
        return self.api.get_open_orders(params)

    def place_order(self, params):
        return self.api.place_order(params)

    def delete_open_orders(self, params):
        return self.api.delete_open_orders(params)
