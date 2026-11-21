"""
clean.py - M2 Data Quality Analyst
==================================
Reads the raw Olist files, applies every rule in docs/data_quality_audit.md
(DQ-01 to DQ-13), and writes ONE ROW PER ORDER to data/interim/orders_clean.csv.

Policy: flag, don't delete.
- Raw files in data/raw/ are only read, never changed (checked with verify_raw.py).
- No order is removed. Every rule adds a column, so KPI owners (M3, M6)
  decide what to exclude for each KPI.

The script first runs verify_raw.py and STOPS if any raw file differs from
the audited version, so cleaning always uses the audited dataset.

The cleaned CSV is first written to a temporary file, re-read and reconciled
with the raw orders. Only if every check passes is it published as
data/interim/orders_clean.csv, followed by the reports below. If a check fails,
the previously published files are left unchanged.

Every successful run also writes:
- docs/cleaning_validation.md: evidence that no order was lost or duplicated,
  the count for every rule, and the exact IQR calculation
- docs/orders_clean_schema.md: every column of the cleaned dataset, explained

How to run (from the project root, with .venv active):
    python src/clean.py
"""

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))  # make src/ importable from any working folder
from verify_raw import all_ok, verify_files               # noqa: E402  (raw-file fingerprint check)

# ------------------------------------------------------------------
# 1. Paths and settings
# ------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent   # project root (one level above src/)
RAW = ROOT / "data" / "raw"                      # original files: read only
INTERIM = ROOT / "data" / "interim"              # cleaned output goes here
OUTPUT_FILE = INTERIM / "orders_clean.csv"
REPORT_FILE = ROOT / "docs" / "cleaning_validation.md"
SCHEMA_FILE = ROOT / "docs" / "orders_clean_schema.md"

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"                # one format for every date column
DATE_COLS = [
    "order_purchase_timestamp",       # (1) customer buys
    "order_approved_at",              # (2) payment approved
    "order_delivered_carrier_date",   # (3) handed to courier
    "order_delivered_customer_date",  # (4) customer receives
    "order_estimated_delivery_date",  # promised date
]

# Rule ID -> flag column. Order of this list = order in reports.
RULES = [
    ("DQ-01", "flag_delivered_no_delivery_date", "Delivered but no customer delivery date"),
    ("DQ-02", "flag_canceled_with_delivery_date", "Canceled but has a customer delivery date"),
    ("DQ-03", "flag_delivered_no_carrier_date", "Delivered but no carrier date"),
    ("DQ-04", "flag_delivered_no_approval_date", "Delivered but no approval date"),
    ("DQ-05", "flag_carrier_before_purchase", "Carrier date before purchase"),
    ("DQ-06", "flag_carrier_before_approval", "Carrier date before approval"),
    ("DQ-07", "flag_delivered_before_carrier", "Customer delivery before carrier date"),
    ("DQ-08", "flag_long_delivery", "Delivery time above IQR upper limit (kept)"),
    ("DQ-09", "flag_no_items", "Order has no items"),
    ("DQ-10", "flag_multiple_reviews", "Order has more than one review"),
    ("DQ-11", "flag_item_unknown_category", "Order contains a product with no category"),
    ("DQ-12", "flag_item_untranslated_category", "Order contains a product whose category has no English name"),
    ("DQ-13", "flag_item_zero_freight", "Order contains an item with zero freight (kept)"),
]
# Rules that describe a data error. DQ-08, DQ-10, DQ-11, DQ-12, DQ-13 describe real situations, not errors.
QUALITY_ISSUE_RULES = ["DQ-01", "DQ-02", "DQ-03", "DQ-04", "DQ-05", "DQ-06", "DQ-07", "DQ-09"]

