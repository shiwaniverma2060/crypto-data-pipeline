"""
PHASE 3: DATA QUALITY CHECKS
------------------------------
Before loading data into the warehouse, we validate it. This is the
single most "senior data engineer" thing you can put on a resume,
because it shows you don't blindly trust data - you check it.

These are the same categories of checks a tool like Great
Expectations runs under the hood; we're writing them by hand first
so you understand exactly what's being tested (highly recommended
before you ever use a tool that does it "automatically" for you).

Checks performed:
  1. Row count sanity check (did we get a reasonable number of rows?)
  2. No duplicate coin_ids
  3. No negative prices or market caps (impossible values = bad data)
  4. No nulls in required columns
  5. Prices within a plausible range (catches API glitches, e.g. a
     coin accidentally reported as $0 or $999999999)
"""

import pandas as pd
import glob
import os

PROCESSED_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")

REQUIRED_COLUMNS = ["coin_id", "symbol", "price_usd", "market_cap_usd"]


class DataQualityError(Exception):
    pass


def get_latest_processed_file():
    files = glob.glob(os.path.join(PROCESSED_DATA_DIR, "crypto_processed_*.csv"))
    if not files:
        raise FileNotFoundError("No processed files found. Run transform.py first.")
    return max(files, key=os.path.getctime)


def run_checks(df):
    results = []

    # 1. Row count sanity check
    passed = len(df) >= 50
    results.append(("row_count >= 50", passed, f"got {len(df)} rows"))

    # 2. No duplicate coin_ids
    dupes = df["coin_id"].duplicated().sum()
    results.append(("no_duplicate_coin_ids", dupes == 0, f"{dupes} duplicates found"))

    # 3. No negative prices or market caps
    negative_prices = (df["price_usd"] < 0).sum()
    negative_caps = (df["market_cap_usd"] < 0).sum()
    results.append(("no_negative_prices", negative_prices == 0, f"{negative_prices} negative prices"))
    results.append(("no_negative_market_caps", negative_caps == 0, f"{negative_caps} negative market caps"))

    # 4. No nulls in required columns
    for col in REQUIRED_COLUMNS:
        nulls = df[col].isna().sum()
        results.append((f"no_nulls_in_{col}", nulls == 0, f"{nulls} nulls"))

    # 5. Plausible price range (catches API glitches / bad scrapes)
    implausible = ((df["price_usd"] <= 0) | (df["price_usd"] > 10_000_000)).sum()
    results.append(("prices_in_plausible_range", implausible == 0, f"{implausible} implausible prices"))

    return results


def print_report(results):
    print("\n[VALIDATE] Data Quality Report")
    print("-" * 50)
    all_passed = True
    for check_name, passed, detail in results:
        status = "PASS" if passed else "FAIL"
        if not passed:
            all_passed = False
        print(f"  [{status}] {check_name} ({detail})")
    print("-" * 50)
    return all_passed


if __name__ == "__main__":
    latest_file = get_latest_processed_file()
    print(f"[VALIDATE] Checking {latest_file}")
    df = pd.read_csv(latest_file)
    results = run_checks(df)
    passed = print_report(results)

    if not passed:
        raise DataQualityError("One or more data quality checks failed. Halting pipeline before load.")
    print("[VALIDATE] All checks passed. Safe to load.\n")
