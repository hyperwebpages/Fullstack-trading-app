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

connection = sqlite3.connect(config.DB_FILE)
connection.row_factory = sqlite3.Row

cursor = connection.cursor()

cursor.execute("""
    SELECT symbol, exchange FROM cryptos
""")

rows = cursor.fetchall()
symbols  = [row['symbol'] for row in rows]

for market in markets:
    if 'USDT' in market and 'USDT:USDT' not in market:
        if market not in symbols:
            cexchange = 'binance'
            print(f"Added new crypto {market} from {cexchange}")
            if market[:5] == 'USDT/': 
                modified_ticker = market[5:] + "_short"
            elif market[-5:] == '/USDT':
                modified_ticker = market[:-5] + "_long"
            print(modified_ticker)            
            cursor.execute("INSERT INTO cryptos (symbol, exchange, symboshort) VALUES (?, ?, ?)", (market, cexchange, modified_ticker))

connection.commit()