# Delivery KPI Methodology

## 1. Analysis Population

- Total delivered orders: 96,478
- Eligible orders: 96,470
- Excluded delivered orders: 8
- Exclusion reason: Missing actual customer delivery timestamp.
- Non-delivered orders are excluded from delivery performance classification.

All delivery classification percentages use 96,470 eligible orders as the denominator.

## 2. KPI Definitions

### Average Actual Delivery Time
Purchase timestamp to actual customer delivery timestamp.

Measured in elapsed days.

### Average Estimated Delivery Time
Purchase timestamp to estimated delivery timestamp.

Measured in elapsed days.

### Average Delivery Delay
Actual customer delivery calendar date minus estimated delivery calendar date.

Measured in calendar days.

- Negative value: Delivered early.
- Zero: Delivered on the estimated date.
- Positive value: Delivered late.

### Early Delivery
Actual delivery calendar date is before the estimated delivery calendar date.

### On-date Delivery
Actual delivery calendar date equals the estimated delivery calendar date.

### Late Delivery
Actual delivery calendar date is after the estimated delivery calendar date.

### On-time Delivery
Actual delivery calendar date is on or before the estimated delivery calendar date.

On-time delivery includes both early and on-date deliveries.

**Formula:**

On-time Delivery Rate = (Early Deliveries + On-date Deliveries) / Eligible Delivered Orders × 100

## 3. Results

| KPI | Result |
|---|---:|
| Average actual delivery time | 12.56 days |
| Average estimated delivery time | 23.74 days |
| Average delivery delay | -11.88 days |
| Early delivery percentage | 91.89% |
| On-date delivery percentage | 1.34% |
| Late delivery percentage | 6.77% |
| **On-time delivery percentage** | **93.23%** |

## 4. Delivery Classification Counts

| Category | Orders |
|---|---:|
| Early | 88,644 |
| On-date | 1,292 |
| Late | 6,534 |
| **Eligible orders** | **96,470** |
| **On-time (early + on-date)** | **89,936** |

## 5. Important Limitations

- Results describe historical Olist orders from 2016–2018.
- Non-delivered orders are excluded from delivery classification.
- Eight delivered orders without actual delivery timestamps are excluded.
- Delivery classification uses calendar dates, not exact time-of-day comparisons.
- Average delivery duration uses elapsed time, while delivery delay uses calendar-day differences.
- These descriptive results do not establish causes of delivery performance.