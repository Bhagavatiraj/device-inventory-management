from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PLOTS = ROOT/"output/plots"

def _save(name):
    PLOTS.mkdir(parents=True, exist_ok=True)
    plt.tight_layout(); plt.savefig(PLOTS/name, dpi=160, bbox_inches="tight"); plt.close()

def create_plots(tx, device_stats, type_summary, feature_importance):
    sns.set_theme(style="whitegrid")

    plt.figure(figsize=(8,5)); sns.histplot(tx.checkout_duration_hours, bins=50, kde=True)
    plt.title("Distribution of Checkout Duration"); plt.xlabel("Hours"); _save("checkout_duration_distribution.png")

    plt.figure(figsize=(8,5)); sns.histplot(device_stats.utilization_rate, bins=30)
    plt.title("Device Utilization Rate Distribution"); plt.xlabel("Utilization Rate"); _save("utilization_distribution.png")

    order = type_summary.sort_values("total_checkouts", ascending=False)
    plt.figure(figsize=(8,5)); sns.barplot(data=order, x="device_type", y="total_checkouts")
    plt.title("Checkout Frequency by Device Type"); plt.xlabel("Device Type"); plt.ylabel("Checkouts"); _save("device_type_demand.png")

    plt.figure(figsize=(8,5)); sns.boxplot(data=device_stats, x="device_type", y="utilization_rate")
    plt.title("Utilization Rate by Device Type"); plt.xticks(rotation=25); _save("utilization_by_device_type.png")

    monthly = tx.groupby("checkout_month").size().reset_index(name="checkouts")
    plt.figure(figsize=(10,5)); sns.lineplot(data=monthly, x="checkout_month", y="checkouts", marker="o")
    plt.title("Monthly Checkout Trend"); plt.xticks(rotation=45); _save("monthly_checkout_trend.png")

    if feature_importance is not None:
        top = feature_importance.head(10)
        plt.figure(figsize=(8,5)); sns.barplot(data=top, x="importance", y="feature")
        plt.title("Demand Model Feature Importance"); _save("feature_importance.png")
