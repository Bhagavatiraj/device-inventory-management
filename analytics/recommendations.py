import pandas as pd

def generate_recommendations(device_stats, tx):
    under = device_stats[device_stats.utilization_segment=="Underutilized"].sort_values("utilization_rate")
    high = device_stats[device_stats.utilization_segment=="Highly Utilized"].sort_values("utilization_rate", ascending=False)
    q1, q3 = tx.checkout_duration_hours.quantile([.25,.75])
    iqr = q3-q1
    threshold = q3 + 1.5*iqr
    long_tx = tx[tx.checkout_duration_hours > threshold]

    recs = []
    if len(under):
        recs.append(f"{len(under)} devices fall in the bottom utilization quartile and should be reviewed for reallocation before new purchases.")
    if len(high):
        recs.append(f"{len(high)} devices fall in the top utilization quartile; these assets should be monitored for capacity constraints.")
    recs.append(f"{len(long_tx)} checkout records exceed the IQR-based prolonged-duration threshold of {threshold:.1f} hours.")
    return recs, under, high, long_tx
