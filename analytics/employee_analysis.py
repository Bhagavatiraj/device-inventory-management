def employee_usage(employees, tx):
    usage = tx.groupby("employee_id").agg(
        checkout_count=("transaction_id","count"),
        total_checkout_hours=("checkout_duration_hours","sum"),
        avg_checkout_duration_hours=("checkout_duration_hours","mean")
    ).reset_index()
    preferred = tx.groupby(["employee_id","device_id"]).size().reset_index(name="n")
    preferred = preferred.sort_values(["employee_id","n"], ascending=[True,False]).drop_duplicates("employee_id")
    out = employees.merge(usage, on="employee_id", how="left").merge(
        preferred[["employee_id","device_id"]].rename(columns={"device_id":"most_frequently_borrowed_device"}),
        on="employee_id", how="left"
    ).fillna({"checkout_count":0,"total_checkout_hours":0,"avg_checkout_duration_hours":0})
    return out.sort_values("checkout_count", ascending=False)
