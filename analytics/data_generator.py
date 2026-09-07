"""Generate reproducible synthetic inventory data for portfolio analytics."""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
RNG = np.random.default_rng(42)

DEVICE_CATALOG = [
    ("Laptop", "Dell", "Latitude 5440", 1350),
    ("Laptop", "Apple", "MacBook Air M3", 1550),
    ("Laptop", "Lenovo", "ThinkPad T14", 1250),
    ("Monitor", "Dell", "P2425H", 280),
    ("Monitor", "LG", "27UP850", 420),
    ("Tablet", "Apple", "iPad Air", 650),
    ("Tablet", "Samsung", "Galaxy Tab S9", 720),
    ("Camera", "Canon", "EOS R50", 900),
    ("Camera", "Sony", "Alpha ZV-E10", 820),
    ("Projector", "Epson", "PowerLite", 780),
]
DEPARTMENTS = ["Engineering", "Finance", "Marketing", "Operations", "HR", "Research"]
LOCATIONS = ["Austin", "Dallas", "Houston", "College Station"]
ROLES = ["Analyst", "Engineer", "Manager", "Coordinator", "Researcher"]

def generate():
    RAW.mkdir(parents=True, exist_ok=True)
    n_devices, n_employees, n_tx = 260, 420, 9000

    devices = []
    for i in range(n_devices):
        dtype, manufacturer, model, cost = DEVICE_CATALOG[i % len(DEVICE_CATALOG)]
        devices.append({
            "device_id": f"DEV{i+1:04d}",
            "device_type": dtype,
            "manufacturer": manufacturer,
            "model": model,
            "purchase_date": pd.Timestamp("2022-01-01") + pd.Timedelta(days=int(RNG.integers(0, 1300))),
            "purchase_cost": cost + int(RNG.normal(0, cost * 0.08)),
            "department_owner": RNG.choice(DEPARTMENTS),
            "location": RNG.choice(LOCATIONS),
            "status": RNG.choice(["Available", "Checked Out", "Maintenance"], p=[.75,.20,.05]),
        })
    devices = pd.DataFrame(devices)
    devices.to_csv(RAW/"devices.csv", index=False)

    employees = pd.DataFrame({
        "employee_id": [f"EMP{i+1:04d}" for i in range(n_employees)],
        "department": RNG.choice(DEPARTMENTS, n_employees, p=[.28,.12,.16,.20,.08,.16]),
        "job_role": RNG.choice(ROLES, n_employees),
        "location": RNG.choice(LOCATIONS, n_employees),
    })
    employees.to_csv(RAW/"employees.csv", index=False)

    dates = pd.date_range("2024-01-01", "2026-08-31", freq="D")
    type_weight = {"Laptop": 4.5, "Monitor": 2.7, "Tablet": 1.9, "Camera": 1.0, "Projector": 1.2}
    weights = devices.device_type.map(type_weight).to_numpy()
    weights = weights / weights.sum()
    tx = []
    for i in range(n_tx):
        dev_idx = int(RNG.choice(np.arange(n_devices), p=weights))
        dev = devices.iloc[dev_idx]
        employee = employees.iloc[int(RNG.integers(0, n_employees))]
        base = pd.Timestamp(RNG.choice(dates))
        checkout = base + pd.Timedelta(hours=int(RNG.integers(7, 19)), minutes=int(RNG.integers(0,60)))
        scale = {"Laptop": 96, "Monitor": 144, "Tablet": 60, "Camera": 36, "Projector": 20}[dev.device_type]
        duration = max(2, float(RNG.gamma(shape=2.0, scale=scale)))
        # Long tail creates realistic outliers.
        if RNG.random() < 0.025:
            duration *= float(RNG.uniform(3, 8))
        returned = checkout + pd.Timedelta(hours=duration)
        tx.append({
            "transaction_id": f"TX{i+1:06d}",
            "device_id": dev.device_id,
            "employee_id": employee.employee_id,
            "checkout_timestamp": checkout,
            "return_timestamp": returned,
        })
    tx = pd.DataFrame(tx)

    # Small reproducible data-quality imperfections for cleaning demonstration.
    dup = tx.sample(15, random_state=42)
    tx = pd.concat([tx, dup], ignore_index=True)
    bad_idx = tx.sample(8, random_state=7).index
    tx.loc[bad_idx[:4], "return_timestamp"] = tx.loc[bad_idx[:4], "checkout_timestamp"] - pd.Timedelta(hours=3)
    tx.loc[bad_idx[4:], "return_timestamp"] = pd.NaT

    tx.to_csv(RAW/"checkout_history.csv", index=False)
    print(f"Generated {len(devices)} devices, {len(employees)} employees and {len(tx)} raw transactions.")

if __name__ == "__main__":
    generate()
