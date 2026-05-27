# FinAPI — Stock Price REST API

A lightweight REST API built with Python and Flask that returns real-time stock market data using Yahoo Finance (`yfinance`). Built as part of the M1/M2 Finance Quantitative program at ITBS.

## Tech Stack

- Python 3.10+
- Flask
- yfinance
- Git

## Project Structure
finapi/
├── finapi/
│   ├── init.py
│   ├── app.py        # Flask app and endpoints
│   └── prices.py     # Market data logic (yfinance)
├── tests/
│   └── test_app.py
├── .gitignore
├── requirements.txt
└── README.md
## Installation

```bash
# Clone the project
git clone <your-repo-url>
cd finapi

# Create and activate virtual environment
python -m venv .venv
source .venv/Scripts/activate  # Windows
# source .venv/bin/activate    # Mac/Linux

# Install dependencies
pip install -r requirements.txt
```

## Run the Server

```bash
python -m finapi.app
```

Server runs at `http://localhost:5000`

## Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Check if the API is running |
| GET | `/price/<ticker>` | Get the latest closing price |
| GET | `/history/<ticker>?days=N` | Get price history (1–365 days) |

## Usage Examples

```bash
# Health check
curl http://localhost:5000/health

# Latest price for Apple
curl http://localhost:5000/price/AAPL

# 5-day history for Microsoft
curl "http://localhost:5000/history/MSFT?days=5"

# Error handling — invalid ticker
curl -i http://localhost:5000/price/ZZZZZ

# Error handling — invalid parameter
curl -i "http://localhost:5000/history/AAPL?days=abc"
```

## Sample Response

```json
{
  "ticker": "AAPL",
  "date": "2026-05-26",
  "close": 308.33,
  "currency": "USD"
}
```

## Author

Molka — EPT, M1 Finance Quantitative