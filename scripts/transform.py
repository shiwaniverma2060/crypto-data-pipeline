"""
PHASE 2: TRANSFORM
--------------------
Takes the most recent raw JSON file from data/raw/ and turns it into
a clean, analysis-ready table using pandas.

What "cleaning" means here (this is the part interviewers actually
ask about, so understand WHY each step exists):
  1. Select only the columns we care about (raw API gives 20+ fields,
     we don't need all of them).
  2. Rename columns to clean, consistent snake_case names.
  3. Convert types (e.g. last_updated string -> real datetime).
  4. Drop rows with missing critical fields (bad data shouldn't
     silently flow downstream).
  5. Add a pipeline metadata column (extracted_at) so every row is
     traceable to the run that produced it.
"""

import pandas as pd
import glob
import os
from datetime import datetime, timezone

RAW_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
PROCESSED_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")

COLUMNS_TO_KEEP = {
    "id": "coin_id",
    "symbol": "symbol",
    "name": "name",
    "current_price": "price_usd",
    "market_cap": "market_cap_usd",
    "market_cap_rank": "market_cap_rank",
    "total_volume": "volume_24h_usd",
    "price_change_percentage_24h": "price_change_pct_24h",
    "circulating_supply": "circulating_supply",
    "last_updated": "last_updated",
}


def get_latest_raw_file():
    """Finds the most recently created raw JSON file."""
    files = glob.glob(os.path.join(RAW_DATA_DIR, "crypto_raw_*.json"))
    if not files:
        raise FileNotFoundError("No raw files found. Run extract.py first.")
    return max(files, key=os.path.getctime)


def transform(raw_filepath):
    df = pd.read_json(raw_filepath)

    # 1 & 2: select + rename columns
    df = df[list(COLUMNS_TO_KEEP.keys())].rename(columns=COLUMNS_TO_KEEP)

    # 3: type conversion
    df["last_updated"] = pd.to_datetime(df["last_updated"], utc=True)

    # 4: drop rows missing critical fields (a coin with no price is useless data)
    before = len(df)
    df = df.dropna(subset=["coin_id", "price_usd", "market_cap_usd"])
    dropped = before - len(df)
    if dropped:
        print(f"[TRANSFORM] Dropped {dropped} rows with missing critical fields")

    # 5: pipeline metadata
    df["extracted_at"] = datetime.now(timezone.utc)

    return df


def save_processed_csv(df):
    os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    filepath = os.path.join(PROCESSED_DATA_DIR, f"crypto_processed_{timestamp}.csv")
    df.to_csv(filepath, index=False)
    print(f"[TRANSFORM] Saved {len(df)} clean rows to {filepath}")
    return filepath


if __name__ == "__main__":
    raw_file = get_latest_raw_file()
    print(f"[TRANSFORM] Reading {raw_file}")
    clean_df = transform(raw_file)
    save_processed_csv(clean_df)
