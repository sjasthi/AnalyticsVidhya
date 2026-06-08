# this is a yahoo stock API
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import yfinance as yf
import pandas as pd

app = FastAPI(title="Stock Market API")

# -----------------------------
# Request Model (for historical data)
# -----------------------------
class HistoricalRequest(BaseModel):
    symbol: str
    start_date: str
    end_date: str


# =========================================================
# 1. Company Information Endpoint
# =========================================================
@app.get("/company/{symbol}")
def get_company_info(symbol: str):
    stock = yf.Ticker(symbol)
    info = stock.info

    return {
        "symbol": symbol,
        "company_name": info.get("longName"),
        "business_summary": info.get("longBusinessSummary"),
        "industry": info.get("industry"),
        "sector": info.get("sector"),
        "country": info.get("country"),
        "website": info.get("website"),
        "employees": info.get("fullTimeEmployees"),
        "officers": info.get("companyOfficers"),
    }


# =========================================================
# 2. Stock Market Data Endpoint (Real-time)
# =========================================================
@app.get("/stock/{symbol}")
def get_stock_data(symbol: str):
    stock = yf.Ticker(symbol)
    data = stock.history(period="1d")

    if data.empty:
        return {"error": "No data found"}

    latest = data.tail(1).iloc[0]

    return {
        "symbol": symbol,
        "current_price": float(latest["Close"]),
        "open": float(latest["Open"]),
        "high": float(latest["High"]),
        "low": float(latest["Low"]),
        "volume": int(latest["Volume"]),
    }


# =========================================================
# 3. Historical Market Data Endpoint (POST)
# =========================================================
@app.post("/historical")
def get_historical_data(request: HistoricalRequest):
    stock = yf.Ticker(request.symbol)

    df = stock.history(start=request.start_date, end=request.end_date)

    if df.empty:
        return {"error": "No historical data found"}

    df.reset_index(inplace=True)

    return {
        "symbol": request.symbol,
        "data": df.to_dict(orient="records")
    }


# =========================================================
# 4. Analytical Insights Endpoint
# =========================================================
@app.post("/analysis")
def analyze_stock(request: HistoricalRequest):
    stock = yf.Ticker(request.symbol)
    df = stock.history(start=request.start_date, end=request.end_date)

    if df.empty:
        return {"error": "No data found for analysis"}

    df["Daily Return"] = df["Close"].pct_change()

    analysis = {
        "symbol": request.symbol,
        "mean_price": float(df["Close"].mean()),
        "max_price": float(df["Close"].max()),
        "min_price": float(df["Close"].min()),
        "volatility": float(df["Daily Return"].std()),
        "total_return": float((df["Close"].iloc[-1] / df["Close"].iloc[0]) - 1),
    }

    # Simple insight logic
    if analysis["volatility"] > 0.03:
        insight = "High volatility stock — higher risk."
    else:
        insight = "Stable stock — lower volatility."

    analysis["insight"] = insight

    return analysis