# Every column of orders_clean.csv: (type, meaning, rule). The script stops if a column is undocumented.
SCHEMA = {
    "order_id": ("text", "Unique order identifier (one row per order)", ""),
    "customer_id": ("text", "Customer key for this order (links to customers)", ""),
    "order_status": ("text", "Order status, lowercase (delivered, shipped, canceled, ...)", ""),
    "order_purchase_timestamp": ("datetime", "(1) Customer placed the order", ""),
    "order_approved_at": ("datetime", "(2) Payment approved; empty if never approved", ""),
    "order_delivered_carrier_date": ("datetime", "(3) Handed to the courier; empty if never dispatched", ""),
    "order_delivered_customer_date": ("datetime", "(4) Delivered to the customer; empty if never delivered", ""),
    "order_estimated_delivery_date": ("datetime", "Delivery date promised to the customer", ""),
    "flag_delivered_no_delivery_date": ("bool", "Delivered but no customer delivery date", "DQ-01"),
    "flag_canceled_with_delivery_date": ("bool", "Canceled but has a customer delivery date", "DQ-02"),
    "flag_delivered_no_carrier_date": ("bool", "Delivered but no carrier date", "DQ-03"),
    "flag_delivered_no_approval_date": ("bool", "Delivered but no approval date", "DQ-04"),
    "flag_carrier_before_purchase": ("bool", "Carrier date earlier than purchase date", "DQ-05"),
    "flag_carrier_before_approval": ("bool", "Carrier date earlier than approval date", "DQ-06"),
    "flag_delivered_before_carrier": ("bool", "Customer delivery earlier than carrier date", "DQ-07"),
    "delivery_days": ("float", "Days from purchase to customer delivery (helper for EDA; KPI definition owned by M3/M6)", ""),
    "processing_days": ("float", "Days from purchase to carrier handover (helper for EDA)", ""),
    "flag_long_delivery": ("bool", "Delivered order with delivery_days above the IQR upper limit (kept)", "DQ-08"),
    "item_count": ("int", "Number of items in the order (0 = no items)", "DQ-09"),
    "items_unknown_category": ("int", "Items whose product has no category", "DQ-11"),
    "items_untranslated_category": ("int", "Items whose category has no English name", "DQ-12"),
    "items_zero_freight": ("int", "Items with freight_value = 0", "DQ-13"),
    "flag_no_items": ("bool", "Order has no items", "DQ-09"),
    "flag_item_unknown_category": ("bool", "At least one item has no product category", "DQ-11"),
    "flag_item_untranslated_category": ("bool", "At least one item's category has no English name", "DQ-12"),
    "flag_item_zero_freight": ("bool", "At least one item has zero freight (kept)", "DQ-13"),
    "review_count": ("int", "Number of reviews for the order (0 = no review)", "DQ-10"),
    "review_score_latest": ("float", "Score of the latest review (PROPOSED rule, awaiting M3); empty if no review", "DQ-10"),
    "review_score_mean": ("float", "Average review score (alternative rule); empty if no review", "DQ-10"),
    "flag_multiple_reviews": ("bool", "Order has more than one review", "DQ-10"),
    "customer_city": ("text", "Customer city, lowercase", ""),
    "customer_state": ("text", "Customer state, 2-letter uppercase code", ""),
    "flag_any_quality_issue": ("bool", "True if any data-error rule is True (DQ-01 to DQ-07, DQ-09)", "summary"),
}


# ------------------------------------------------------------------
# 2. Load raw data
# ------------------------------------------------------------------
def load_raw():
    """Read the 7 raw tables this script needs."""
    return {
        "orders": pd.read_csv(RAW / "olist_orders_dataset.csv"),
        "items": pd.read_csv(RAW / "olist_order_items_dataset.csv"),
        "reviews": pd.read_csv(RAW / "olist_order_reviews_dataset.csv"),
        "customers": pd.read_csv(RAW / "olist_customers_dataset.csv"),
        "products": pd.read_csv(RAW / "olist_products_dataset.csv"),
        "translation": pd.read_csv(RAW / "product_category_name_translation.csv"),
    }


# ------------------------------------------------------------------
# 3. Standardise types and text
# ------------------------------------------------------------------
def standardise(orders, customers):
    """Parse dates with one format and tidy text columns."""
    orders = orders.copy()        # work on a copy, never on the loaded raw table
    customers = customers.copy()

    for col in DATE_COLS:
        before_missing = orders[col].isna().sum()
        orders[col] = pd.to_datetime(orders[col], format=DATE_FORMAT, errors="coerce")
        failed = orders[col].isna().sum() - before_missing
        if failed > 0:            # audit found 0 failures; warn loudly if the data ever changes
            print(f"WARNING: {failed} values in {col} could not be parsed")

    orders["order_status"] = orders["order_status"].str.strip().str.lower()
    customers["customer_state"] = customers["customer_state"].str.strip().str.upper()
    customers["customer_city"] = customers["customer_city"].str.strip().str.lower()
    return orders, customers


