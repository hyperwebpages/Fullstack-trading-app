import sqlite3
import config

connection = sqlite3.connect(config.DB_FILE)

cursor = connection.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS cryptos (
        id INTEGER PRIMARY KEY,
        symbol TEXT NOT NULL UNIQUE,
        symboshort TEXT NOT NULL UNIQUE,
        exchange TEXT NOT NULL        
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS crypto_prices (
               id INTEGER PRIMARY KEY,
               crypto_id INTEGER,
               timeframe NOT NULL,
               timestamp NOT NULL,
               open NOT NULL,
               high NOT NULL,
               low NOT NULL,
               close NOT NULL,
               volume NOT NULL,
               UNIQUE(crypto_id, timeframe, timestamp),
               FOREIGN KEY (crypto_id) REFERENCES cryptos (id) 
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS strategy (
        id INTEGER PRIMARY KEY,
        name NOT NULL
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS crypto_strategy (
        id INTEGER PRIMARY KEY,
        crypto_id INTEGER NOT NULL,
        strategy_id INTEGER NOT NULL,
        FOREIGN KEY (crypto_id) REFERENCES cryptos (id)
        FOREIGN KEY (strategy_id) REFERENCES strategy (id)
    )
""")

try:
    strategies  = ['opening_range_breakout', 'opening_range_breakdown']
    for strategy in strategies:
        cursor.execute("""
            INSERT INTO strategy(name) VALUES (?)
        """, (strategy,))
    connection.commit()
except Exception as e:
    print(f"An error occurred: {e}")

connection.commit()
