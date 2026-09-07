# Device Inventory Intelligence & Utilization Analytics

## Overview
A Python-based analytics project that simulates organizational device inventory and checkout activity, then measures utilization, demand, employee usage, data quality, and prolonged checkout behavior. The project also trains a baseline Random Forest model for device-demand analytics and exposes results through a Streamlit dashboard.

> **Data transparency:** The included datasets are synthetic and reproducibly generated with a fixed random seed. They are intended for portfolio demonstration and must not be represented as real organizational data.

## Analytics Capabilities
- Data cleaning and quality validation
- Exploratory data analysis
- Device-level utilization measurement
- Employee usage analysis
- Device-type demand analysis
- Descriptive statistics and correlation analysis
- IQR-based prolonged checkout detection
- Quartile-based underutilization/high-utilization segmentation
- Random Forest demand modeling
- Automated reports and interactive dashboard

## Project Structure
```text
analytics/          Analytics pipeline and models
data/raw/           Synthetic source data
data/processed/     Cleaned datasets
dashboard/          Streamlit dashboard
output/             Generated reports, CSVs, plots and model metrics
```

## Quick Start
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
python -m analytics.generate_report
streamlit run dashboard/app.py
```

## Methodology

### Utilization Rate
For each device:

`utilization rate = total checkout duration / common observation period`

### Inventory Segmentation
- Underutilized: bottom utilization quartile
- Highly utilized: top utilization quartile
- Moderate: remaining devices

### Prolonged Checkout Detection
The project uses the IQR rule:

`Q3 + 1.5 × IQR`

Records exceeding this threshold are flagged as statistical duration outliers.

### Predictive Analytics
A Random Forest Regressor models monthly device-category demand using temporal and category features. Evaluation metrics are saved to `output/model_metrics.json`.

## Outputs
Running the pipeline generates:
- `data_quality_report.csv`
- `device_utilization.csv`
- `device_type_summary.csv`
- `employee_usage.csv`
- `underutilized_devices.csv`
- `high_demand_devices.csv`
- `statistical_summary.json`
- `model_metrics.json`
- EDA plots
- Automated Markdown analytics report

