def compute_allocation(delta_mv_ptf,
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


def compute_selection(delta_mv_ptf,
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


def compute_selection_by_instrument(delta_mv_ptf,
                            previous_mv_ptf,
                            total_previous_mv_ptf,
                            delta_mv_classif_benchmark,
                            previous_mv_classif_benchmark
                            ):
    if previous_mv_ptf != 0 and previous_mv_classif_benchmark != 0:
        weight_ptf = previous_mv_ptf / total_previous_mv_ptf
        return_ptf = delta_mv_ptf / previous_mv_ptf
        return_classif_bm = delta_mv_classif_benchmark / previous_mv_classif_benchmark
        selection = weight_ptf * (return_ptf - return_classif_bm)
    else:
        selection = 0

    return selection


def brinson_fachler(data_df, classification_criteria):
    # Sum all values across the instruments
    attribution_df = data_df.groupby(["Start Date", classification_criteria]).agg({
        "DeltaMv_portfolio": "sum",
        "PreviousMv_portfolio": "sum",
        "DeltaMv_benchmark": "sum",
        "PreviousMv_benchmark": "sum",
        "TotalPreviousMv_portfolio": "first",
        "TotalReturn_portfolio": "first",
        "TotalPreviousMv_benchmark": "first",
        "TotalReturn_benchmark": "first"
    }).reset_index()

    # Compute allocation effect for each date
    attribution_df["Allocation"] = attribution_df.apply(
        lambda row: compute_allocation(
            row["DeltaMv_portfolio"],
            row["PreviousMv_portfolio"],
            row["TotalPreviousMv_portfolio"],
            row["DeltaMv_benchmark"],
            row["PreviousMv_benchmark"],
            row["TotalPreviousMv_benchmark"],
            row["TotalReturn_benchmark"],
        ),
        axis = 1)

    attribution_df["Selection"] = attribution_df.apply(
        lambda row: compute_selection(
            row["DeltaMv_portfolio"],
            row["PreviousMv_portfolio"],
            row["TotalPreviousMv_portfolio"],
            row["DeltaMv_benchmark"],
            row["PreviousMv_benchmark"]
        ),
        axis=1)

    attribution_df["Excess return"] = attribution_df["Allocation"] + attribution_df["Selection"]

    attribution_df = attribution_df.reset_index()
    attribution_columns = ["Start Date",
                           classification_criteria,
                           "Excess return",
                           "Allocation",
                           "Selection",
                           "TotalReturn_portfolio",
                           "TotalReturn_benchmark"
                           ]
    attribution_df = attribution_df[attribution_columns]

    return attribution_df


def brinson_fachler_instrument(data_df, classification_criteria, classification_value):
    # Filter on the value of the classification
    data_df = data_df[data_df[classification_criteria] == classification_value]

    instruments_columns = ["Start Date",
                           classification_criteria,
                           "Product description",
                           "PreviousMv_portfolio",
                           "DeltaMv_portfolio",
                           "TotalPreviousMv_portfolio",
                           "PreviousMv_benchmark",
                           "DeltaMv_benchmark",
                           "TotalReturn_portfolio",
                           "TotalReturn_benchmark"
                         ]

    instruments_df = data_df[instruments_columns].copy()

    # Compute delta and previous MVs per date for the benchmark
    instruments_df["ClassifPreviousMv_benchmark"] = instruments_df.groupby("Start Date")["PreviousMv_benchmark"].transform("sum")
    instruments_df["ClassifDeltaMv_benchmark"] = instruments_df.groupby("Start Date")["DeltaMv_benchmark"].transform("sum")

    instruments_df["Selection"] = instruments_df.apply(
        lambda row: compute_selection_by_instrument(
            row["DeltaMv_portfolio"],
            row["PreviousMv_portfolio"],
            row["TotalPreviousMv_portfolio"],
            row["ClassifDeltaMv_benchmark"],
            row["ClassifPreviousMv_benchmark"]
        ),
        axis=1)

    selection_columns = ["Start Date",
                         "Product description",
                         "Selection",
                         "TotalReturn_portfolio",
                         "TotalReturn_benchmark"]

    instruments_df = instruments_df[selection_columns]

    return instruments_df