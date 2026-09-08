from pathlib import Path
import json
from analytics.data_generator import generate
from analytics.data_cleaning import load_and_clean
from analytics.inventory_analysis import add_turnaround_metrics, device_utilization, device_type_summary
from analytics.employee_analysis import employee_usage
from analytics.statistical_analysis import run_statistics
from analytics.forecasting import train_demand_model
from analytics.visualizations import create_plots
from analytics.recommendations import generate_recommendations

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/"output"

def main():
    # Generate only if raw data is absent.
    if not (ROOT/"data/raw/checkout_history.csv").exists():
        generate()

    devices, employees, tx = load_and_clean()
    tx = add_turnaround_metrics(tx)
    tx.to_csv(ROOT/"data/processed/checkout_history_clean.csv", index=False)
    device_stats, observation_hours = device_utilization(devices, tx)
    type_summary = device_type_summary(device_stats)
    emp = employee_usage(employees, tx)
    stats = run_statistics(device_stats, tx)
    metrics, fi = train_demand_model(tx, devices)
    create_plots(tx, device_stats, type_summary, fi)
    recs, under, high, long_tx = generate_recommendations(device_stats, tx)

    device_stats.to_csv(OUT/"device_utilization.csv", index=False)
    type_summary.to_csv(OUT/"device_type_summary.csv", index=False)
    emp.to_csv(OUT/"employee_usage.csv", index=False)
    under.to_csv(OUT/"underutilized_devices.csv", index=False)
    high.to_csv(OUT/"high_demand_devices.csv", index=False)

    report = f"""# Device Inventory Intelligence Report

## Dataset
- Clean checkout records analyzed: **{len(tx):,}**
- Devices analyzed: **{len(devices):,}**
- Employees represented: **{len(employees):,}**
- Observation period: **{observation_hours/24:.0f} days**

## Checkout Duration
- Mean: **{stats['duration_hours']['mean']:.2f} hours**
- Median: **{stats['duration_hours']['median']:.2f} hours**
- Standard deviation: **{stats['duration_hours']['std']:.2f} hours**

## Borrowing and Turnaround
- Average borrowing frequency: **{device_stats['borrowing_frequency_per_month'].mean():.2f} checkouts per device-month**
- Average device turnaround: **{stats['turnaround_hours']['mean']:.2f} hours**
- Median device turnaround: **{stats['turnaround_hours']['median']:.2f} hours**

## Predictive Demand Model
- MAE: **{metrics['MAE']:.2f}**
- RMSE: **{metrics['RMSE']:.2f}**
- R²: **{metrics['R2']:.3f}**

## Operational Findings
""" + "\n".join(f"- {r}" for r in recs) + """

## Methodology Notes
Utilization is calculated as total checkout duration divided by the common observation period. Borrowing frequency is the number of checkouts per device-month. Turnaround is the non-overlapping time between a device return and its next checkout; overlapping records are excluded from turnaround averages. Underutilized and highly utilized devices are defined using the bottom and top utilization quartiles. Prolonged checkout records are identified using the IQR outlier rule.

## Limitation
The included source data is synthetic and intended for portfolio demonstration. The analytics pipeline can be applied to real organizational checkout data with compatible fields.
"""
    (OUT/"reports").mkdir(exist_ok=True)
    (OUT/"reports/inventory_analytics_report.md").write_text(report)
    print("Analytics pipeline complete. See output/ for reports, metrics, CSVs and plots.")

if __name__ == "__main__":
    main()
