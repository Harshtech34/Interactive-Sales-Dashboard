# tests/test_services.py
import os
import pandas as pd
from src.seed_data import seed_from_csv, create_db
from src.services import read_sales_df, kpis_for_period, period_compare

def test_seed_and_read(tmp_path):
    # copy example small CSV to tmp and seed
    sample = """Date,Product,Quantity,Price,Customer_ID,Region,Total_Sales
2024-01-01,Phone,1,100,C001,East,100
2024-01-02,Phone,2,150,C002,West,300
"""
    p = tmp_path / "sample.csv"
    p.write_text(sample)
    # seed into in-repo DB (warning: will create file in repo/data when run); for CI you might set a tmp DB path
    seed_from_csv(csv_path=str(p), drop_existing=True)
    df = read_sales_df()
    assert not df.empty
    kpis = kpis_for_period(df)
    assert kpis["total_revenue"] >= 0
