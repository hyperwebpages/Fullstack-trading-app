-- SQLite
SELECT symbol, exchange, symboshort, crypto_id, max(close), timestamp
FROM crypto_prices join cryptos on cryptos.id = crypto_prices.crypto_id
GROUP BY crypto_id
ORDER BY timestamp DESC