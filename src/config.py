import os

from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('API_KEY', '')
API_SECRET = os.getenv('API_SECRET', '')
BASE_URL = os.getenv('API_BASE_URL', '')

SYMBOL = os.getenv('SYMBOL', '')

EXCHANGE_INFO_PATH = os.getenv('EXCHANGE_INFO_PATH', '')
BOOK_TICKER_PATH = os.getenv('BOOK_TICKER_PATH', '')
ACCOUNT_INFORMATION = os.getenv('ACCOUNT_INFORMATION', '')

# Trading parameters
default_symbol = os.getenv('SYMBOL', 'BTCUSDT')
default_spend_pct = float(os.getenv('SPEND_PCT', '1.0'))  # 1.0 = 100%, 0.1 = 10%

