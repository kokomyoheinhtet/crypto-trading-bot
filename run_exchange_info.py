from src.basic_version_service import BasicVersionService
from src.config import SYMBOL


def ask_user_input():
    print()
    user_input = input("Press Enter to continue...(q to quit)")
    print()
    if user_input.lower() == 'q':
        exit(0)
    else:
        return user_input


if __name__ == "__main__":
    print("Starting exchange info service")

    service = BasicVersionService()

    # 0. Discover symbol
    exchangeInfo = service.get_exchange_info()
    print("Exchange info API Success")

    exchangeInfoSymbols = exchangeInfo['symbols']
    print(f"Exchange Info Symbols: {len(exchangeInfoSymbols)} found")
    print()

    minQty, stepSize, minNotional = None, None, None
    for exchangeInfoSymbol in exchangeInfoSymbols:
        if exchangeInfoSymbol['symbol'] == SYMBOL:

            symbolFilters = exchangeInfoSymbol['filters']
            for symbolFilter in symbolFilters:
                if symbolFilter['filterType'] == 'LOT_SIZE':
                    minQty, stepSize = float(symbolFilter['minQty']), float(symbolFilter['stepSize'])
                elif symbolFilter['filterType'] == 'MIN_NOTIONAL':
                    minNotional = float(symbolFilter['minNotional'])

    print(f"Symbol: {SYMBOL}")
    print(f"Min Qty: {minQty}")
    print(f"Step Size: {stepSize}")
    print(f"Min Notional: {minNotional}")
    ask_user_input()

    # 1. Fetch ticker via REST
    bookTickers = service.get_book_ticker()
    bidPrice, askPrice = None, None

    for bookTicker in bookTickers:
        if bookTicker['symbol'] == SYMBOL:
            bidPrice, askPrice = bookTicker['bidPrice'], bookTicker['askPrice']

    print(f"Bid Price: {bidPrice}")
    print(f"Ask Price: {askPrice}")

    ask_user_input()

    # 2. Check account balance
    account_info = service.get_account()

    print(account_info)

# Wait for user input to print
# user_input = input("Press Enter to continue...")
# print(f"User input: {user_input}")

# service = ExchangeInfoService()
# try:
#     result = service.fetch_exchange_info()
#     print("Exchange Info Response:")
#     print(result)
# except Exception as e:
#     print(f"Error fetching exchange info: {e}")

