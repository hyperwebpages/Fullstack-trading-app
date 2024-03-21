import ccxt
import sqlite3

import config

import pprint as pp
import pandas as pd

def fetch(ticker, tickerperiod, tickerinterval, ticker_id):
    """
    Fetch data for Crypto for the past year and save in the specified database.
    """
    bars = exchange.fetch_ohlcv(ticker, timeframe=tickerinterval, limit=tickerperiod)
    df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
 
    for row in df.itertuples():
        cursor.execute("""
            INSERT OR IGNORE INTO crypto_prices (crypto_id, timeframe, timestamp, open, high, low, close, volume)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (ticker_id, tickerinterval, row.timestamp.strftime('%Y-%m-%d %H:%M:%S'), row.open, row.high, row.low, row.close, row.volume))

    
    print(f"Data for {ticker} saved to table")
    return df

exchange = ccxt.binance({
    "apiKey": config.BINANCE_API_KEY,
    "secret": config.BINANCE_SECRET_KEY
    })

connection = sqlite3.connect(config.DB_FILE)
connection.row_factory = sqlite3.Row

cursor = connection.cursor()

cursor.execute("""
    SELECT id, symbol FROM cryptos WHERE exchange == "binance"
""")

rows =  cursor.fetchall()

symbols = []
stock_dict = {}

for row in rows:
    symbol = row['symbol']
    symbols.append(symbol)
    stock_dict[symbol] = row['id']

    tickerdaily = fetch(symbol, 50, '1d', stock_dict[symbol])

connection.commit()