# ------------------------------------------------------------------
# 4. Order-level flags from the orders table (DQ-01 to DQ-08)
# ------------------------------------------------------------------
def add_order_flags(df):
    delivered = df["order_status"] == "delivered"
    canceled = df["order_status"] == "canceled"

    purchase = df["order_purchase_timestamp"]
    approved = df["order_approved_at"]
    carrier = df["order_delivered_carrier_date"]
    customer = df["order_delivered_customer_date"]

    # Status vs dates (comparisons with a missing date give False)
    df["flag_delivered_no_delivery_date"] = delivered & customer.isna()   # DQ-01
    df["flag_canceled_with_delivery_date"] = canceled & customer.notna()  # DQ-02
    df["flag_delivered_no_carrier_date"] = delivered & carrier.isna()     # DQ-03
    df["flag_delivered_no_approval_date"] = delivered & approved.isna()   # DQ-04

    # Impossible order of events
    df["flag_carrier_before_purchase"] = carrier < purchase               # DQ-05
    df["flag_carrier_before_approval"] = carrier < approved               # DQ-06
    df["flag_delivered_before_carrier"] = customer < carrier              # DQ-07

    # Helper durations in days (86,400 seconds = 1 day). Final KPI definitions belong to M3/M6.
    df["delivery_days"] = (customer - purchase).dt.total_seconds() / 86400
    df["processing_days"] = (carrier - purchase).dt.total_seconds() / 86400

    # DQ-08: IQR rule on delivered orders that have a delivery date
    population = df.loc[delivered & customer.notna(), "delivery_days"]
    q1 = population.quantile(0.25)            # pandas default: linear interpolation
    q3 = population.quantile(0.75)
    iqr = q3 - q1
    upper = q3 + 1.5 * iqr
    df["flag_long_delivery"] = delivered & customer.notna() & (df["delivery_days"] > upper)

    iqr_details = {"n": len(population), "q1": q1, "q3": q3, "iqr": iqr,
                   "step": 1.5 * iqr, "upper": upper,
                   "above": int(df["flag_long_delivery"].sum())}
    return df, iqr_details


# ------------------------------------------------------------------
# 5. Item and product rules (DQ-09, DQ-11, DQ-12, DQ-13)
# ------------------------------------------------------------------
def add_item_flags(df, items, products, translation):
    prod = products[["product_id", "product_category_name"]].copy()
    prod["category_missing"] = prod["product_category_name"].isna()                       # DQ-11 (product level)
    known = set(translation["product_category_name"])
    prod["category_untranslated"] = (prod["product_category_name"].notna()
                                     & ~prod["product_category_name"].isin(known))          # DQ-12 (product level)

    # Attach product info to every item; validate="m:1" guarantees one product row per product_id
    it = items.merge(prod, on="product_id", how="left", validate="m:1")
    assert len(it) == len(items), "Item rows changed while joining products"
    it["zero_freight"] = it["freight_value"] == 0                                           # DQ-13 (item level)

    # Summarise per order, then map back (map adds columns, never rows)
    per_order = it.groupby("order_id").agg(
        item_count=("product_id", "size"),
        items_unknown_category=("category_missing", "sum"),
        items_untranslated_category=("category_untranslated", "sum"),
        items_zero_freight=("zero_freight", "sum"),
    )
    for col in per_order.columns:
        df[col] = df["order_id"].map(per_order[col]).fillna(0).astype(int)

    df["flag_no_items"] = df["item_count"] == 0                                 # DQ-09
    df["flag_item_unknown_category"] = df["items_unknown_category"] > 0         # DQ-11
    df["flag_item_untranslated_category"] = df["items_untranslated_category"] > 0  # DQ-12
    df["flag_item_zero_freight"] = df["items_zero_freight"] > 0                 # DQ-13

    source_counts = {
        "products_no_category": int(prod["category_missing"].sum()),
        "products_untranslated": int(prod["category_untranslated"].sum()),
        "untranslated_names": sorted(prod.loc[prod["category_untranslated"], "product_category_name"].unique()),
        "items_zero_freight": int(it["zero_freight"].sum()),
        "total_products": len(prod),
        "total_items": len(it),
    }
    return df, source_counts


