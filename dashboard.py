# dashboard.py
import streamlit as st
from src.services import (
    read_sales_df,
    kpis_for_period,
    period_compare,
    rfm_clustering,
    filter_by_date,
)
from src.seed_data import seed_from_csv
import pandas as pd
import os
from datetime import timedelta

st.set_page_config(
    page_title="Interactive Sales Dashboard (Internship)",
    layout="wide",
    page_icon=":bar_chart:",
)

# -------------------------------
# SIDEBAR: Upload + Filters
# -------------------------------
st.sidebar.title("Data & Filters")
uploaded = st.sidebar.file_uploader(
    "Upload sales CSV to seed DB (optional)", type=["csv"]
)

if uploaded is not None:
    if st.session_state.get("last_uploaded_name") != uploaded.name:

        os.makedirs("data", exist_ok=True)
        temp_path = os.path.join("data", "uploaded_sales.csv")

        with open(temp_path, "wb") as f:
            f.write(uploaded.getbuffer())

        seed_from_csv(csv_path=temp_path, drop_existing=True)

        st.session_state["last_uploaded_name"] = uploaded.name
        st.sidebar.success("Database seeded successfully!")
        st.rerun()


# -------------------------------
# Load Data
# -------------------------------
df = read_sales_df()

if df.empty:
    st.warning(
        "No data found in DB. Run `python src/seed_data.py` or upload CSV in sidebar."
    )
    st.stop()

# Ensure Date column is datetime
df["Date"] = pd.to_datetime(df["Date"])

# -------------------------------
# Default Date Filter
# -------------------------------
min_date = df["Date"].min().date()
max_date = df["Date"].max().date()

date_range = st.sidebar.date_input(
    "Date range",
    [min_date, max_date],
    min_value=min_date,
    max_value=max_date,
)

# -------------------------------
# Product & Region Filters
# -------------------------------
products = st.sidebar.multiselect(
    "Products",
    options=sorted(df["Product"].unique()),
    default=sorted(df["Product"].unique()),
)

regions = []
if "Region" in df.columns:
    region_list = sorted(df["Region"].dropna().unique())
    regions = st.sidebar.multiselect(
        "Regions",
        options=region_list,
        default=region_list,
    )

# Apply product + region filters
df_filtered = df.copy()

if products:
    df_filtered = df_filtered[df_filtered["Product"].isin(products)]

if regions:
    df_filtered = df_filtered[df_filtered["Region"].isin(regions)]

# Apply date filter
start_date, end_date = date_range[0], date_range[1]
df_period = filter_by_date(df_filtered, start_date, end_date)

# -------------------------------
# KPI Section
# -------------------------------
comp = period_compare(df_filtered, start_date, end_date)
cur = comp["current"]
changes = comp["changes_pct"]

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Revenue",
    f"₹{cur['total_revenue']:,.0f}",
    delta=None
    if changes["revenue"] is None
    else f"{round(changes['revenue'], 2)}%",
)

col2.metric(
    "Total Orders",
    f"{cur['total_orders']}",
    delta=None
    if changes["orders"] is None
    else f"{round(changes['orders'], 2)}%",
)

col3.metric(
    "Avg Revenue / Order",
    f"₹{cur['avg_order']:,.0f}",
    delta=None
    if changes["avg_order"] is None
    else f"{round(changes['avg_order'], 2)}%",
)

col4.metric(
    "Unique Customers",
    f"{cur['unique_customers'] if cur['unique_customers'] is not None else 'N/A'}",
)

st.markdown("---")

# -------------------------------
# Charts Layout
# -------------------------------
left, right = st.columns((3, 1))

with left:
    st.subheader("Sales Over Time")

    ts = (
        df_period.set_index("Date")
        .resample("D")["Total_Sales"]
        .sum()
        .reset_index()
    )

    st.line_chart(
        ts.rename(columns={"Date": "index"})
        .set_index("index")["Total_Sales"]
    )

    st.subheader("Product Performance")

    prod_agg = (
        df_period.groupby("Product")
        .agg(
            total_revenue=("Total_Sales", "sum"),
            total_quantity=("Quantity", "sum"),
        )
        .reset_index()
        .sort_values("total_revenue", ascending=False)
    )

    if not prod_agg.empty:
        st.bar_chart(prod_agg.set_index("Product")["total_revenue"])

    st.subheader("Statistical Visuals")

    from src.plots import (
        boxplot_price_by_product,
        violin_quantity_by_product,
        correlation_heatmap,
    )

    st.pyplot(boxplot_price_by_product(df_period))
    st.pyplot(violin_quantity_by_product(df_period))
    st.pyplot(correlation_heatmap(df_period))

with right:
    st.subheader("Business Insights")

    if not prod_agg.empty:
        top_product = prod_agg.iloc[0]["Product"]
        st.markdown(f"**Top Product:** {top_product}")

    if "Region" in df_period.columns and not df_period["Region"].isna().all():
        top_region = (
            df_period.groupby("Region")["Total_Sales"]
            .sum()
            .idxmax()
        )
        st.markdown(f"**Top Region:** {top_region}")

    st.markdown("**Interpretation**")
    st.write(
        """
        - Check revenue delta vs previous period in KPIs.
        - Use date filters to evaluate promotional windows.
        - RFM segmentation below helps identify high-value customers.
        """
    )

    st.download_button(
        "Download filtered CSV",
        df_period.to_csv(index=False).encode("utf-8"),
        file_name="filtered_sales.csv",
        mime="text/csv",
    )

# -------------------------------
# RFM Segmentation
# -------------------------------
st.markdown("---")
st.subheader("Customer Segmentation (RFM)")

cust_df, km = rfm_clustering(df_period, n_clusters=3)

if not cust_df.empty:
    st.dataframe(
        cust_df.sort_values("monetary", ascending=False).head(20)
    )
    st.bar_chart(cust_df["cluster"].value_counts().sort_index())
else:
    st.info(
        "Not enough customer data for segmentation (requires Customer_ID)."
    )

# -------------------------------
# Raw Data
# -------------------------------
st.markdown("---")
st.subheader("Data Table (sample)")
st.dataframe(df_period.head(200))

st.markdown("---")
st.subheader("How to interpret this dashboard")

st.write(
    """
    - The KPIs at the top show the current period and % change vs the previous period of equal length.
    - Use filters to drill into product or region performance.
    - RFM clusters can be used for retention marketing.
    """
)
