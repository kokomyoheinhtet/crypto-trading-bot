from .api_client import APIClient
from .config import default_symbol


class ExchangeInfoService:
    def __init__(self):
        self.api = APIClient()
        self.symbol_info = None
        self.trading_rules = None

    def discover_symbol(self, symbol=default_symbol):
        info = self.api.get_exchange_info()
        symbols = info.get('symbols', [])
        for s in symbols:
            if s['symbol'] == symbol:
                self.symbol_info = s
                self.trading_rules = self._extract_trading_rules(s)
                return True
        return False

    def _extract_trading_rules(self, symbol_info):
        filters = symbol_info.get('filters', [])
        rules = {}
        for f in filters:
            if f['filterType'] == 'LOT_SIZE':
                rules['minQty'] = float(f['minQty'])
                rules['stepSize'] = float(f['stepSize'])
            if f['filterType'] == 'MIN_NOTIONAL':
                rules['minNotional'] = float(f['minNotional'])
        return rules

    def get_trading_rules(self):
        return self.trading_rules

