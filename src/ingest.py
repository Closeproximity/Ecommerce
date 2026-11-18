
import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

# --------------------------------------------------
# 1. Project configuration
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"

load_dotenv(PROJECT_ROOT / ".env")

database_url = URL.create(
    drivername="postgresql+psycopg",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT", "5432")),
    database=os.getenv("DB_NAME"),
)

engine = create_engine(database_url)

# --------------------------------------------------
# 2. CSV-to-PostgreSQL table mapping
# --------------------------------------------------

DATASETS = {
    "olist_customers_dataset.csv": "customers",
    "olist_geolocation_dataset.csv": "geolocation",
    "olist_order_items_dataset.csv": "order_items",
    "olist_order_payments_dataset.csv": "payments",
    "olist_order_reviews_dataset.csv": "reviews",
    "olist_orders_dataset.csv": "orders",
    "olist_products_dataset.csv": "products",
    "olist_sellers_dataset.csv": "sellers",
    "product_category_name_translation.csv": "category_translation",
}

CHUNK_SIZE = 10_000


# --------------------------------------------------
# 3. Ingest one CSV file
# --------------------------------------------------

def ingest_csv(filename, table_name):
    file_path = RAW_DATA_DIR / filename

    if not file_path.exists():
        raise FileNotFoundError(f"Dataset not found: {file_path}")

    expected_rows = sum(
        len(chunk)
        for chunk in pd.read_csv(file_path, chunksize=CHUNK_SIZE)
    )

    imported_rows = 0
    first_chunk = True

    print(f"\nImporting {filename} into {table_name}...")

    for chunk in pd.read_csv(file_path, chunksize=CHUNK_SIZE):

        chunk.to_sql(
            name=table_name,
            con=engine,
            if_exists="replace" if first_chunk else "append",
            index=False,
            method="multi",
            chunksize=1000,
        )

        imported_rows += len(chunk)
        first_chunk = False

        print(f"  Imported: {imported_rows:,} / {expected_rows:,}")

    with engine.connect() as connection:
        database_rows = connection.execute(
            text(f'SELECT COUNT(*) FROM "{table_name}"')
        ).scalar_one()

    if imported_rows != expected_rows or database_rows != expected_rows:
        raise RuntimeError(
            f"Row count mismatch for {table_name}: "
            f"expected={expected_rows}, "
            f"imported={imported_rows}, "
            f"database={database_rows}"
        )

    print(f"SUCCESS: {table_name} ({database_rows:,} rows)")


# --------------------------------------------------
# 4. Main ingestion process
# --------------------------------------------------

def main():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        print("PostgreSQL connection successful.")
        print("Starting dataset ingestion...")

        for filename, table_name in DATASETS.items():
            ingest_csv(filename, table_name)

        print("\nAll datasets imported and row counts verified.")

    except Exception as error:
        print(f"\nINGESTION FAILED: {error}")
        raise

    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