# ------------------------------------------------------------------
# 6. Reviews (DQ-10): one rating per order
# ------------------------------------------------------------------
def add_review_columns(df, reviews):
    """Add review_count, review_score_latest and review_score_mean.

    PROPOSED rule (awaiting M3 confirmation): use the LATEST review per order.
    "Latest" is decided by review_sort_time:
      1. review_answer_timestamp, or
      2. review_creation_date if the answer timestamp is missing (fallback).
    A review with neither date is treated as the OLDEST, so it is only chosen
    when the order has no dated review. Ties are broken by review_creation_date,
    then review_id, so the result is identical on every run.
    review_score_mean is kept so M3 can switch rules without re-running anything.
    """
    rv = reviews.copy()
    for col in ["review_creation_date", "review_answer_timestamp"]:
        rv[col] = pd.to_datetime(rv[col], format=DATE_FORMAT, errors="coerce")
    rv["review_sort_time"] = rv["review_answer_timestamp"].fillna(rv["review_creation_date"])  # fallback rule
    # na_position="first": missing dates sort as oldest, so keep="last" never prefers them over a dated review
    rv = rv.sort_values(["order_id", "review_sort_time", "review_creation_date", "review_id"],
                        na_position="first")

    latest = rv.drop_duplicates("order_id", keep="last").set_index("order_id")["review_score"]
    counts = rv.groupby("order_id").size()
    means = rv.groupby("order_id")["review_score"].mean()
    spread = rv.groupby("order_id")["review_score"].agg(lambda s: s.max() - s.min())

    df["review_count"] = df["order_id"].map(counts).fillna(0).astype(int)
    df["review_score_latest"] = df["order_id"].map(latest)       # empty when the order has no review
    df["review_score_mean"] = df["order_id"].map(means).round(2)
    df["flag_multiple_reviews"] = df["review_count"] > 1          # DQ-10

    review_stats = {
        "count_distribution": df["review_count"].clip(upper=3).value_counts().sort_index().to_dict(),
        "multi_disagree": int((spread > 0).sum()),
        "answer_missing": int(rv["review_answer_timestamp"].isna().sum()),
        "both_missing": int(rv["review_sort_time"].isna().sum()),
    }
    return df, review_stats


# ------------------------------------------------------------------
# 7. Build the order-level dataset
# ------------------------------------------------------------------
def build_clean(tables):
    orders, customers = standardise(tables["orders"], tables["customers"])
    df, iqr_details = add_order_flags(orders)
    df, source_counts = add_item_flags(df, tables["items"], tables["products"], tables["translation"])
    df, review_stats = add_review_columns(df, tables["reviews"])

    # Customer location; validate="m:1" stops the script if a join would duplicate orders
    df = df.merge(customers[["customer_id", "customer_city", "customer_state"]],
                  on="customer_id", how="left", validate="m:1")

    flag_of = {rule_id: col for rule_id, col, _ in RULES}
    df["flag_any_quality_issue"] = df[[flag_of[r] for r in QUALITY_ISSUE_RULES]].any(axis=1)
    return df, iqr_details, source_counts, review_stats


# ------------------------------------------------------------------
# 8. Validation evidence
# ------------------------------------------------------------------
def reconcile(raw_orders, saved):
    """Compare raw order IDs with the IDs in the file actually written to disk."""
    raw_ids, out_ids = set(raw_orders["order_id"]), set(saved["order_id"])
    checks = [
        ("Raw order rows", len(raw_orders), None),
        ("Raw unique order_id", len(raw_ids), None),
        ("Output rows (re-read from disk)", len(saved), len(saved) == len(raw_orders)),
        ("Output unique order_id", saved["order_id"].nunique(), saved["order_id"].is_unique),
        ("Order IDs lost (in raw, not in output)", len(raw_ids - out_ids), len(raw_ids - out_ids) == 0),
        ("Order IDs added (in output, not in raw)", len(out_ids - raw_ids), len(out_ids - raw_ids) == 0),
        ("Duplicate order_id in output", int(saved["order_id"].duplicated().sum()),
         not saved["order_id"].duplicated().any()),
    ]
    return checks


