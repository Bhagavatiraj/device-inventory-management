from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib, json

ROOT = Path(__file__).resolve().parents[1]

def forecast_monthly_demand(tx):
    monthly = tx.groupby(["checkout_month","device_id"]).size().reset_index(name="checkout_count")
    monthly["date"] = pd.to_datetime(monthly["checkout_month"] + "-01")
    monthly["month_num"] = monthly.date.dt.month
    monthly["year"] = monthly.date.dt.year
    # Aggregate by device type is more useful for operational demand planning.
    device_map = None
    # infer device type not available here; caller passes merged data if needed
    return monthly

def train_demand_model(tx, devices):
    data = tx.merge(devices[["device_id","device_type"]], on="device_id", how="left")
    monthly = data.groupby(["checkout_month","device_type"]).size().reset_index(name="demand")
    monthly["date"] = pd.to_datetime(monthly.checkout_month + "-01")
    monthly["month"] = monthly.date.dt.month
    monthly["quarter"] = monthly.date.dt.quarter
    monthly["year"] = monthly.date.dt.year
    monthly = pd.get_dummies(monthly, columns=["device_type"], dtype=int)
    monthly = monthly.sort_values("date").reset_index(drop=True)
    monthly["lag_1"] = monthly.groupby("year")["demand"].shift(1).fillna(monthly.demand.median())
    features = [c for c in monthly.columns if c not in ["checkout_month","date","demand"]]
    split = int(len(monthly)*0.8)
    train, test = monthly.iloc[:split], monthly.iloc[split:]
    model = RandomForestRegressor(n_estimators=300, random_state=42, min_samples_leaf=2)
    model.fit(train[features], train.demand)
    pred = model.predict(test[features])
    metrics = {
        "MAE": float(mean_absolute_error(test.demand, pred)),
        "RMSE": float(np.sqrt(mean_squared_error(test.demand, pred))),
        "R2": float(r2_score(test.demand, pred))
    }
    model_dir = ROOT/"output/models"; model_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump({"model":model,"features":features}, model_dir/"demand_forecast_model.joblib")
    (ROOT/"output/model_metrics.json").write_text(json.dumps(metrics, indent=2))
    fi = pd.DataFrame({"feature":features,"importance":model.feature_importances_}).sort_values("importance", ascending=False)
    fi.to_csv(ROOT/"output/feature_importance.csv", index=False)
    return metrics, fi
