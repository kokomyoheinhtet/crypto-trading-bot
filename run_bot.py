import math

from src.basic_version_service import BasicVersionService
from src.config import SYMBOL


def ask_user_input(message=None):
    print()
    user_input = input(message + "...(q to quit)\n") if message else input("Press Enter to continue...(q to quit)")
    print()
    if user_input.lower() == 'q':
        exit(0)
    else:
        return user_input


def round_step_size(quantity, step_size):
    return math.floor(quantity / step_size) * step_size


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
    balances = account_info['balances']

    # Convert balances to a more usable format
    balances = {b["asset"]: b["free"] for b in balances}
    usdtBalance = float(balances.get("USDT", 0))

    print("Account Balances:")
    for asset, free_balance in balances.items():
        print(f"{asset}: {free_balance}")

    percentToBuy = ask_user_input(
        message="How many percent of USDT to spend on buy order?")
    buy_ = usdtBalance * (float(percentToBuy) / 100)
    print(f"User chose to spend {percentToBuy}% of USDT balance on buy order which is {buy_} USDT")

    ask_user_input()

    # 3. Place a Market order
    price_ = float(askPrice) - 5
    quantity_ = buy_ / price_
    quantity_ = round_step_size(quantity_, stepSize)
    quantity_ = float(f"{quantity_:.8f}")  # Format to avoid floating point issues

    print(f"Placing LIMIT BUY order for {quantity_} {SYMBOL} at price {price_}")
    ask_user_input()

    placed_order = service.place_order(params={
        "symbol": SYMBOL,
        "side": "BUY",
        "type": "LIMIT",
        "price": price_,
        "quantity": quantity_,
        "timeInForce": "GTC"
    })

    # Placed Order: {'symbol': 'BNBUSDT', 'orderId': 10703322363, 'clientOrderId': '8QMasFtsfXem3qM9IfJnmn', 'transactTime': 1767693942327, 'price': '907.61000000', 'origQty': '0.01600000', 'executedQty': '0.00000000', 'cumulativeQuoteQty': '0.00000000', 'status': 'NEW', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'fills': []}
    print(f"Placed Order: {placed_order}")

    while True:
        order_status = service.get_open_orders(params={'symbol': SYMBOL})
        print(f"Open Orders: {order_status}")
        # Open Orders: [{'symbol': 'BNBUSDT', 'orderId': 10703322363, 'clientOrderId': '8QMasFtsfXem3qM9IfJnmn', 'price': '907.61000000', 'origQty': '0.01600000', 'executedQty': '0.00000000', 'cumulativeQuoteQty': '0.00000000', 'status': 'NEW', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'time': 1767693942327, 'updateTime': None, 'isWorking': None, 'origQuoteOrderQty': '0.00000000'}]

        ask_user_input()
