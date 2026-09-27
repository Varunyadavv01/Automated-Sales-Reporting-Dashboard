import pandas as pd
import json

sales = pd.read_csv("sales_data.csv")
sku_class = pd.read_csv("sku_classification.csv")
replen = pd.read_csv("replenishment_plan.csv")
picklist = pd.read_csv("fifo_picklist.csv")

# Network-wide daily sales trend
daily = sales.groupby("date")["revenue"].sum().reset_index()
daily["date"] = pd.to_datetime(daily["date"])
daily = daily.sort_values("date")
daily_trend = {
    "labels": daily["date"].dt.strftime("%b %d").tolist()[::5],
    "values": daily["revenue"].round(0).tolist()[::5],
}

abc_dist = sku_class["abc_class"].value_counts().reindex(["A", "B", "C"]).to_dict()
abc_revenue = sku_class.groupby("abc_class")["total_revenue"].sum().reindex(["A", "B", "C"]).round(0).to_dict()

category_rev = sales.groupby("category")["revenue"].sum().sort_values(ascending=False).round(0)

store_perf = sales.groupby("store")["revenue"].sum().sort_values(ascending=False).round(0)

stockout_risk = replen["stockout_risk"].value_counts().to_dict()
expiry_risk = picklist["expiry_risk"].value_counts().reindex(["Urgent", "Watch", "OK"]).to_dict()

kpis = {
    "total_revenue": round(sales["revenue"].sum(), 0),
    "total_units": int(sales["units_sold"].sum()),
    "n_stores": sales["store"].nunique(),
    "n_skus": sales["sku_id"].nunique(),
    "orders_needed": int((replen["recommended_order_qty"] > 0).sum()),
    "total_reorder_units": int(replen["recommended_order_qty"].sum()),
    "high_stockout_risk": int((replen["stockout_risk"] == "High").sum()),
    "urgent_expiry_batches": int((picklist["expiry_risk"] == "Urgent").sum()),
    "slow_movers": int(len(pd.read_csv("slow_moving_candidates.csv"))),
}

data = {
    "kpis": kpis,
    "daily_trend": daily_trend,
    "abc_dist": abc_dist,
    "abc_revenue": abc_revenue,
    "category_labels": category_rev.index.tolist(),
    "category_values": category_rev.values.tolist(),
    "store_labels": store_perf.index.tolist(),
    "store_values": store_perf.values.tolist(),
    "stockout_risk": stockout_risk,
    "expiry_risk": expiry_risk,
}

with open("dashboard_data.json", "w") as f:
    json.dump(data, f)

print("dashboard_data.json written")
print(json.dumps(kpis, indent=2))
