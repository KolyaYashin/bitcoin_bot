from config import API_KEY, SECRET_KEY
from binance.client import Client

client = Client(API_KEY, SECRET_KEY)

exchange_info = client.get_exchange_info()

every_pair_set = []
usdt_pairs_set = []

for s in exchange_info['symbols']:
    symbol = s['symbol']
    every_pair_set.append(symbol)
    if symbol.endswith('USDT'):
        usdt_pairs_set.append(symbol)


id2settings = {}