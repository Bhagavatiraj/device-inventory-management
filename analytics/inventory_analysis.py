import pandas as pd
import numpy as np

def add_turnaround_metrics(tx):
    enriched = tx.sort_values(["device_id", "checkout_timestamp"]).copy()
    previous_return = enriched.groupby("device_id")["return_timestamp"].cummax().groupby(
        enriched["device_id"]
    ).shift()
    turnaround = (enriched["checkout_timestamp"] - previous_return).dt.total_seconds() / 3600
    enriched["turnaround_hours"] = turnaround.where(turnaround >= 0)
    return enriched

def device_utilization(devices, tx):
    obs_start = tx.checkout_timestamp.min()
    obs_end = tx.return_timestamp.max()
    observation_hours = max((obs_end - obs_start).total_seconds()/3600, 1)
    observation_months = max(
        (obs_end.to_period("M") - obs_start.to_period("M")).n + 1, 1
    )

    agg = tx.groupby("device_id").agg(
        checkout_count=("transaction_id","count"),
        unique_employees=("employee_id","nunique"),
        total_checkout_hours=("checkout_duration_hours","sum"),
        avg_checkout_duration_hours=("checkout_duration_hours","mean"),
        median_checkout_duration_hours=("checkout_duration_hours","median"),
        turnaround_count=("turnaround_hours","count"),
        avg_turnaround_hours=("turnaround_hours","mean"),
        median_turnaround_hours=("turnaround_hours","median")
    ).reset_index()
    agg["borrowing_frequency_per_month"] = agg.checkout_count / observation_months
    agg["utilization_rate"] = (agg.total_checkout_hours/observation_hours).clip(upper=1)
    result = devices.merge(agg, on="device_id", how="left").fillna({
        "checkout_count":0, "unique_employees":0, "total_checkout_hours":0,
        "avg_checkout_duration_hours":0, "median_checkout_duration_hours":0,
        "turnaround_count":0, "avg_turnaround_hours":0,
        "median_turnaround_hours":0, "borrowing_frequency_per_month":0,
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
        avg_borrowing_frequency_per_month=("borrowing_frequency_per_month","mean"),
        avg_utilization_rate=("utilization_rate","mean"),
        avg_checkout_duration_hours=("avg_checkout_duration_hours","mean"),
        avg_turnaround_hours=("avg_turnaround_hours","mean")
    ).reset_index().sort_values("total_checkouts", ascending=False)
