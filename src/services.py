# src/services.py
import pandas as pd
from sqlalchemy import text
from src.db import engine
from datetime import datetime, timedelta
from sklearn.cluster import KMeans

def read_sales_df(query=None):
    if query is None:
        query = "SELECT * FROM sales"
    with engine.connect() as conn:
        df = pd.read_sql_query(text(query), conn, parse_dates=["Date"])
    return df

def kpis_for_period(df):
    total_revenue = float(df["Total_Sales"].sum()) if not df.empty else 0.0
    total_orders = int(len(df))
    avg_order = float(df["Total_Sales"].mean()) if total_orders > 0 else 0.0
    unique_customers = int(df["Customer_ID"].nunique()) if "Customer_ID" in df.columns else None
    return {
        "total_revenue": total_revenue,
        "total_orders": total_orders,
        "avg_order": avg_order,
        "unique_customers": unique_customers,
    }

def filter_by_date(df, start_date, end_date):
    mask = (df["Date"].dt.date >= pd.to_datetime(start_date).date()) & (df["Date"].dt.date <= pd.to_datetime(end_date).date())
    return df.loc[mask].copy()

def period_compare(df, start_date, end_date):
    # current period
    cur = filter_by_date(df, start_date, end_date)
    # previous period same length
    s = pd.to_datetime(start_date).date()
    e = pd.to_datetime(end_date).date()
    length = (e - s).days + 1
    prev_end = s - pd.Timedelta(days=1)
    prev_start = prev_end - pd.Timedelta(days=length - 1)
    prev = filter_by_date(df, prev_start, prev_end)
    cur_kpis = kpis_for_period(cur)
    prev_kpis = kpis_for_period(prev)
    def pct_change(cur_v, prev_v):
        if prev_v == 0:
            return None
        return (cur_v - prev_v) / prev_v * 100.0
    return {
        "current": cur_kpis,
        "previous": prev_kpis,
        "changes_pct": {
            "revenue": pct_change(cur_kpis["total_revenue"], prev_kpis["total_revenue"]),
            "orders": pct_change(cur_kpis["total_orders"], prev_kpis["total_orders"]),
            "avg_order": pct_change(cur_kpis["avg_order"], prev_kpis["avg_order"]),
        }
    }

def rfm_clustering(df, n_clusters=3):
    # RFM: Recency (days since last), Frequency (count), Monetary (sum)
    import pandas as pd
    last_date = df["Date"].max()
    cust = df.groupby("Customer_ID").agg(
        recency=("Date", lambda d: (last_date - d.max()).days),
        frequency=("Date", "count"),
        monetary=("Total_Sales", "sum")
    ).reset_index().dropna(subset=["Customer_ID"])
    if cust.empty:
        return pd.DataFrame(), None
    X = cust[["recency", "frequency", "monetary"]].copy()
    # scale features roughly (simple transform)
    X["recency"] = X["recency"].astype(float)
    X["frequency"] = X["frequency"].astype(float)
    # Use KMeans
    km = KMeans(n_clusters=max(1,n_clusters), random_state=42)
    cust["cluster"] = km.fit_predict(X)
    return cust, km
