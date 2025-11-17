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
        </style>
    </head>
    <body>
        <h1>📈 My Stock API</h1>
        <p>Enter a ticker symbol and press Enter or click "Show Graph"</p>
        <input id="symbol" placeholder="AAPL">
        <button onclick="drawGraph()">Show Graph</button>
        <canvas id="stockChart" width="800" height="400"></canvas>
        <script>
            let chart;

            async function drawGraph() {
                const symbol = document.getElementById('symbol').value.toUpperCase();
                const response = await fetch(`/intraday/${symbol}`);
                const data = await response.json();

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
    data = ticker.history(period="1d", interval="5m")

    times = [t.strftime("%H:%M") for t in data.index]
    prices = [float(p) for p in data['Close']]

    return JSONResponse({"times": times, "prices": prices})
