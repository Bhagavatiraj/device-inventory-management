from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW, PROCESSED, OUTPUT = ROOT/"data/raw", ROOT/"data/processed", ROOT/"output"

def read_source(name, **kwargs):
    excel_path = RAW / f"{name}.xlsx"
    csv_path = RAW / f"{name}.csv"
    if excel_path.exists():
        return pd.read_excel(excel_path, **kwargs)
    return pd.read_csv(csv_path, **kwargs)

def load_and_clean():
    devices = read_source("devices", parse_dates=["purchase_date"])
    employees = read_source("employees")
    tx = read_source("checkout_history",
                     parse_dates=["checkout_timestamp","return_timestamp"])

    report = []
    report.append({"check":"raw_transactions","count":len(tx)})
    report.append({"check":"duplicate_transactions_removed","count":int(tx.duplicated().sum())})
    tx = tx.drop_duplicates()

    invalid_missing = tx["checkout_timestamp"].isna() | tx["return_timestamp"].isna()
    report.append({"check":"missing_timestamps_removed","count":int(invalid_missing.sum())})
    tx = tx.loc[~invalid_missing].copy()

    invalid_order = tx["return_timestamp"] <= tx["checkout_timestamp"]
    report.append({"check":"invalid_timestamp_order_removed","count":int(invalid_order.sum())})
    tx = tx.loc[~invalid_order].copy()

    invalid_ids = ~tx.device_id.isin(devices.device_id) | ~tx.employee_id.isin(employees.employee_id)
    report.append({"check":"invalid_foreign_keys_removed","count":int(invalid_ids.sum())})
    tx = tx.loc[~invalid_ids].copy()

    tx["checkout_duration_hours"] = (tx.return_timestamp - tx.checkout_timestamp).dt.total_seconds()/3600
    tx["checkout_date"] = tx.checkout_timestamp.dt.date
    tx["checkout_month"] = tx.checkout_timestamp.dt.to_period("M").astype(str)

    PROCESSED.mkdir(parents=True, exist_ok=True)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    devices.to_csv(PROCESSED/"devices_clean.csv", index=False)
    employees.to_csv(PROCESSED/"employees_clean.csv", index=False)
    tx.to_csv(PROCESSED/"checkout_history_clean.csv", index=False)
    pd.DataFrame(report).to_csv(OUTPUT/"data_quality_report.csv", index=False)
    return devices, employees, tx

if __name__ == "__main__":
    load_and_clean()
