def allocation_computation(delta_mv_ptf,
                           previous_mv_ptf,
                           total_previous_mv_ptf,
                           delta_mv_bm,
                           previous_mv_bm,
                           total_previous_mv_bm,
                           total_return_bm
                           ):

    weight_ptf = previous_mv_ptf / total_previous_mv_ptf

    if previous_mv_bm != 0:
        # Standard Brinson-Fachler formula
        weight_bm = previous_mv_bm / total_previous_mv_bm
        return_bm = delta_mv_bm / previous_mv_bm
        allocation_effect = (weight_ptf - weight_bm) * (return_bm - total_return_bm)
    else:
        # Exception case: contribution_i - w_i * B
        allocation_effect = delta_mv_ptf / total_previous_mv_ptf - weight_ptf * total_return_bm
    return allocation_effect


def selection_computation(delta_mv_ptf,
                          previous_mv_ptf,
                          total_previous_mv_ptf,
                          delta_mv_bm,
                          previous_mv_bm,
                          ):
    weight_ptf = previous_mv_ptf / total_previous_mv_ptf
    if previous_mv_ptf != 0 and previous_mv_bm != 0:
        # Standard Brinson-Fachler formula
        return_ptf = delta_mv_ptf / previous_mv_ptf
        return_bm = delta_mv_bm / previous_mv_bm
        selection_effect = weight_ptf * (return_ptf - return_bm)
    else:
        # Exception case: selection is zero
        selection_effect = 0
    return selection_effect


def brinson_fachler(data_df, classification_criteria):
    attribution_columns = ["Start Date",
                           classification_criteria,
                           "PreviousMv_portfolio",
                           "DeltaMv_portfolio",
                           "PreviousMv_benchmark",
                           "DeltaMv_benchmark"
                           ]

    # Sum all values across the instruments
    attribution_df = data_df[attribution_columns].groupby(["Start Date", classification_criteria]).sum()

    # Compute total MVs and benchmark total return per date
    attribution_df["TotalPreviousMv_portfolio"] = attribution_df.groupby("Start Date")["PreviousMv_portfolio"].transform("sum")
    attribution_df["TotalPreviousMv_benchmark"] = attribution_df.groupby("Start Date")["PreviousMv_benchmark"].transform("sum")
    attribution_df["TotalDeltaMv_benchmark"] = attribution_df.groupby("Start Date")["DeltaMv_benchmark"].transform("sum")
    attribution_df["TotalReturn_benchmark"] = attribution_df["TotalDeltaMv_benchmark"] / attribution_df["TotalPreviousMv_benchmark"]

    # # Calculate weights per date
    # attribution_df["Weight_portfolio"] = attribution_df["PreviousMv_portfolio"] / attribution_df["TotalPreviousMv_portfolio"]
    # attribution_df["Weight_benchmark"] = attribution_df["PreviousMv_benchmark"] / attribution_df["TotalPreviousMv_benchmark"]

    # Compute allocation effect for each date
    attribution_df["Allocation Effect"] = attribution_df.apply(
        lambda row: allocation_computation(
            row["DeltaMv_portfolio"],
            row["PreviousMv_portfolio"],
            row["TotalPreviousMv_portfolio"],
            row["DeltaMv_benchmark"],
            row["PreviousMv_benchmark"],
            row["TotalPreviousMv_benchmark"],
            row["TotalReturn_benchmark"],
        ),
        axis = 1)

    attribution_df["Selection Effect"] = attribution_df.apply(
        lambda row: selection_computation(
            row["DeltaMv_portfolio"],
            row["PreviousMv_portfolio"],
            row["TotalPreviousMv_portfolio"],
            row["DeltaMv_benchmark"],
            row["PreviousMv_benchmark"]
        ),
        axis=1)

    attribution_df = attribution_df.reset_index()
    attribution_columns = ["Start Date",
                           classification_criteria,
                           "Allocation Effect",
                           "Selection Effect"
                           ]
    attribution_df = attribution_df[attribution_columns]

    return attribution_df


    # Calculate weights and returns
    # attribution_df['Weight_portfolio'] = \
    #     attribution_df['PreviousMv_portfolio'] / attribution_df.groupby('Start Date')['PreviousMv_portfolio'].transform('sum')
    #
    #
    # attribution_df['Weight_benchmark'] = \
    #     attribution_df['PreviousMv_benchmark'] / attribution_df.groupby('Start Date')['PreviousMv_benchmark'].transform('sum')
    #
    # attribution_df['Return_portfolio'] = attribution_df.apply(
    #     lambda row: row['DeltaMv_portfolio'] / row['PreviousMv_portfolio']
    #     if row['Weight_portfolio'] != 0
    #     else row['DeltaMv_benchmark'] / row['PreviousMv_benchmark'], axis=1
    # )
    #
    # attribution_df['Return_benchmark'] = attribution_df.apply(
    #     lambda row: row['DeltaMv_benchmark'] / row['PreviousMv_benchmark']
    #     if row['Weight_benchmark'] != 0
    #     else row['DeltaMv_portfolio'] / row['PreviousMv_portfolio'], axis=1)

    # attribution_df['Allocation Effect'] = \
    #     (attribution_df['Weight_portfolio'] - attribution_df['Weight_benchmark']) \
    #     * (attribution_df['Return_benchmark'] - attribution_df['Total_Return_benchmark'])

    # attribution_df['Selection Effect'] = attribution_df['Weight_portfolio'] * (attribution_df['Return_portfolio'] - attribution_df['Return_benchmark'])