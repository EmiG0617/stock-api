# main.py
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
import yfinance as yf
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow frontend JS to call API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for testing; restrict in production
    allow_methods=["*"],
    allow_headers=["*"]
)

# Homepage
@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html>
    <head>
        <title>Stock API Graph</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body {
                background-color: black;
                color: white;
                font-family: sans-serif;
                text-align: center;
            }
            input, button {
                padding: 5px;
                margin: 10px auto;
                display: block;
                background-color: #222;
                color: white;
                border: 1px solid #555;
                border-radius: 5px;
            }
            canvas {
                margin-top: 20px;
                background-color: #111; /* makes the chart area black */
            }
             /* 🌟 NEW — side-by-side price stats */
            .price-container {
                display: flex;
                justify-content: center;
                gap: 40px;
                margin-top: 10px;
                margin-bottom: 10px;
            }
            .price-box {
                background-color: #222;
                padding: 10px 20px;
                border-radius: 8px;
                border: 1px solid #444;
                font-size: 16px;
                font-weight: bold;
                min-width: 150px;
            }
        </style>

        <h1>📈 My Stock API</h1>

        <input id="symbol" placeholder="AAPL">
        <button onclick="drawGraph()">Show Graph</button>

        <!-- 🌟 NEW — 3 Price Stats side-by-side -->
        <div class="price-container">
            <p id="weekLow" class="price-box"></p>
            <p id="weekHigh" class="price-box"></p>
            <p id="currentPrice" class="price-box"></p>
        </div>
        <canvas id="stockChart" width="600" height="250"></canvas>
        <script>
            let chart;

            async function drawGraph() {
                const symbol = document.getElementById('symbol').value.toUpperCase();
                const response = await fetch(`/intraday/${symbol}`);
                const data = await response.json();
                const lastPrice = data.prices[data.prices.length - 1];
                const priceMin = Math.min(...data.prices);
                const priceMax = Math.max(...data.prices);
                document.getElementById('weekLow').textContent = `52-week low: $${priceMin.toFixed(2)}`;
                document.getElementById('weekHigh').textContent = `52-week high: $${priceMax.toFixed(2)}`;
                document.getElementById('currentPrice').textContent = `Current Price: $${lastPrice.toFixed(2)}`;

                const ctx = document.getElementById('stockChart').getContext('2d');
                if(chart) { chart.destroy(); }

                chart = new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: data.times,
                        datasets: [{
                            label: symbol + " Price",
                            data: data.prices,
                            borderColor: 'white', // bright color for visibility
                            backgroundColor: 'rgba(0,255,255,0.2)',
                            fill: false,
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: { labels: { color: 'white' } }
                        },
                        scales: {
                            x: { ticks: { color: 'white' }, title: { display: true, text: 'Time', color: 'white' } },
                            y: { ticks: { color: 'white' }, title: { display: true, text: 'Price ($)', color: 'white' } }
                        }
                    }
                });
            }

            // Trigger Enter key
            document.getElementById('symbol').addEventListener("keypress", function(event){
                if(event.key === "Enter") drawGraph();
            });
        </script>

    </body>
    </html>
    """

# Intraday endpoint
@app.get("/intraday/{symbol}")
def intraday(symbol: str):
    ticker = yf.Ticker(symbol)
    data = ticker.history(period="1y", interval="1m")

    times = [t.strftime("%H:%M") for t in data.index]
    prices = [float(p) for p in data['Close']]

    return JSONResponse({"times": times, "prices": prices})
