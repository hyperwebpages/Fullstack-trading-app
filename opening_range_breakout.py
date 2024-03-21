import sqlite3, config
import ccxt
import pandas as pd
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime, date

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
    SELECT id FROM strategy WHERE name='opening_range_breakout'
""")

strategy_id = cursor.fetchone()['id']

cursor.execute("""
    SELECT symbol, exchange, symboshort, cryptos.id as cryptos_id FROM cryptos
    join crypto_strategy on crypto_strategy.crypto_id = cryptos.id
    WHERE crypto_strategy.strategy_id = ?
""", (strategy_id,))

cryptos =  cursor.fetchall()

current_date = date.today().isoformat()
start_minute_bar = f"{current_date} 00:00:00"
end_minute_bar = f"{current_date} 00:15:00"

symbols = []
stock_dict = {}

for crypto in cryptos:
    symbol = crypto['symbol']
    symbols.append(symbol)
    stock_dict[symbol] = crypto['cryptos_id']

    tickermins = fetch(symbol, 14400, '1m', stock_dict[symbol])

    opening_range_mask = (tickermins.timestamp >= start_minute_bar) & (tickermins.timestamp <= end_minute_bar)
    opening_range_bars = tickermins.loc[opening_range_mask]
    print(opening_range_bars)

    opening_range_low = opening_range_bars['low'].min()
    opening_range_high = opening_range_bars['high'].max()
    opening_range = opening_range_high - opening_range_low

    print(opening_range_low)
    print(opening_range_high)
    print(opening_range)

    after_opening_range_mask = (tickermins.timestamp > end_minute_bar)
    after_opening_range_bars = tickermins.loc[after_opening_range_mask]

    print(after_opening_range_bars)

    after_opening_range_breakout = after_opening_range_bars[after_opening_range_bars['close'] > opening_range_high]

    if not after_opening_range_breakout.empty:
        print(after_opening_range_breakout)
        limit_price = after_opening_range_breakout.iloc[0]['close']
        print(limit_price)
        print(f"placing order for {symbol} at {limit_price}, closed above {opening_range_high} at {after_opening_range_breakout.iloc[0]}")


connection.commit()