def write_report(raw_results, checks, df, iqr, src, rev):
    """Write docs/cleaning_validation.md. No dates or machine paths, so the file only changes when results change."""
    lines = [
        "# Cleaning Validation Report",
        "",
        "*Generated automatically by `python src/clean.py`. Do not edit by hand; re-run the script instead.*",
        "",
        "## 1. Raw data integrity (`python src/verify_raw.py`)",
        "",
        "Cleaning only runs when all 9 expected files are listed once in the manifest and match it.",
        "",
        "| File | Status |", "|---|---|",
        *[f"| `{f}` | {s} |" for f, s in raw_results],
        "",
        "## 2. Row reconciliation (no order lost or duplicated)",
        "",
        "| Check | Value | Result |", "|---|---:|---|",
        *[f"| {name} | {value:,} | {'' if ok is None else ('PASS' if ok else 'FAIL')} |" for name, value, ok in checks],
        "",
        "Joins use `validate=\"m:1\"` (customers, products) and per-order counts use `.map()`, "
        "so no step can multiply order rows. The script stops with an error if any check fails.",
        "",
        "## 3. Rule counts (order level)",
        "",
        "| Rule | Flag column | Orders | % of orders | Counts as quality issue |", "|---|---|---:|---:|---|",
        *[f"| {rid} | `{col}` | {int(df[col].sum()):,} | {df[col].mean() * 100:.2f}% | "
          f"{'Yes' if rid in QUALITY_ISSUE_RULES else 'No'} |" for rid, col, _ in RULES],
        f"| **Any** | `flag_any_quality_issue` | **{int(df['flag_any_quality_issue'].sum()):,}** | "
        f"**{df['flag_any_quality_issue'].mean() * 100:.2f}%** | DQ-01 to DQ-07, DQ-09 |",
        "",
        "Source-level counts behind the item/product rules:",
        "",
        f"- DQ-11: {src['products_no_category']:,} of {src['total_products']:,} products have no category",
        f"- DQ-12: {src['products_untranslated']:,} products in categories without an English name: "
        + ", ".join(f"`{c}`" for c in src["untranslated_names"]),
        f"- DQ-13: {src['items_zero_freight']:,} of {src['total_items']:,} items have freight = 0",
        "",
        "## 4. DQ-08 long-delivery threshold (exact calculation)",
        "",
        "- Population: orders with status `delivered` **and** a customer delivery date "
        f"(n = {iqr['n']:,})",
        "- `delivery_days` = (order_delivered_customer_date − order_purchase_timestamp) in seconds ÷ 86,400",
        "- Quartiles: `pandas.Series.quantile` with its default linear interpolation",
        "",
        "| Step | Value (days) |", "|---|---:|",
        f"| Q1 (25th percentile) | {iqr['q1']:.4f} |",
        f"| Q3 (75th percentile) | {iqr['q3']:.4f} |",
        f"| IQR = Q3 − Q1 | {iqr['iqr']:.4f} |",
        f"| 1.5 × IQR | {iqr['step']:.4f} |",
        f"| **Upper limit = Q3 + 1.5 × IQR** | **{iqr['upper']:.4f}** |",
        f"| Orders above the limit | {iqr['above']:,} |",
        "",
        "## 5. Reviews per order (DQ-10)",
        "",
        "| Reviews per order | Orders |", "|---|---:|",
        *[f"| {'3 or more' if k == 3 else k} | {v:,} |" for k, v in rev["count_distribution"].items()],
        "",
        f"Orders with several reviews whose scores disagree: {rev['multi_disagree']:,}",
        "",
        "Latest-review ordering (proposed rule, awaiting M3): `review_answer_timestamp`, falling back to "
        "`review_creation_date` when it is missing; reviews with neither date sort as oldest.",
        "",
        f"- Reviews with missing `review_answer_timestamp` (fallback used): {rev['answer_missing']:,}",
        f"- Reviews with neither date (treated as oldest): {rev['both_missing']:,}",
        "",
        "Columns provided: `review_count`, `review_score_latest` (proposed rule), `review_score_mean` (alternative). "
        "See `docs/data_quality_audit.md`, section 6.",
        "",
    ]
    REPORT_FILE.write_text("\n".join(lines), encoding="utf-8")


