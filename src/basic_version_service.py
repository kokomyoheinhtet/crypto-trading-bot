from src.api_client import APIClient


class BasicVersionService:
    def __init__(self):
        self.api = APIClient()

    def get_exchange_info(self):
        return self.api.get_exchange_info()

    def get_book_ticker(self):
        return self.api.get_book_ticker()

    def get_account(self):
        return self.api.get_account()
