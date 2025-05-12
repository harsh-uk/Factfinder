import os
import requests
from summarizer.config import ALPHAVANTAGE_API_KEY
API_KEY = ALPHAVANTAGE_API_KEY
BASE_URL = "https://www.alphavantage.co/query"

def search_symbol(company_name: str) -> str:
    # Fallback map for popular companies
    known = {
        "apple": "AAPL",
        "microsoft": "MSFT",
        "amazon": "AMZN",
        "meta": "META",
        "facebook": "META",
        "alphabet": "GOOGL",
        "google": "GOOGL",
        "tesla": "TSLA",
        "netflix": "NFLX",
        "nvidia": "NVDA"
    }
    key = company_name.lower()
    if key in known:
        return known[key]

    params = {
        "function": "SYMBOL_SEARCH",
        "keywords": company_name,
        "apikey": API_KEY
    }
    response = requests.get(BASE_URL, params=params)
    matches = response.json().get("bestMatches", [])
    if matches:
        return matches[0].get("1. symbol")
    return None

def get_quarterly_financials(symbol: str) -> dict:
    params = {
        "function": "INCOME_STATEMENT",
        "symbol": symbol,
        "apikey": API_KEY
    }
    response = requests.get(BASE_URL, params=params)
    data = response.json()

    result = {}
    for report in data.get("quarterlyReports", []):
        date = report["fiscalDateEnding"]
        year, month = map(int, date.split("-")[:2])
        quarter = f"Q{(month - 1) // 3 + 1}"
        revenue = float(report.get("totalRevenue", 0))
        profit = float(report.get("netIncome", 0))
        result.setdefault(str(year), {})[quarter] = {
            "revenue": revenue,
            "profit": profit
        }

    return result
