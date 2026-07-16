"""
PHASE 1: EXTRACT
-----------------
Pulls live market data for the top 100 cryptocurrencies from the
CoinGecko public API (free, no API key required) and saves the raw
JSON response to disk with a timestamp.

Why we save the RAW response first (before cleaning it):
  - This is standard data engineering practice. You always keep an
    unmodified copy of what the source gave you, so if your
    transform logic has a bug later, you can re-run it without
    having to call the API again.
"""

import requests
import json
import os
from datetime import datetime, timezone

# CoinGecko free endpoint: top 100 coins by market cap, priced in USD
API_URL = "https://api.coingecko.com/api/v3/coins/markets"

PARAMS = {
    "vs_currency": "usd",
    "order": "market_cap_desc",
    "per_page": 100,
    "page": 1,
    "sparkline": "false",
    "price_change_percentage": "24h",
}

RAW_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")


def extract_market_data():
    """Calls the CoinGecko API and returns the parsed JSON response."""
    response = requests.get(API_URL, params=PARAMS, timeout=30)
    response.raise_for_status()  # crashes loudly if the API call fails
    return response.json()


def save_raw_json(data):
    """Saves the raw API response to data/raw/ with a UTC timestamp filename."""
    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    filepath = os.path.join(RAW_DATA_DIR, f"crypto_raw_{timestamp}.json")

    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)

    print(f"[EXTRACT] Saved {len(data)} records to {filepath}")
    return filepath


if __name__ == "__main__":
    data = extract_market_data()
    save_raw_json(data)
