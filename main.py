from fastapi import FastAPI, HTTPException, Header
import yfinance as yf
import pandas as pd

app = FastAPI(
    title="Stock API",
    description="Multi-symbol stock API with indicators + API key authentication",
    version="1.0.0"
)

# ============================================
# 🔐 AUTHENTICATION
# ============================================

API_KEY = "YOUR_SECRET_API_KEY"   # Change this before deploying

def verify_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return True

# ============================================
# 📌 HELPER — RSI calculation
# ============================================

def calc_rsi(series: pd.Series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()

    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return round(rsi.iloc[-1], 2)

# ============================================
# 📌 HELPER — MACD calculation
# ============================================

def calc_macd(series: pd.Series):
    ema12 = series.ewm(span=12).mean()
    ema26 = series.ewm(span=26).mean()

    macd_line = ema12 - ema26
    signal_line = macd_line.ewm(span=9).mean()

    return {
        "macd": round(macd_line.iloc[-1], 4),
        "signal": round(signal_line.iloc[-1], 4),
        "histogram": round((macd_line - signal_line).iloc[-1], 4)
    }

# ============================================
# 🔥 ENDPOINT 1 — Single symbol
# ============================================

@app.get("/stock/{symbol}")
def get_stock(symbol: str, authorized: bool = verify_key):
    stock = yf.Ticker(symbol)
    info = stock.history(period="1d")

    if info.empty:
        raise HTTPException(status_code=404, detail="Invalid symbol")

    close_price = float(info["Close"].iloc[-1])
    return {"symbol": symbol.upper(), "price": close_price}

# ============================================
# 🔥 ENDPOINT 2 — Multiple symbols at once
# ============================================

@app.post("/stocks")
def get_multiple_stocks(symbols: list[str], authorized: bool = verify_key):
    results = {}

    for sym in symbols:
        stock = yf.Ticker(sym)
        info = stock.history(period="1d")

        if info.empty:
            results[sym.upper()] = {"error": "Invalid symbol"}
        else:
            price = float(info["Close"].iloc[-1])
            results[sym.upper()] = {"price": price}

    return results

# ============================================
# 🔥 ENDPOINT 3 — Tech indicators (RSI, MACD)
# ============================================

@app.get("/stock/{symbol}/indicators")
def indicators(symbol: str, authorized: bool = verify_key):
    stock = yf.Ticker(symbol)
    data = stock.history(period="3mo")

    if data.empty:
        raise HTTPException(status_code=404, detail="Invalid symbol")

    close = data["Close"]

    return {
        "symbol": symbol.upper(),
        "rsi": calc_rsi(close),
        "macd": calc_macd(close)
    }

# ============================================
# 🔥 ROOT — Test if API works
# ============================================

@app.get("/")
def home():
    return {"message": "Stock API Online", "features": ["multi-symbol", "rsi", "macd", "auth"]}
