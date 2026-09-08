import json
from pathlib import Path
import pandas as pd
from scipy.stats import pearsonr, spearmanr

ROOT = Path(__file__).resolve().parents[1]

def run_statistics(device_stats, tx):
    duration = tx.checkout_duration_hours
    summary = {
        "records_analyzed": int(len(tx)),
        "duration_hours": {
            "mean": float(duration.mean()), "median": float(duration.median()),
            "std": float(duration.std()), "min": float(duration.min()),
            "max": float(duration.max()), "q25": float(duration.quantile(.25)),
            "q75": float(duration.quantile(.75))
        }
    }
    turnaround = tx["turnaround_hours"].dropna()
    if len(turnaround):
        summary["turnaround_hours"] = {
            "records_analyzed": int(len(turnaround)),
            "mean": float(turnaround.mean()), "median": float(turnaround.median()),
            "std": float(turnaround.std()), "min": float(turnaround.min()),
            "max": float(turnaround.max()), "q25": float(turnaround.quantile(.25)),
            "q75": float(turnaround.quantile(.75))
        }
    if len(device_stats) > 2:
        p = pearsonr(device_stats.checkout_count, device_stats.utilization_rate)
        s = spearmanr(device_stats.checkout_count, device_stats.utilization_rate)
        summary["checkout_count_vs_utilization"] = {
            "pearson_r": float(p.statistic), "pearson_p_value": float(p.pvalue),
            "spearman_rho": float(s.statistic), "spearman_p_value": float(s.pvalue)
        }
    (ROOT/"output/statistical_summary.json").write_text(json.dumps(summary, indent=2))
    return summary
