# E-commerce Delivery & Logistics Performance Analysis

A data analytics project focused on understanding e-commerce delivery performance, logistics operations, order patterns, and payment behavior using the Brazilian E-Commerce Public Dataset by Olist.

## 1. Project Overview

This project analyzes historical e-commerce transactions to understand delivery performance and identify patterns in order fulfillment.

The project uses Python, Pandas, PostgreSQL, and SQL to ingest, validate, transform, and analyze the dataset.

### Project Objectives

- Analyze actual versus estimated delivery performance.
- Measure average delivery duration and delivery delays.
- Identify early, on-date, and late deliveries.
- Analyze order items, product values, freight charges, and payment behavior.
- Prepare reliable datasets for downstream analysis and visualization.

## 2. Dataset Information

**Dataset:** Brazilian E-Commerce Public Dataset by Olist

**Source:** https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce

**Format:** CSV

**Historical coverage:** 2016–2018

The dataset contains nine CSV files covering customers, orders, order items, payments, reviews, products, sellers, geolocation, and product category translations.

### Dataset files

| CSV file | Description |
|---|---|
| olist_customers_dataset.csv | Customer information |
| olist_geolocation_dataset.csv | ZIP prefix and geographic coordinates |
| olist_order_items_dataset.csv | Individual items within orders |
| olist_order_payments_dataset.csv | Payment records |
| olist_order_reviews_dataset.csv | Customer reviews |
| olist_orders_dataset.csv | Order and delivery timestamps |
| olist_products_dataset.csv | Product information |
| olist_sellers_dataset.csv | Seller information |
| product_category_name_translation.csv | Product category translations |

The original dataset files are stored locally in `data/raw/` and are not committed to Git.

### Data Documentation

The following documents provide detailed information about the dataset and its suitability for analysis:

| Document | Description |
|---|---|
| [Data Dictionary](docs/data_dictionary.md) | Column-level descriptions, meanings, data types, and source information for all nine tables. |
| [Excel Data Dictionary](docs/data_dictionary.xlsx) | Downloadable Excel version of the data dictionary, including sample values and missing-value percentages. |
| [Dataset Provenance](docs/dataset_provenance.md) | Dataset source, license, download information, record counts, and historical coverage. |
| [Field Availability](docs/field_availability.md) | Availability of important analytical fields and documented data limitations. |
| [Delivery KPI Methodology](docs/delivery_kpi_methodology.md) | Definitions and calculation methods for delivery performance metrics. |

## 3. Technology Stack

| Technology | Purpose |
|---|---|
| Python | Data ingestion and profiling |
| Pandas | CSV processing |
| PostgreSQL | Relational database |
| SQLAlchemy | Python database connectivity |
| Psycopg | PostgreSQL driver |
| SQL | Constraints, analytical views, and queries |
| Git and GitHub | Version control and collaboration |

## 4. Repository Structure

```text
project1-delivery-analysis/
│
├── dashboard/
│
├── data/
│   ├── raw/
│   ├── interim/
│   └── processed/
│
├── docs/
│   ├── column_profile.csv
│   ├── dataset_inspection_summary.csv
│   ├── data_dictionary.md
│   ├── table_grain_analysis.md
│   └── delivery_kpi_methodology.md
│
├── notebooks/
│
├── reports/
│   └── figures/
│
├── sql/
│   ├── schema.sql
│   └── views.sql
│
├── src/
│   ├── inspect_data.py
│   ├── inspect_grain.py
│   ├── validate_keys.py
│   ├── validate_remaining.py
│   ├── inspect_delivery_coverage.py
│   ├── analyze_delivery_performance.py
│   ├── test_db_connection.py
│   └── ingest.py
│
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

## 5. Environment Setup

### Prerequisites

Install or configure:

- Python 3.13 or a compatible Python version
- PostgreSQL
- Git
- pip
- Virtual environment support

The ingestion pipeline was tested using Fedora 44, Python 3.13.15, and PostgreSQL 18.6.

### Clone the repository

```bash
git clone https://github.com/kashiyn133-gif/Ecommerce.git

cd Ecommerce
```

### Create a Python virtual environment

```bash
python -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

## 6. Dataset Setup

Download the Brazilian E-Commerce Public Dataset by Olist from Kaggle:

https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce

Extract the nine CSV files into:

```text
data/raw/
```

Keep the original CSV files unchanged.

The ingestion pipeline expects the filenames listed in the dataset mapping in `src/ingest.py`.

## 7. PostgreSQL Configuration

Start the PostgreSQL service if it is not already running.

On Fedora:

```bash
sudo systemctl start postgresql
```

Create a dedicated database role and database using the PostgreSQL administrator.

```bash
sudo -u postgres psql
```

Inside PostgreSQL:

```sql
CREATE ROLE delivery_user WITH LOGIN PASSWORD 'YOUR_PASSWORD';

CREATE DATABASE delivery_db OWNER delivery_user;

\q
```

If the role already exists, do not recreate it. Configure its password or use the existing credentials as appropriate.

### Configure environment variables

Create a local `.env` file:

```bash
cp .env.example .env
```

