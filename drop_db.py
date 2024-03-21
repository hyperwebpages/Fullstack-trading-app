import sqlite3
import config

connection = sqlite3.connect(config.DB_FILE)

cursor = connection.cursor()

cursor.execute("""
    DROP TABLE cryptos
""")

cursor.execute("""
    DROP TABLE crypto_prices
""")

connection.commit()