# src/utils.py
def format_currency(amount: float, symbol: str = '₹') -> str:
    try:
        return f"{symbol}{amount:,.0f}"
    except Exception:
        return f"{symbol}{amount}"
