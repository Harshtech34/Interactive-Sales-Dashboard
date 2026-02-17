# src/plots.py
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import pandas as pd
from matplotlib.figure import Figure

sns.set_theme(style="whitegrid")

def boxplot_price_by_product(df: pd.DataFrame) -> Figure:
    fig, ax = plt.subplots(figsize=(8,5))
    sns.boxplot(x='Product', y='Price', data=df, ax=ax)
    ax.set_title('Price Distribution by Product')
    plt.tight_layout()
    return fig

def violin_quantity_by_product(df: pd.DataFrame) -> Figure:
    fig, ax = plt.subplots(figsize=(8,5))
    sns.violinplot(x='Product', y='Quantity', data=df, inner='quartile', ax=ax)
    ax.set_title('Quantity Distribution by Product')
    plt.tight_layout()
    return fig

def correlation_heatmap(df: pd.DataFrame, cols=None) -> Figure:
    if cols is None:
        cols = df.select_dtypes('number').columns.tolist()
    corr = df[cols].corr()
    fig, ax = plt.subplots(figsize=(7,6))
    sns.heatmap(corr, annot=True, fmt='.2f', cmap='vlag', ax=ax)
    ax.set_title('Feature Correlation Heatmap')
    plt.tight_layout()
    return fig

def interactive_sales_over_time(df: pd.DataFrame, date_col='Date', value_col='Total_Sales', freq='D'):
    ts = df.set_index(date_col).resample(freq)[value_col].sum().reset_index()
    fig = px.line(ts, x=date_col, y=value_col, title='Sales Over Time',
                  hover_data={value_col: ':.2f'}, markers=True)
    return fig

def interactive_product_performance(df: pd.DataFrame):
    agg = df.groupby('Product').agg(
        total_revenue=('Total_Sales', 'sum'),
        avg_price=('Price', 'mean'),
        total_quantity=('Quantity', 'sum'),
    ).reset_index().sort_values('total_revenue', ascending=False)
    fig = px.bar(agg, x='Product', y='total_revenue', text='total_revenue',
                 title='Revenue by Product', hover_data=['avg_price', 'total_quantity'])
    return fig
