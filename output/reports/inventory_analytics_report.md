# Device Inventory Intelligence Report

## Dataset
- Clean checkout records analyzed: **8,992**
- Devices analyzed: **260**
- Employees represented: **420**
- Observation period: **1099 days**

## Checkout Duration
- Mean: **206.61 hours**
- Median: **148.30 hours**
- Standard deviation: **244.02 hours**

## Predictive Demand Model
- MAE: **7.15**
- RMSE: **9.74**
- R²: **0.963**

## Operational Findings
- 65 devices fall in the bottom utilization quartile and should be reviewed for reallocation before new purchases.
- 65 devices fall in the top utilization quartile; these assets should be monitored for capacity constraints.
- 477 checkout records exceed the IQR-based prolonged-duration threshold of 533.1 hours.

## Methodology Notes
Utilization is calculated as total checkout duration divided by the common observation period. Underutilized and highly utilized devices are defined using the bottom and top utilization quartiles. Prolonged checkout records are identified using the IQR outlier rule.

## Limitation
The included source data is synthetic and intended for portfolio demonstration. The analytics pipeline can be applied to real organizational checkout data with compatible fields.
