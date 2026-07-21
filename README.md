# 🪙 Crypto Market Data Pipeline

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Airflow](https://img.shields.io/badge/Apache%20Airflow-017CEE?style=for-the-badge&logo=apacheairflow&logoColor=white)
![dbt](https://img.shields.io/badge/dbt-FF694B?style=for-the-badge&logo=dbt&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Supabase](https://img.shields.io/badge/Supabase-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white)

**A production-style, end-to-end ETL/ELT data pipeline** that automatically extracts live cryptocurrency market data, validates its quality, loads it into a cloud data warehouse, transforms it into analytics-ready tables, and orchestrates the entire workflow on a daily schedule — fully automated, running on 100% free-tier infrastructure.

> Built to demonstrate real-world data engineering skills: API integration, data validation, cloud warehousing, SQL-based transformation, containerization, and workflow orchestration.

---

## Pipeline Preview

**Airflow Orchestration** — all 5 pipeline stages (extract → transform → validate → load → dbt_run) running successfully

![Airflow Pipeline Success](screenshots/airflow-pipeline-success.png)

**Cluster Health** — Airflow scheduler and metadata database status

![Cluster Health](screenshots/cluster-health.png)

**Supabase Data Warehouse** — validated data landed in the cloud PostgreSQL warehouse

![Supabase Data Table](screenshots/supabase-data-table.png)
![Supabase Data Columns](screenshots/supabase-data-columns.png)

---

## 📌 What This Project Does

Every day, without any manual intervention, this pipeline:

1. **Pulls** live market data for the top 100 cryptocurrencies from a public API
2. **Cleans** and reshapes the raw data into a consistent, typed format
3. **Validates** the data against 9 automated quality checks — and halts the pipeline if anything looks wrong
4. **Loads** the validated data into a cloud PostgreSQL data warehouse
5. **Transforms** the raw warehouse data into clean, analytics-ready tables using SQL
6. **Orchestrates** all of the above automatically, on schedule, with full failure handling and retry logic

This mirrors the exact pattern used by real data teams to move data from an external source into a warehouse where it can power dashboards, reports, or further analysis.

---

## 🏗️ Architecture

```
                    ┌─────────────────┐
                    │   CoinGecko API  │   (free public data source)
                    └────────┬─────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  1. EXTRACT      │   Python + Requests
                    │  extract.py      │   → saves raw JSON snapshot
                    └────────┬─────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  2. TRANSFORM    │   Python + Pandas
                    │  transform.py    │   → cleans, types, reshapes
                    └────────┬─────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  3. VALIDATE     │   9 automated data quality checks
                    │  validate.py     │   → halts pipeline on failure
                    └────────┬─────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  4. LOAD         │   SQLAlchemy + psycopg2
                    │  load.py         │   → writes to Postgres warehouse
                    └────────┬─────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │   Supabase       │   Cloud-hosted PostgreSQL
                    │ (Data Warehouse) │   (raw_crypto_prices table)
                    └────────┬─────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  5. TRANSFORM    │   dbt (staging + mart models)
                    │  (in-warehouse)  │   → SQL-based modeling
                    └────────┬─────────┘
                             │
                             ▼
              ┌──────────────┴───────────────┐
              ▼                               ▼
   ┌────────────────────┐         ┌────────────────────┐
   │ mart_latest_prices  │         │  mart_top_movers    │
   │ (current snapshot)  │         │ (gainers/losers)    │
   └─────────────────────┘         └─────────────────────┘

   All 5 steps orchestrated daily by Apache Airflow, running in Docker.
```

---

## 🛠️ Tech Stack & Why Each Tool Was Used

| Tool | Role in This Project | Why It Was Chosen |
|---|---|---|
| **Python** | Core scripting language for extract, transform, validate, and load logic | Industry-standard for data engineering; readable, huge ecosystem of libraries |
| **Pandas** | Data cleaning, type conversion, reshaping | The standard tool for tabular data manipulation in Python |
| **Requests** | HTTP calls to the CoinGecko API | Simple, reliable library for API integration |
| **PostgreSQL (via Supabase)** | Cloud data warehouse | Real relational database experience; Supabase provides a free-tier hosted Postgres instance with zero infrastructure setup |
| **SQLAlchemy + psycopg2** | Python-to-Postgres database connectivity | Standard, production-grade approach for loading data into a SQL database from Python |
| **dbt (data build tool)** | SQL-based transformation layer inside the warehouse | Industry-standard for building maintainable, testable, version-controlled SQL transformations — separates "raw" data from "analytics-ready" data using a staging → mart pattern |
| **Apache Airflow** | Workflow orchestration and scheduling | The most widely used orchestration tool in the data engineering industry; manages task dependencies, retries, and failure handling |
| **Docker & Docker Compose** | Containerized local Airflow deployment | Lets Airflow run identically on any machine without polluting the host system; mirrors how Airflow is deployed in real production environments |
| **Git & GitHub** | Version control | Standard practice for any engineering project |

---

## ✅ Key Engineering Practices Demonstrated

- **Separation of concerns** — each script (extract/transform/validate/load) does exactly one job, making the pipeline easy to debug and extend
- **Fail-safe data quality gating** — the pipeline automatically halts before loading data if any of 9 validation checks fail (duplicate records, negative prices, missing fields, implausible values), preventing bad data from ever reaching the warehouse
- **Raw vs. modeled data separation** — raw API responses are preserved untouched, while dbt builds clean, business-ready models on top, following the staging → mart pattern used in real data warehouses
- **Idempotent, append-only loading** — every pipeline run appends a timestamped snapshot rather than overwriting, preserving full historical data for trend analysis
- **Full orchestration with dependency management** — Airflow ensures each step only runs after the previous one succeeds, with automatic retries on transient failures
- **Environment-based secrets management** — database credentials are kept out of version control via `.env` files and `.gitignore`

---

## 📂 Project Structure

```
crypto-data-pipeline/
├── scripts/
│   ├── extract.py          # Pulls live data from CoinGecko API
│   ├── transform.py        # Cleans and reshapes raw data
│   ├── validate.py         # Runs 9 automated data quality checks
│   └── load.py             # Loads validated data into Postgres
├── dbt_crypto/
│   ├── models/
│   │   ├── staging/
│   │   │   ├── sources.yml
│   │   │   └── stg_crypto_prices.sql
│   │   └── marts/
│   │       ├── mart_latest_prices.sql
│   │       └── mart_top_movers.sql
│   └── dbt_project.yml
├── dags/
│   └── crypto_pipeline_dag.py   # Airflow DAG orchestrating all 5 steps
├── docker-compose.yaml          # Local Airflow deployment
├── requirements.txt
└── README.md
```

---

## 🔄 Pipeline Workflow (Step-by-Step)

| Step | What Happens | Output |
|---|---|---|
| **1. Extract** | Calls CoinGecko's free public API for the top 100 coins by market cap | Timestamped raw JSON file |
| **2. Transform** | Selects relevant fields, renames columns, converts types, drops incomplete records | Clean, typed CSV |
| **3. Validate** | Checks row count, duplicates, negative values, nulls, and plausible price ranges | Pass/fail quality report — pipeline halts on failure |
| **4. Load** | Appends validated records into the `raw_crypto_prices` table in Postgres | Growing historical table in the warehouse |
| **5. dbt Run** | Builds `stg_crypto_prices` (cleaning layer), then `mart_latest_prices` (current snapshot) and `mart_top_movers` (gainers/losers by market cap tier) | Analytics-ready tables |
| **6. Orchestration** | Airflow runs all of the above daily, in the correct order, with retry logic | Fully automated daily pipeline |

---

## 🚀 Running This Project Locally

```bash
# 1. Clone and set up environment
git clone <this-repo-url>
cd crypto-data-pipeline
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Configure your database connection
# Create a .env file with your PostgreSQL connection string:
# SUPABASE_DB_URL=postgresql://user:password@host:5432/dbname

# 3. Run the pipeline manually, step by step
python3 scripts/extract.py
python3 scripts/transform.py
python3 scripts/validate.py
python3 scripts/load.py

# 4. Run dbt transformations
cd dbt_crypto
dbt run --profiles-dir .

# 5. Orchestrate with Airflow (Docker required)
cd ..
docker compose up airflow-init
docker compose up -d
# Visit http://localhost:8080 (login: admin/admin)
# Trigger the "crypto_pipeline" DAG
```

---

## 📈 Potential Extensions

- Add Slack/email alerting on pipeline failure
- Build a Streamlit or Power BI dashboard on top of `mart_top_movers`
- Add a second data source to demonstrate multi-source ingestion
- Add historical trend analysis and basic forecasting models

---

## 👩‍💻 About This Project

Built as a hands-on portfolio project to demonstrate practical data engineering skills — designing ETL pipelines, working with cloud data warehouses, writing maintainable SQL transformations with dbt, and orchestrating production-style workflows with Airflow and Docker.
