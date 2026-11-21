# Data Quality Audit

**Project:** E-commerce Delivery & Logistics Performance Analysis
**Owner:** M2 – Data Quality Analyst
**Source:** Brazilian E-Commerce Public Dataset by Olist (see `docs/dataset_provenance.md`)

**Evidence**

| File | What it proves |
|---|---|
| `notebooks/00_data_audit.ipynb` | How each problem was found (12 checks with findings) |
| `src/clean.py` | Every rule below implemented as a column |
| `docs/cleaning_validation.md` | Generated on every run: row reconciliation, order-level count for every rule, exact IQR calculation |
| `docs/raw_file_checksums.csv` + `src/verify_raw.py` | Raw files are byte-for-byte the audited versions |

## 1. Before / After Summary

| Stage | Orders |
|---|---:|
| Raw orders (`olist_orders_dataset.csv`) | 99,441 |
| Orders flagged by at least one data-quality rule (DQ-01 to DQ-07, DQ-09) | 2,186 (2.20%) |
| Orders excluded | **0** |
| Orders in cleaned dataset (`data/interim/orders_clean.csv`) | 99,441 |

Long deliveries (DQ-08) and the context rules (DQ-10 to DQ-13) are flagged separately and not counted above, because they describe real situations, not data errors.

**Policy: flag, don't delete.** No record is removed. Every rule adds a column, so each KPI owner (M3, M6) decides which flags to exclude for their KPI and reports that exclusion as part of the denominator.

## 2. Data Quality Rules

All 13 rules are implemented in `src/clean.py`. "Source rows affected" is counted where the problem lives (order, product or item); "Orders flagged" is the order-level count in the cleaned dataset. Both are regenerated in `docs/cleaning_validation.md` on every run.

| Rule ID | Description | Source rows affected | Orders flagged | % of orders | Implemented as (column in `orders_clean.csv`) | Action | Reason |
|---|---|---:|---:|---:|---|---|---|
| DQ-01 | Status `delivered` but no customer delivery date | 8 orders | 8 | 0.01% | `flag_delivered_no_delivery_date` | Flag | Delivery time and on-time status cannot be measured |
| DQ-02 | Status `canceled` but has a customer delivery date | 6 orders | 6 | 0.01% | `flag_canceled_with_delivery_date` | Flag | Status and timestamp contradict each other |
| DQ-03 | Status `delivered` but no carrier (dispatch) date | 2 orders | 2 | <0.01% | `flag_delivered_no_carrier_date` | Flag | Processing and transit time cannot be split |
| DQ-04 | Status `delivered` but no approval date | 14 orders | 14 | 0.01% | `flag_delivered_no_approval_date` | Flag | Processing time from approval cannot be measured |
| DQ-05 | Carrier date earlier than purchase date | 166 orders | 166 | 0.17% | `flag_carrier_before_purchase` | Flag | Impossible order of events |
| DQ-06 | Carrier date earlier than approval date | 1,359 orders | 1,359 | 1.37% | `flag_carrier_before_approval` | Flag | Suspicious, likely system timing; affects processing-time KPI |
| DQ-07 | Customer delivery date earlier than carrier date | 23 orders | 23 | 0.02% | `flag_delivered_before_carrier` | Flag | Impossible order of events |
| DQ-08 | Delivery time above IQR upper limit (29.15 days, see section 5) | 4,896 orders | 4,896 | 4.92% | `flag_long_delivery` | Flag, **keep** | Real long deliveries, not errors; core to delay analysis |
| DQ-09 | Order has no items in `order_items` | 775 orders | 775 | 0.78% | `flag_no_items`, `item_count` | Flag | No price or freight available for these orders |
| DQ-10 | Order has more than one review | 547 orders | 547 | 0.55% | `flag_multiple_reviews`, `review_count`, `review_score_latest`, `review_score_mean` | One score per order (section 6) | Avoids double-counting ratings |
| DQ-11 | Product has no category | 610 products | 1,451 | 1.46% | `flag_item_unknown_category`, `items_unknown_category` | Flag; label `unknown` in analysis | Never drop; keep as its own segment |
| DQ-12 | Category has no English translation (`pc_gamer`, `portateis_cozinha_e_preparadores_de_alimentos`) | 13 products | 22 | 0.02% | `flag_item_untranslated_category`, `items_untranslated_category` | Flag; keep Portuguese name | Translation table is incomplete |
| DQ-13 | Item freight value is 0 | 383 items | 339 | 0.34% | `flag_item_zero_freight`, `items_zero_freight` | Flag, **keep** | Plausible free shipping, not an error |

DQ-11 to DQ-13 are product/item problems. Because the cleaned dataset is one row per order, an order is flagged when **at least one** of its items is affected, and the `items_*` count columns say how many.

## 3. Checks Passed (no action needed)

