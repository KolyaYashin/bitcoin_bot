from config import API_KEY, SECRET_KEY
from binance.client import Client

client = Client(API_KEY, SECRET_KEY)

exchange_info = client.get_exchange_info()

every_pair_set = set([])
usdt_pairs_set = set([])

for s in exchange_info['symbols']:
    symbol = s['symbol']
    every_pair_set.add(symbol)
    if symbol.endswith('USDT'):
        usdt_pairs_set.add(symbol)


id2settings = {}