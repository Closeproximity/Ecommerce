
# Delivery KPI Methodology

## Analysis population
- Total delivered orders: 96,478
- Eligible orders: 96,470
- Excluded delivered orders: 8
- Exclusion reason: Missing actual customer delivery timestamp.

## KPI definitions

### Average Actual Delivery Time
Purchase timestamp to actual customer delivery timestamp.
Measured in elapsed days.

### Average Estimated Delivery Time
Purchase timestamp to estimated delivery timestamp.
Measured in elapsed days.

### Average Delivery Delay
Actual customer delivery calendar date minus estimated delivery calendar date.
Measured in calendar days.

### Early Delivery
Actual delivery calendar date is before the estimated delivery date.

### On-time Delivery
Actual delivery calendar date equals the estimated delivery date.

### Late Delivery
Actual delivery calendar date is after the estimated delivery date.

## Results

| KPI | Result |
|---|---:|
| Average actual delivery time | 12.56 days |
| Average estimated delivery time | 23.74 days |
| Average delivery delay | -11.88 days |
| Early delivery percentage | 91.89% |
| On-time delivery percentage | 1.34% |
| Late delivery percentage | 6.77% |

## Important limitations
- Results describe historical Olist orders from 2016–2018.
- Non-delivered orders are excluded from delivery classification.
- Eight delivered orders without actual delivery timestamps are excluded.
- Delivery classification uses calendar dates, not exact time-of-day comparisons.
- These descriptive results do not establish causes of delivery performance.
