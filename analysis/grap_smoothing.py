import pandas as pd
import numpy as np


def grap_smoothing(df, start_date, breakdowns_list):
    start_date = pd.to_datetime(start_date)
    df["Start Date"] = pd.to_datetime(df["Start Date"])
    df = df[df["Start Date"] >= start_date]

    returns_df = df.groupby("Start Date")[["TotalReturn_portfolio", "TotalReturn_benchmark"]].first().reset_index()

    returns_df["GRAP factor"] = np.nan
    for i in range(len(returns_df)):
        portfolio_product = (1 + returns_df.loc[:i - 1, "TotalReturn_portfolio"]).prod() if i > 0 else 1
        benchmark_product = (1 + returns_df.loc[i + 1:, "TotalReturn_benchmark"]).prod()
        returns_df.loc[i, "GRAP factor"] = portfolio_product * benchmark_product

    returns_df = returns_df.drop(["TotalReturn_portfolio", "TotalReturn_benchmark"], axis=1)
    df = df.drop(["TotalReturn_portfolio", "TotalReturn_benchmark"], axis=1)

    df = pd.merge(df, returns_df[["Start Date", "GRAP factor"]], on="Start Date", how="left")

    # GRAP factor application
    # Define the columns to exclude from the GRAP factor multiplication
    excluded_cols = ["Start Date", "GRAP factor"] + breakdowns_list

    # Identify all the columns to multiply by the GRAP factor
    cols_to_multiply = [col for col in df.columns if col not in excluded_cols]

    # Multiply those columns by the "GRAP Factor" column row-by-row
    df[cols_to_multiply] = df[cols_to_multiply].mul(df["GRAP factor"], axis=0)

    grap_result_df = df.groupby(breakdowns_list)[cols_to_multiply].sum().reset_index()

    # Create the "Total" row
    total_row = {col: "Total" for col in breakdowns_list}  # Set string columns to "Total"
    for col in cols_to_multiply:
        total_row[col] = df[col].sum()  # Compute the sum for numeric columns

    # Append the row to the DataFrame
    grap_result_df = pd.concat([pd.DataFrame([total_row]), grap_result_df], ignore_index=True)

    return grap_result_df
