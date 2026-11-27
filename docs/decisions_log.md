# Decisions Log

Team decisions for Project 1 (E-commerce Delivery & Logistics Performance Analysis).
Each decision records who decided, why, and where it is implemented, so the analysis can be reproduced and explained.

| ID | Date | Decision | Decided by | Reason | Implemented in |
|---|---|---|---|---|---|
| D-01 | 26 Nov 2026 | **DQ-10 rating rule: use the latest review per order** (`review_score_latest`). Ordering: `review_answer_timestamp`, falling back to `review_creation_date`; a review with no date counts as oldest; ties by `review_creation_date`, then `review_id`. | Proposed by M2 (Charvi), confirmed by M3 (Ali) | Reflects the customer's final opinion once the delivery outcome is known, and gives one whole-number score per order, so the 1–5 star distribution stays valid. 547 orders have more than one review and 202 of them disagree, so `review_score_mean` is kept as a sensitivity check. | `src/clean.py`, `docs/data_quality_audit.md` (section 6, v1.2), `docs/kpi_definitions_m3.md` (section 2) |

## How to add a decision

Add a new row with the next ID (D-02, D-03, ...), today's date, who decided, the reason, and the files where it is used. Never delete an old row; if a decision changes, add a new row that says which ID it replaces.