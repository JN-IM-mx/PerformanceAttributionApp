import pandas as pd

def prepare_data(ptf_list, bm, ptf_df, bm_df, classifications_df):
    # Filter ptf_df on portfolios in ptf_list and remove unneeded columns
    ptf_df = ptf_df[ptf_df["Portfolio"].isin(ptf_list)]
    ptf_df = ptf_df.drop(["Portfolio", "ProductTaxonomy", "End Date"], axis=1)
    ptf_df = ptf_df.groupby(["Start Date", "Instrument"]).sum().reset_index()

    # Filter bm_df on portfolios in bm_list and remove unneeded columns
    bm_df = bm_df[bm_df["Benchmark"] == bm]
    bm_df = bm_df.drop(["Benchmark", "ProductTaxonomy", "End Date"], axis=1)

    merged_df = pd.merge(ptf_df, bm_df, how="outer", on=["Instrument", "Start Date"], suffixes=("_portfolio", "_benchmark")).fillna(0)

    # Compute total MVs and total returns per date
    total_mv_returns_columns = ["Start Date", "DeltaMv_portfolio", "DeltaMv_benchmark", "PreviousMv_portfolio", "PreviousMv_benchmark"]
    total_mv_returns_df = merged_df[total_mv_returns_columns]

    merged_df["TotalPreviousMv_portfolio"] = total_mv_returns_df.groupby("Start Date")["PreviousMv_portfolio"].transform("sum")
    merged_df["TotalPreviousMv_benchmark"] = total_mv_returns_df.groupby("Start Date")["PreviousMv_benchmark"].transform("sum")
    merged_df["TotalDeltaMv_portfolio"] = total_mv_returns_df.groupby("Start Date")["DeltaMv_portfolio"].transform("sum")
    merged_df["TotalDeltaMv_benchmark"] = total_mv_returns_df.groupby("Start Date")["DeltaMv_benchmark"].transform("sum")
    merged_df["TotalReturn_portfolio"] = merged_df["TotalDeltaMv_portfolio"] / merged_df["TotalPreviousMv_portfolio"]
    merged_df["TotalReturn_benchmark"] = merged_df["TotalDeltaMv_benchmark"] / merged_df["TotalPreviousMv_benchmark"]

    merged_df = pd.merge(merged_df, classifications_df, left_on="Instrument", right_on="Product", how="left").fillna(
        "Cash")

    return merged_df

