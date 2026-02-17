# src/data_processing.py
import pandas as pd
from typing import Union
from io import StringIO

def load_sales_data(path_or_buffer: Union[str, StringIO]) -> pd.DataFrame:
    """
    Load CSV from a file path or file-like object, parse dates and numeric columns,
    and ensure Total_Sales exists.
    """
    df = pd.read_csv(path_or_buffer)
    df.columns = [c.strip() for c in df.columns]

    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

    for col in ['Quantity', 'Price', 'Total_Sales']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    if 'Total_Sales' not in df.columns or df['Total_Sales'].isnull().any():
        if {'Quantity', 'Price'}.issubset(df.columns):
            df['Total_Sales'] = df['Quantity'].multiply(df['Price'])

    df = df.dropna(subset=['Date', 'Product', 'Total_Sales'])
    df = df.sort_values('Date').reset_index(drop=True)
    return df

def add_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df['year'] = df['Date'].dt.year
    df['month'] = df['Date'].dt.month
    df['day'] = df['Date'].dt.day
    df['revenue_per_unit'] = df['Total_Sales'] / df['Quantity'].replace(0, 1)
    return df

def aggregate_kpis(df: pd.DataFrame) -> dict:
    return {
        'total_revenue': float(df['Total_Sales'].sum()),
        'total_orders': int(len(df)),
        'avg_revenue_per_order': float(df['Total_Sales'].mean()) if len(df) > 0 else 0.0,
        'unique_customers': int(df['Customer_ID'].nunique()) if 'Customer_ID' in df.columns else None
    }
