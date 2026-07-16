"""
PHASE 4: LOAD
--------------
Loads the validated, clean CSV into your Supabase Postgres database
(this is your free cloud data warehouse).

We use an "append" strategy into a raw table: every pipeline run adds
new rows with a timestamp, rather than overwriting. This mirrors how
real warehouses work - you keep history, and let dbt (Phase 5) build
clean "current state" views on top of the raw history.
"""

import pandas as pd
import glob
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()  # reads the .env file for your DB connection string

PROCESSED_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")
TABLE_NAME = "raw_crypto_prices"


def get_latest_processed_file():
    files = glob.glob(os.path.join(PROCESSED_DATA_DIR, "crypto_processed_*.csv"))
    if not files:
        raise FileNotFoundError("No processed files found. Run transform.py first.")
    return max(files, key=os.path.getctime)


def load_to_supabase(df):
    db_url = os.getenv("SUPABASE_DB_URL")
    if not db_url:
        raise EnvironmentError(
            "SUPABASE_DB_URL not found. Make sure your .env file exists and "
            "contains SUPABASE_DB_URL=<your connection string>."
        )

    engine = create_engine(db_url)

    df.to_sql(
        TABLE_NAME,
        engine,
        if_exists="append",   # append = keep history across runs
        index=False,
    )
    print(f"[LOAD] Inserted {len(df)} rows into '{TABLE_NAME}' in Supabase")


if __name__ == "__main__":
    latest_file = get_latest_processed_file()
    print(f"[LOAD] Reading {latest_file}")
    df = pd.read_csv(latest_file)
    load_to_supabase(df)
