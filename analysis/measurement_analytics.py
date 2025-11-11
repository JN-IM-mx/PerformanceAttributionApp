"""
Measurement & Analytics: Performance tracking and evolution analysis.

This module calculates the cumulative evolution of portfolio returns, benchmark returns,
and excess returns over a selected performance period.

The output DataFrame has columns: Date (date object), Return, BM return, Excess return
(all in percent, starting at 0% on the first aggregation point).
"""

import pandas as pd


def measurement_analytics_master(merged_df: pd.DataFrame, classification_criteria=None, frequency: str = "daily") -> pd.DataFrame:
    """
    Master-level measurement & analytics calculation (ignores classification_criteria for compatibility).

    Args:
        merged_df: Merged DataFrame from prepare_data
        classification_criteria: Ignored; kept for registry compatibility
        frequency: Frequency for aggregation. One of "daily", "weekly", "monthly".

    Returns:
        DataFrame with columns: Date (date object), Return, BM return, Excess return
    """
    return calculate_measurement_analytics(merged_df, frequency=frequency)


def measurement_analytics_instrument(merged_df: pd.DataFrame, classification_criteria=None, classification_value=None, frequency: str = "daily"):
    """
    Placeholder for portfolio-level analytics table.

    Currently returns zeros for Volatility and Benchmark volatility.
    To be implemented with proper volatility calculations.

    Args:
        merged_df: Prepared merged DataFrame from prepare_data
        classification_criteria: Ignored (kept for compatibility)
        classification_value: Ignored (we aggregate across selected portfolios)
        frequency: One of "daily", "weekly", "monthly" (ignored for now)

    Returns:
        DataFrame with columns ["Metric", "Value"] containing placeholder zeros.
    """
    return pd.DataFrame([
        {"Metric": "Volatility", "Value": 0.0},
        {"Metric": "Benchmark volatility", "Value": 0.0}
    ])


def calculate_measurement_analytics(merged_df: pd.DataFrame, frequency: str = "daily") -> pd.DataFrame:
    """
    Calculate cumulative return evolution over time for portfolio, benchmark, and excess return.

    Leverages pre-computed TotalReturn_* from prepare_data to avoid duplicating aggregation logic.
    Simply compounds daily returns to the requested frequency and calculates cumulative returns.

    Args:
        merged_df: Merged DataFrame from prepare_data (includes TotalReturn_portfolio and TotalReturn_benchmark)
        frequency: Frequency for aggregation. One of "daily", "weekly", "monthly".
                   - "daily": use daily returns as-is
                   - "weekly": compound daily returns to weekly
                   - "monthly": compound daily returns to monthly

    Returns:
        DataFrame with columns: Date (date object), Return, BM return, Excess return
        All returns are cumulative percentages (float), starting at 0% on the first point.
    """
    if merged_df is None or merged_df.empty:
        return pd.DataFrame(columns=["Date", "Return", "BM return", "Excess return"])

    # Extract unique daily returns (TotalReturn_* are already aggregated at portfolio level per day in prepare_data)
    df = merged_df[["Start Date", "TotalReturn_portfolio", "TotalReturn_benchmark"]].drop_duplicates(subset=["Start Date"]).sort_values("Start Date").reset_index(drop=True)
    
    if df.empty:
        return pd.DataFrame(columns=["Date", "Return", "BM return", "Excess return"])

    df["Start Date"] = pd.to_datetime(df["Start Date"])
    
    # Compound daily returns to requested frequency
    if frequency == "daily":
        # Use daily returns as-is
        daily_returns = df.copy()
    elif frequency in ("weekly", "monthly"):
        # Set index for resampling
        df.index = df["Start Date"]
        
        # Compound returns: (1 + r1) * (1 + r2) * ... - 1
        resample_rule = "W" if frequency == "weekly" else "M"
        daily_returns = df.groupby(pd.Grouper(freq=resample_rule)).agg({
            "TotalReturn_portfolio": lambda x: (1 + x).prod() - 1,
            "TotalReturn_benchmark": lambda x: (1 + x).prod() - 1
        }).reset_index()
        daily_returns = daily_returns[daily_returns["TotalReturn_portfolio"].notna() | daily_returns["TotalReturn_benchmark"].notna()].reset_index(drop=True)
    else:
        daily_returns = df.copy()
    
    # Compute cumulative returns (product of growth factors: (1+r1)*(1+r2)*...)
    # This gives cumulative growth from the start of the period
    daily_returns["Fund_Factor"] = (1 + daily_returns["TotalReturn_portfolio"]).cumprod()
    daily_returns["BM_Factor"] = (1 + daily_returns["TotalReturn_benchmark"]).cumprod()
    
    # Convert to cumulative percent return (with first point = 0%, second point = return from day 1, etc.)
    # Cumulative return = (Factor - 1) * 100, so baseline (Factor=1) = 0%
    daily_returns["Return"] = (daily_returns["Fund_Factor"] - 1) * 100
    daily_returns["BM return"] = (daily_returns["BM_Factor"] - 1) * 100
    daily_returns["Excess return"] = daily_returns["Return"] - daily_returns["BM return"]
    
    # Convert dates to date objects
    daily_returns["Date"] = pd.to_datetime(daily_returns["Start Date"]).dt.date
    result = daily_returns[["Date", "Return", "BM return", "Excess return"]].copy()
    
    # Insert a baseline 0% row at the start of the period (one day before first date)
    # so the chart shows: [0% at baseline_date] -> [actual cumulative return at first_date]
    if not result.empty:
        first_date = result.loc[0, "Date"]
        # first_date is already a datetime.date object, convert to datetime for timedelta arithmetic
        baseline_date = pd.to_datetime(first_date) - pd.Timedelta(days=1)
        baseline_row = pd.DataFrame([{
            "Date": baseline_date.date(),
            "Return": 0.0,
            "BM return": 0.0,
            "Excess return": 0.0
        }])
        result = pd.concat([baseline_row, result], ignore_index=True)
    
    return result
