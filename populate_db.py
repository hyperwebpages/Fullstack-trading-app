import ccxt
import sqlite3

import config

import pprint as pp

exchange = ccxt.binance({
    "apiKey": config.BINANCE_API_KEY,
    "secret": config.BINANCE_SECRET_KEY
})

# Load all markets
markets = exchange.load_markets()

# List all USDT pairs
usdt_pairs = [market for market in markets if 'USDT' in market and 'USDT:USDT' not in market]
pp.pprint(usdt_pairs)
pp.pprint(len(usdt_pairs))

#connection = sqlite3.connect('app.db')

#cursor = connection.cursor()

#cursor.execute("INSERT INTO stock (symbol, company) VALUES ('ABDE', 'Adobe Inc.')")
#cursor.execute("INSERT INTO stock (symbol, company) VALUES ('VZ', 'Verizon')")

#connection.commit()