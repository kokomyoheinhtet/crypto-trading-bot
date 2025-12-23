from flask import Flask, jsonify

from src.api_client import APIClient
from src.config import default_symbol, default_spend_pct
from src.exchange_info_service import ExchangeInfoService

app = Flask(__name__)

exchange_service = ExchangeInfoService()
api_client = APIClient()

@app.before_first_request
def startup_discover_symbol():
    found = exchange_service.discover_symbol(default_symbol)
    if not found:
        raise Exception(f"Symbol {default_symbol} not found in exchange info.")

@app.route("/api/v1/bot/buy", methods=["POST"])
def buy():
    # 1. Fetch ticker
    ticker = api_client.get_book_ticker()
    price = float(ticker["askPrice"]) if "askPrice" in ticker else None
    if not price:
        return jsonify({"error": "No ask price found."}), 400

    # 2. Check account balance
    account = api_client.get_account()
    balances = {b['asset']: float(b['free']) for b in account.get('balances', [])}
    usdt_balance = balances.get('USDT', 0)
    spend_amount = usdt_balance * default_spend_pct

    # 3. Calculate quantity to buy
    rules = exchange_service.get_trading_rules()
    min_qty = rules['minQty']
    step_size = rules['stepSize']
    min_notional = rules['minNotional']
    qty = max(min_qty, spend_amount / price)
    # Round down to step size
    qty = qty - (qty % step_size)
    if qty * price < min_notional:
        return jsonify({"error": "Order notional below minimum."}), 400

    # 4. Place market order
    order = api_client.place_order({
        "symbol": default_symbol,
        "side": "BUY",
        "type": "MARKET",
        "quantity": qty
    })
    order_id = order.get('orderId')
    if not order_id:
        return jsonify({"error": "Order placement failed.", "details": order}), 400

    # 5. Poll order status
    import time
    for _ in range(10):
        status = api_client.get_order(order_id, default_symbol)
        if status.get('status') in ["FILLED", "PARTIALLY_FILLED", "CANCELED", "EXPIRED"]:
            break
        time.sleep(1)

    # 6. Print stats
    new_account = api_client.get_account()
    new_balances = {b['asset']: float(b['free']) for b in new_account.get('balances', [])}
    btc_bought = new_balances.get('BTC', 0) - balances.get('BTC', 0)
    usdt_left = new_balances.get('USDT', 0)
    return jsonify({
        "old_balance": balances,
        "new_balance": new_balances,
        "btc_bought": btc_bought,
        "usdt_left": usdt_left,
        "order_status": status.get('status')
    })

if __name__ == "__main__":
    app.run(debug=True)
