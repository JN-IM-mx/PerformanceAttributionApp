import pandas as pd

def apply_smoothing(row, breakdowns_list, col, bkd_col_sum_to_prev_date):
    breakdown = row[breakdowns_list[0]]
    
    # Check if the breakdown value has previously appeared in the dataframe - the final output takes the current row value if it hasn't appeared
    if breakdown not in bkd_col_sum_to_prev_date:
        mf_final_output = row[col]
        bkd_col_sum_to_prev_date[breakdown] = row[col]
    else:
        # Apply the standard Modified Frongello function and update the cumulative sum of the breakdown value for the final term  - \sum_{\theta=t}^{T-1} (E_{i,j,\theta})
        mf_final_output = 0.5 * row[col] * row["Prev_TotalReturn_adjustment_factor"] + 0.5 * (row["TotalReturn_portfolio"] + row["TotalReturn_benchmark"]) * bkd_col_sum_to_prev_date[breakdown]
        bkd_col_sum_to_prev_date[breakdown] += mf_final_output

    return mf_final_output

def modified_frongello_smoothing(df, start_date, breakdowns_list):
    start_date = pd.to_datetime(start_date)
    df["Start Date"] = pd.to_datetime(df["Start Date"])
    df = df[df["Start Date"] >= start_date]

    returns_df = df.groupby("Start Date")[["TotalReturn_portfolio", "TotalReturn_benchmark"]].first().reset_index()

    # Calculated columns for calculation - preparation of the addition of respective cumulative product of the portfolio and benchmark to the previous date
    
    returns_df["TotalReturn_portfolio_factor"] = returns_df["TotalReturn_portfolio"] + 1
    returns_df["TotalReturn_benchmark_factor"] = returns_df["TotalReturn_benchmark"] + 1
    returns_df["TotalReturn_portfolio_cumprod"] = returns_df["TotalReturn_portfolio_factor"].cumprod()
    returns_df["TotalReturn_benchmark_cumprod"] = returns_df["TotalReturn_benchmark_factor"].cumprod()
    returns_df["TotalReturn_adjustment_factor"] = returns_df["TotalReturn_portfolio_cumprod"] + returns_df["TotalReturn_benchmark_cumprod"]

    # Shift the total return adjustment factor so that we can access the value in the same row for the apply_smoothing method - Latex representation below
    # \left(\prod_{\theta=1}^{T-1} (1 + \text{RP}{\theta}) + \prod_{\theta=1}^{T-1} (1 + \text{RB}{\theta}) \right)
    returns_df["Prev_TotalReturn_adjustment_factor"] = returns_df["TotalReturn_adjustment_factor"].shift(1)

    returns_df = returns_df.drop(["TotalReturn_portfolio_factor", "TotalReturn_benchmark_factor", "TotalReturn_portfolio_cumprod", "TotalReturn_benchmark_cumprod", "TotalReturn_adjustment_factor"], axis=1)

    # All data required is accessible through the merged df
    df = pd.merge(df, returns_df[["Start Date", "Prev_TotalReturn_adjustment_factor"]], on="Start Date", how="left")

    # Modified Frongello application
    # Define the columns to exclude from the Modified Frongello
    excluded_cols = ["Start Date", "TotalReturn_portfolio", "TotalReturn_benchmark", "Prev_TotalReturn_adjustment_factor"] + breakdowns_list

    # Identify all the columns to apply the Modified Frongello to
    cols_to_apply_smoothing = [col for col in df.columns if col not in excluded_cols]

    # Loop over columns to apply smoothing with an apply method. Create dictionary to keep track of the sum of the previous values to the current row.
    for col in cols_to_apply_smoothing:
        bkd_col_sum_to_prev_date = {}
        df[col + '_MF'] = df.apply(apply_smoothing, axis=1,  args=(breakdowns_list, col, bkd_col_sum_to_prev_date))
        df[col] = df[col + '_MF']
        df = df.drop([col + '_MF'], axis=1)

    modified_frongello_result_df = df.groupby(breakdowns_list)[cols_to_apply_smoothing].sum().reset_index()
    # Create the "Total" row
    total_row = {col: "Total" for col in breakdowns_list}  # Set string columns to "Total"
    for col in cols_to_apply_smoothing:
        total_row[col] = df[col].sum()  # Compute the sum for numeric columns

    # Append the row to the DataFrame
    modified_frongello_result_df = pd.concat([pd.DataFrame([total_row]), modified_frongello_result_df], ignore_index=True)

    return modified_frongello_result_df