Edit `.env`:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=delivery_db
DB_USER=delivery_user
DB_PASSWORD=YOUR_PASSWORD
```

Use your own PostgreSQL credentials.

**Security:** Never commit `.env` or expose database passwords. The repository includes `.env.example` as a configuration template.

## 8. Database Ingestion

Make sure the following conditions are satisfied:

- PostgreSQL is running.
- The target database exists.
- `.env` contains valid database credentials.
- All nine CSV files are available in `data/raw/`.
- The Python virtual environment is active.

Run:

```bash
python src/ingest.py
```

The ingestion script:

1. Connects to PostgreSQL.
2. Reads the nine CSV files.
3. Processes data in chunks of 10,000 rows.
4. Loads records into PostgreSQL.
5. Compares imported row counts with database row counts.
6. Reports success or raises an error if validation fails.

**Important:** The ingestion script uses `if_exists="replace"` for the first chunk of each table. This drops and recreates existing target tables. Run it only against a fresh database or a database you intentionally want to rebuild. Do not rerun it casually against a database containing constraints and dependent views.

## 9. Apply Database Constraints

After successful ingestion, execute:

```bash
psql -h localhost -U delivery_user -d delivery_db \
    -v ON_ERROR_STOP=1 -f sql/schema.sql
```

The schema script defines:

- 8 primary keys
- 6 foreign keys

It checks for the expected constraints before creating them, allowing safe reruns when the expected constraints already exist.

## 10. Create Analytical SQL Views

Execute:

```bash
psql -h localhost -U delivery_user -d delivery_db \
    -v ON_ERROR_STOP=1 -f sql/views.sql
```

The script creates four analytical views:

| View | Purpose |
|---|---|
| vw_order_delivery_performance | Delivery duration, delay, timing classification, and on-time status |
| vw_order_item_summary | Order-level item counts and product/freight totals |
| vw_order_payment_summary | Order-level payment records, methods, and payment totals |
| vw_order_analytics | Consolidated order-level analytical dataset |

Item and payment records are aggregated separately before joining to orders. This prevents row multiplication when an order contains multiple items and payment records.

## 11. Validation

Connect to PostgreSQL:

```bash
psql -h localhost -U delivery_user -d delivery_db
```

Check the main table counts:

```sql
SELECT
    (SELECT COUNT(*) FROM orders) AS total_orders,
    (SELECT COUNT(*) FROM order_items) AS total_order_items,
    (SELECT COUNT(*) FROM payments) AS total_payment_records;
```

Check the consolidated analytical view:

```sql
SELECT
    COUNT(*) AS total_rows,
    COUNT(DISTINCT order_id) AS unique_orders
FROM vw_order_analytics;
```

Expected:

| Metric | Expected |
|---|---:|
| Orders | 99,441 |
| Order items | 112,650 |
| Payment records | 103,886 |
| Analytical rows | 99,441 |
| Unique analytical orders | 99,441 |

### Constraint validation

```sql
SELECT
    contype,
    COUNT(*) AS constraint_count
FROM pg_constraint
WHERE connamespace = 'public'::regnamespace
  AND contype IN ('p', 'f')
GROUP BY contype
ORDER BY contype;
```

Expected:

- Primary keys: 8
- Foreign keys: 6

## 12. Initial Delivery Performance Results

The current delivery analysis produced the following results:

| KPI | Result |
|---|---:|
| Total delivered orders | 96,478 |
| Eligible delivered orders | 96,470 |
| Average actual delivery time | 12.56 days |
| Average estimated delivery time | 23.74 days |
| Average delivery delay | -11.88 days |
| Early delivery percentage | 91.89% |
| On-date delivery percentage | 1.34% |
| Late delivery percentage | 6.77% |
| On-time delivery percentage | 93.23% |

On-time delivery includes both early and on-date deliveries.

The on-time delivery rate is calculated using eligible delivered orders as the denominator.

Detailed definitions and limitations are available in `docs/delivery_kpi_methodology.md`.

## 13. Data Quality and Limitations

Important findings from initial data profiling:

- The geolocation table contains duplicate records and non-unique ZIP prefixes.
- Customer unique IDs can appear in multiple customer records.
- Review IDs alone are not unique.
- Some product attributes and review comments contain missing values.
- Two product categories do not have corresponding English translations.
- 775 orders have no matching order-item records.
- One delivered order has no matching payment record.
- Eight delivered orders are excluded from delivery classification because their actual delivery timestamps are missing.

Missing information is preserved and documented rather than fabricated.

### Reproducing the data-quality work (M2)

```bash
python src/verify_raw.py   # raw files match the audited SHA-256 fingerprints
python src/clean.py        # creates data/interim/orders_clean.csv + docs/cleaning_validation.md
```

- Rules DQ-01 to DQ-13: `docs/data_quality_audit.md`
- Validation evidence (row reconciliation, rule counts, IQR calculation): `docs/cleaning_validation.md`

## 14. Analytical Methodology

- Preserve original source data.
- Respect the grain of each source table.
- Aggregate one-to-many relationships before joining to order-level data.
- Use calendar dates for delivery classification.
- Use elapsed time for actual delivery duration.
- State the denominator for every percentage-based KPI.
- Distinguish missing data from actual zero values.
- Avoid making causal claims from descriptive analysis.

## 15. Team Collaboration

The project is developed collaboratively using Git and GitHub.

Contributors should:

1. Work on their assigned branches.
2. Commit changes regularly.
3. Avoid pushing directly to `main`.
4. Create pull requests for review.
5. Coordinate changes to shared documentation, SQL files, and project structure.

---

## 16. License and Attribution

Dataset: Brazilian E-Commerce Public Dataset by Olist.

Refer to the Kaggle dataset page and its associated CC BY-NC-SA 4.0 license terms before redistributing the dataset or derived materials.

Dataset source: https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce