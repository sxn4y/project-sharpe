# risk.py
import yfinance as yf
import pandas as pd
import numpy as np

# default tickers
tickers = ["AAPL", "NVDA", "TSLA", "MSFT", "GOOG", "AMZN"]

def safe_find_key(df, possible_keys):
    """Return the first matching key from DataFrame index."""
    for key in possible_keys:
        for existing in df.index:
            if key.lower() in existing.lower():
                return existing
    return None

def get_from_df(df, possible_keys):
    """Get the latest value from any matching key in DataFrame."""
    key = safe_find_key(df, possible_keys)
    if key:
        val = df.loc[key].iloc[0]
        return float(val) if pd.notna(val) else np.nan
    return np.nan

def fetch_financials(ticker):
    """Fetch financial data with multiple fallbacks."""
    t = yf.Ticker(ticker)
    try:
        bs = t.balance_sheet
        is_ = t.financials
    except Exception as e:
        raise ValueError(f"Could not fetch data: {e}")

    if bs.empty and not t.quarterly_balance_sheet.empty:
        bs = t.quarterly_balance_sheet
    if is_.empty and not t.quarterly_financials.empty:
        is_ = t.quarterly_financials

    if bs.empty or is_.empty:
        raise ValueError("No financial data available.")

    data = {
        "total_assets": get_from_df(bs, ["Total Assets"]),
        "total_liabilities": get_from_df(bs, ["Total Liab", "Total Liabilities Net Minority Interest"]),
        "current_assets": get_from_df(bs, ["Total Current Assets", "Current Assets"]),
        "current_liabilities": get_from_df(bs, ["Total Current Liabilities", "Current Liabilities"]),
        "retained_earnings": get_from_df(bs, ["Retained Earnings"]),
        "ebit": get_from_df(is_, ["EBIT", "Ebit", "Operating Income"]),
        "total_revenue": get_from_df(is_, ["Total Revenue", "Revenue"]),
        "market_cap": t.info.get("marketCap", np.nan)
    }

    # Validate minimal requirements
    required = ["total_assets", "total_liabilities", "current_assets", "current_liabilities", "total_revenue"]
    if any(np.isnan(data[k]) for k in required):
        raise ValueError("Missing critical data fields.")

    # Replace missing optional fields with 0
    for k in ["retained_earnings", "ebit", "market_cap"]:
        if np.isnan(data[k]):
            data[k] = 0

    return data

def altman_z_score(data):
    """Compute Altman Z-score."""
    TA = data["total_assets"]
    if TA <= 0:
        return np.nan
    A = (data["current_assets"] - data["current_liabilities"]) / TA
    B = data["retained_earnings"] / TA
    C = data["ebit"] / TA
    D = data["market_cap"] / data["total_liabilities"] if data["total_liabilities"] > 0 else 0
    E = data["total_revenue"] / TA
    return 1.2*A + 1.4*B + 3.3*C + 0.6*D + 1.0*E

def bankruptcy_probability(Z):
    """Estimate 4-year bankruptcy probability from Z-score."""
    if np.isnan(Z):
        return np.nan
    prob = 1 / (1 + np.exp(1.5 * (Z - 2.5)))  # logistic approximation
    return round(prob * 100, 2)

def risk_report(ticker):
    """Generate risk report for a given ticker."""
    try:
        data = fetch_financials(ticker)
        Z = altman_z_score(data)
        prob = bankruptcy_probability(Z)
        zone = "Safe" if Z > 2.99 else ("Grey" if Z > 1.8 else "Distress")
        return {
            "Ticker": ticker,
            "Altman Z": round(Z, 2),
            "4Y Bankruptcy Probability (%)": prob,
            "Zone": zone
        }
    except Exception as e:
        return {"Ticker": ticker, "Error": str(e)}

if __name__ == "__main__":
    print("\n📉 4-Year Bankruptcy Risk Report\n")
    reports = [risk_report(t) for t in tickers]
    df = pd.DataFrame(reports)
    print(df.to_string(index=False))