def write_schema(df):
    """Write docs/orders_clean_schema.md from SCHEMA, with true/false counts for every flag."""
    undocumented = [c for c in df.columns if c not in SCHEMA]
    missing = [c for c in SCHEMA if c not in df.columns]
    assert not undocumented and not missing, f"Schema out of date: new={undocumented}, gone={missing}"

    lines = [
        "# `orders_clean.csv` Schema",
        "",
        "*Generated automatically by `python src/clean.py`. Do not edit by hand.*",
        "",
        f"- **File:** `data/interim/orders_clean.csv` (not committed; recreate with `python src/clean.py`)",
        f"- **Grain:** one row per order ({len(df):,} rows, {len(df.columns)} columns)",
        "- **Key:** `order_id` (unique)",
        "- **Policy:** no rows removed; filter with the `flag_*` columns and state the exclusion in each KPI",
        "- **Rules:** see `docs/data_quality_audit.md`",
        "",
        "| # | Column | Type | Meaning | Rule | Orders where True |",
        "|---:|---|---|---|---|---:|",
    ]
    for i, col in enumerate(df.columns, 1):
        typ, meaning, rule = SCHEMA[col]
        true_count = f"{int(df[col].sum()):,}" if typ == "bool" else ""
        lines.append(f"| {i} | `{col}` | {typ} | {meaning} | {rule} | {true_count} |")
    lines += [
        "",
        "## Suggested filters",
        "",
        "| Use | Keep orders where |",
        "|---|---|",
        "| Delivery time, on-time, delay | `order_status == 'delivered'` and not `flag_delivered_no_delivery_date` "
        "(optionally exclude `flag_delivered_before_carrier`) |",
        "| Processing time | `order_delivered_carrier_date` present, not `flag_carrier_before_purchase`; "
        "decide on `flag_carrier_before_approval` |",
        "| Ratings | `review_count > 0`; use `review_score_latest` or `review_score_mean` once M3 confirms |",
        "| Price / freight | `item_count > 0` |",
        "| Category analysis | label orders with `flag_item_unknown_category` as `unknown`, never drop them |",
        "",
    ]
    SCHEMA_FILE.write_text("\n".join(lines), encoding="utf-8")


# ------------------------------------------------------------------
# 9. Run
# ------------------------------------------------------------------
def main():
    # Stop immediately if the raw data is not the audited version
    raw_results = verify_files()
    if not all_ok(raw_results):
        for file, status in raw_results:
            if status != "OK":
                print(f"{status:22} {file}")
        sys.exit("STOPPED: raw files do not match docs/raw_file_checksums.csv. "
                 "Run `python src/verify_raw.py` for details. Nothing was cleaned.")

    tables = load_raw()
    df, iqr, src, rev = build_clean(tables)

    # Check the schema BEFORE writing anything, so an undocumented column stops the run early
    undocumented = [c for c in df.columns if c not in SCHEMA]
    missing = [c for c in SCHEMA if c not in df.columns]
    if undocumented or missing:
        sys.exit(f"STOPPED: schema out of date (new={undocumented}, gone={missing}). Nothing was published.")

    # 1. Write to a TEMPORARY file first; the published file is untouched until validation passes
    INTERIM.mkdir(parents=True, exist_ok=True)
    temp_file = OUTPUT_FILE.with_name(OUTPUT_FILE.stem + ".tmp.csv")
    try:
        df.to_csv(temp_file, index=False)

        # 2. Validate what is really on disk: re-read the temporary file and reconcile it with raw
        saved = pd.read_csv(temp_file, usecols=["order_id"])
        checks = reconcile(tables["orders"], saved)
        failed = [name for name, _, ok in checks if ok is False]
        if failed:
            sys.exit(f"STOPPED: validation failed {failed}. The previous published files were left unchanged.")

        # 3. Publish: replace the final CSV in one step (no half-written file is ever visible)
        temp_file.replace(OUTPUT_FILE)
    finally:
        if temp_file.exists():      # failure or crash: remove the temporary file
            temp_file.unlink()

    # 4. Only after the CSV is published, write the success reports
    write_report(raw_results, checks, df, iqr, src, rev)
    write_schema(df)

    print(f"Rows: {len(tables['orders']):,} raw -> {len(saved):,} saved | lost 0 | duplicated 0")
    print(f"Orders with any quality issue: {int(df['flag_any_quality_issue'].sum()):,}")
    print(f"IQR upper limit: {iqr['upper']:.2f} days ({iqr['above']:,} orders above)")
    print(f"Saved: {OUTPUT_FILE.relative_to(ROOT).as_posix()}")
    print(f"Report: {REPORT_FILE.relative_to(ROOT).as_posix()}")
    print(f"Schema: {SCHEMA_FILE.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()