import pandas as pd
import numpy as np

def device_utilization(devices, tx):
    obs_start = tx.checkout_timestamp.min()
    obs_end = tx.return_timestamp.max()
    observation_hours = max((obs_end - obs_start).total_seconds()/3600, 1)

    agg = tx.groupby("device_id").agg(
        checkout_count=("transaction_id","count"),
        unique_employees=("employee_id","nunique"),
        total_checkout_hours=("checkout_duration_hours","sum"),
        avg_checkout_duration_hours=("checkout_duration_hours","mean"),
        median_checkout_duration_hours=("checkout_duration_hours","median")
    ).reset_index()
    agg["utilization_rate"] = (agg.total_checkout_hours/observation_hours).clip(upper=1)
    result = devices.merge(agg, on="device_id", how="left").fillna({
        "checkout_count":0, "unique_employees":0, "total_checkout_hours":0,
        "avg_checkout_duration_hours":0, "median_checkout_duration_hours":0,
        "utilization_rate":0
    })
    q25, q75 = result.utilization_rate.quantile([.25,.75])
    result["utilization_segment"] = np.select(
        [result.utilization_rate <= q25, result.utilization_rate >= q75],
        ["Underutilized","Highly Utilized"], default="Moderately Utilized"
    )
    return result, observation_hours

def device_type_summary(device_stats):
    return device_stats.groupby("device_type").agg(
        devices=("device_id","count"),
        total_checkouts=("checkout_count","sum"),
        avg_utilization_rate=("utilization_rate","mean"),
        avg_checkout_duration_hours=("avg_checkout_duration_hours","mean")
    ).reset_index().sort_values("total_checkouts", ascending=False)
