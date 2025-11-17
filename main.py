from fastapi import FastAPI
import yfinance as yf

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Stock API is running!"}

@app.get("/stock/{symbol}")
def get_stock(symbol: str):
    stock = yf.Ticker(symbol)
    info = stock.history(period="1d")
    if info.empty:
        return {"error": "Invalid symbol"}
    
    price = float(info["Close"].iloc[-1])
    return {"symbol": symbol.upper(), "price": price}
