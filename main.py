import sqlite3, config
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime

app = FastAPI()
templates  =  Jinja2Templates(directory = config.JINJA_FOLDER)


# Define the custom filter
def remove_pattern(value: str) -> str:
    patterns = ["DOWN/", "UP/", "/"]
    
    # Remove each pattern from the string
    for pattern in patterns:
        value = value.replace(pattern, "")
    return value

# Register the custom filter with Jinja2
templates.env.filters["remove_pattern"] = remove_pattern


@app.get("/")
def index(request: Request):
    crypto_filter = request.query_params.get('filter', False)

    connection = sqlite3.connect(config.DB_FILE)
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    if crypto_filter == 'new_closing_highs':
        cursor.execute("""
            SELECT * FROM (
                SELECT symbol, exchange, symboshort, crypto_id, max(close), timestamp
                FROM crypto_prices join cryptos on cryptos.id = crypto_prices.crypto_id
                GROUP BY crypto_id
                ORDER BY symbol
            ) WHERE timestamp = ?  
        """, (datetime.now().replace(hour=0, minute=0, second=0, microsecond=0),))
    else:

        cursor.execute("""
            SELECT id, symbol, exchange, symboshort FROM cryptos ORDER BY exchange, symbol
        """)

    rows = cursor.fetchall()
    context = {"request":request, "cryptos":rows}
    
    return templates.TemplateResponse("index.html", context)

@app.get("/crypto/{symboshort}")
def crypto_detail(request: Request, symboshort):
    connection = sqlite3.connect(config.DB_FILE)
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute("""
        SELECT * FROM strategy
    """)

    strategies = cursor.fetchall()


    cursor.execute("""
        SELECT id, symbol, exchange, symboshort FROM cryptos WHERE symboshort = ?
    """, (symboshort,))

    row = cursor.fetchone()

    cursor.execute("""
        SELECT * FROM crypto_prices WHERE crypto_id = ? ORDER BY timestamp DESC
    """, (row['id'],))

    prices = cursor.fetchall()

    context = {"request":request, "crypto":row, "prices":prices, "strategies":strategies}
    
    return templates.TemplateResponse("crypto_detail.html", context)

@app.post("/apply_strategy")
def apply_strategy(strategy_id:int = Form(...), crypto_id: int = Form(...)):
    connection = sqlite3.connect(config.DB_FILE)
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO crypto_strategy (crypto_id, strategy_id) VALUES (?,?)              
    """, (crypto_id, strategy_id))

    connection.commit()

    return RedirectResponse(url=f"/strategy/{strategy_id}", status_code=303)

@app.get("/strategy/{strategy_id}")
def strategy(request:Request, strategy_id):
    connection = sqlite3.connect(config.DB_FILE)
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, name
        FROM strategy 
        WHERE id = ?                  
    """, (strategy_id,))

    strategy = cursor.fetchone()

    cursor.execute("""
        SELECT symbol, exchange, symboshort, crypto_strategy.id as crypto_strategy_id FROM cryptos JOIN crypto_strategy on crypto_strategy.crypto_id = cryptos.id  
        WHERE strategy_id = ?
        ORDER BY exchange, symbol
    """, (strategy_id,))

    cryptos = cursor.fetchall()

    return templates.TemplateResponse("strategy.html", {"request": request, "cryptos":cryptos, "strategy":strategy})

@app.post("/delete_crypto_strategy")
def delete_crypto_strategy(crypto_strategy_id: int = Form(...)):
    connection = sqlite3.connect(config.DB_FILE)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    

    cursor.execute("""
        SELECT strategy_id
        FROM crypto_strategy 
        WHERE id = ?                  
    """, (crypto_strategy_id,))

    strategy = cursor.fetchone()


    try:
        cursor.execute("DELETE FROM crypto_strategy WHERE id = ?", (crypto_strategy_id,))
        connection.commit()
    except Exception as e:
        connection.rollback()
        raise HTTPException(status_code=400, detail=f"Could not delete record: {e}")
    finally:
        connection.close()
    returnurl = f"/strategy/{strategy['strategy_id']}" 
    return RedirectResponse(url=returnurl, status_code=303)  # Redirect back to the listing page or another appropriate page