| Check | Result |
|---|---|
| Exact duplicate rows (7 tables) | 0 in every table |
| Duplicate `order_id` in orders | 0 → one row per order confirmed |
| Status labels | 8 consistent lowercase values |
| Date parsing (5 columns, format `YYYY-MM-DD HH:MM:SS`) | 0 failures |
| Approval before purchase / delivery before purchase / estimate before purchase | 0 each |
| Review scores outside 1–5 | 0 |
| Price ≤ 0 or negative freight | 0 |
| Orders without a customer / items without an order / reviews without an order | 0 each |
| Customer state codes | 27 clean codes (26 states + DF) |

## 4. Missing Values Considered Normal

| Column | Missing | Why it is acceptable |
|---|---:|---|
| `review_comment_title` | 87,656 (88.34%) | Optional free-text field |
| `review_comment_message` | 58,247 (58.70%) | Optional free-text field |
| `order_delivered_customer_date` (non-delivered orders) | 2,957 | Orders that never reached the customer |
| `order_delivered_carrier_date` (non-dispatched orders) | 1,781 | Orders that never reached the courier |
| Product weight / dimensions | 2 products | Not used in Project 1 |

## 5. DQ-08 Threshold: How 29.15 Days Is Calculated

1. **Population:** orders with status `delivered` **and** a customer delivery date (n = 96,470).
2. **Measure:** `delivery_days` = (`order_delivered_customer_date` − `order_purchase_timestamp`) in seconds ÷ 86,400, so fractions of a day are kept.
3. **Quartiles:** `pandas.Series.quantile(0.25)` and `quantile(0.75)`, default linear interpolation.
4. **Rule:** upper limit = Q3 + 1.5 × (Q3 − Q1). Orders strictly above it are flagged.

| Step | Exact value (days) | Rounded |
|---|---:|---:|
| Q1 (25th percentile) | 6.7662 | 6.77 |
| Q3 (75th percentile) | 15.7202 | 15.72 |
| IQR = Q3 − Q1 | 8.9540 | 8.95 |
| 1.5 × IQR | 13.4310 | 13.43 |
| **Upper limit = Q3 + 1.5 × IQR** | **29.1512** | **29.15** |
| Orders above the limit | 4,896 | |

Source: `docs/cleaning_validation.md` section 4. The limit is recalculated from the data on every run, never hard-coded.

## 6. Multiple Reviews per Order (DQ-10): Handling Rule

**Facts:** 547 orders have more than one review (543 have 2, 4 have 3 or more), and in **202 of them the scores disagree**, so the rule changes the result. 814 `review_id`s are shared by several orders (one review left for orders bought together). 768 orders have no review.

**Proposed rule (status: awaiting M3 confirmation):** use the **latest review per order**, the one with the newest `review_answer_timestamp`. Ties are broken by `review_creation_date`, then `review_id`, so the result is identical on every run.

**Why latest:** it reflects the customer's final opinion after the delivery outcome is known, and it keeps exactly one score per order, so no order is counted twice in rating KPIs.

**Columns provided so M3 can choose without re-running anything:**

| Column | Meaning |
|---|---|
| `review_count` | Number of reviews for the order (0 = no review) |
| `review_score_latest` | Score under the proposed rule; empty if no review |
| `review_score_mean` | Average score, if M3 prefers the mean |
| `flag_multiple_reviews` | `True` when `review_count` > 1 |

A shared `review_id` gives each linked order the same score. Orders with no review are excluded from rating KPIs only, and that count must be stated with the KPI. **M3 to confirm or change the rule; the decision will be recorded in `docs/decisions_log.md`.**

## 7. Reproduce and Verify (any OS)

From the project root, with the virtual environment active:

```bash
python src/verify_raw.py   # 1. raw files match the audited fingerprints (all OK, exit code 0)
python src/clean.py        # 2. writes data/interim/orders_clean.csv and docs/cleaning_validation.md
```

- All paths are relative to the project root and use `/`, so the same commands work on Windows, macOS and Linux.
- `clean.py` stops with an error if any order is lost, added or duplicated.
- If `verify_raw.py` reports a mismatch, re-download the dataset from Kaggle. Run `python src/verify_raw.py --update` only if the team agrees to move to a new dataset version.

## 8. Notes and Limitations

- **Raw data unchanged:** SHA-256 fingerprints and sizes of all 9 raw files are stored in `docs/raw_file_checksums.csv`.
- **Geolocation table not used:** the project has no distance field, and one ZIP prefix maps to many coordinates.
- **Timezone:** timestamps are kept as stored in the source (Brazil local time); no conversion applied.
- **Source column misspellings:** `product_name_lenght` and `product_description_lenght` are misspelled in the original Olist data and left unchanged.
- Flags describe data issues only. They do not imply causes of delivery performance.