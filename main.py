from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import yfinance as yf

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html>
        <head>
            <title><h1 style="text-align: center;">My First Stock API</h1></title>
            <style>
                body { font-family: Arial; padding: 40px; }
                button {
                    padding: 12px 20px;
                    margin: 8px;
                    background: #4CAF50;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    cursor: pointer;
                }
                input {
                    padding: 8px;
                    font-size: 16px;
                    margin-right: 8px;
                }
            </style>
        </head>
        <body>
            <h1>📈 Stock API</h1>
            <p>Enter a ticker symbol (AAPL, TSLA, AMZN...)</p>

            <input id="symbol" placeholder="AAPL" />
            <button onclick="getPrice()">Get Price</button>

            <pre id="output"></pre>

            <script>
                async function getPrice() {
                    const symbol = document.getElementById('symbol').value;
                    const response = await fetch(`/price/${symbol}`);
                    const data = await response.json();
                    document.getElementById('output').textContent = JSON.stringify(data, null, 2);
                }
            </script>
        </body>
    </html>
    """

@app.get("/price/{symbol}")
def get_price(symbol: str):
    ticker = yf.Ticker(symbol)
    data = ticker.history(period="1d")
    if data.empty:
        return {"error": "Invalid symbol"}
    price = data["Close"].iloc[-1]
    return {"symbol": symbol.upper(), "price": float(price)}
