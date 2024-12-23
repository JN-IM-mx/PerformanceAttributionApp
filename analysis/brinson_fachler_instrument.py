def selection_by_instrument(delta_mv_ptf,
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


def brinson_fachler_instrument(data_df, classification_criteria, classification_value):
    selection_columns = ["Start Date",
                         classification_criteria,
                         "Product description",
                         "PreviousMv_portfolio",
                         "DeltaMv_portfolio",
                         "PreviousMv_benchmark",
                         "DeltaMv_benchmark"
                         ]

    selection_df = data_df[selection_columns]

    # Compute the total previous
    selection_df = selection_df.copy()
    selection_df["TotalPreviousMv_portfolio"] = selection_df.groupby("Start Date")["PreviousMv_portfolio"].transform("sum")

    # Filter on the value of the classification
    selection_df = selection_df[selection_df[classification_criteria] == classification_value]


    # Compute delta and previous MVs per date for the benchmark
    selection_df["ClassifPreviousMv_benchmark"] = selection_df.groupby("Start Date")["PreviousMv_benchmark"].transform("sum")
    selection_df["ClassifDeltaMv_benchmark"] = selection_df.groupby("Start Date")["DeltaMv_benchmark"].transform("sum")

    # # Calculate weights per date
    # attribution_df["Weight_portfolio"] = attribution_df["PreviousMv_portfolio"] / attribution_df["TotalPreviousMv_portfolio"]
    # attribution_df["Weight_benchmark"] = attribution_df["PreviousMv_benchmark"] / attribution_df["TotalPreviousMv_benchmark"]

    selection_df["Selection Effect"] = selection_df.apply(
        lambda row: selection_by_instrument(
            row["DeltaMv_portfolio"],
            row["PreviousMv_portfolio"],
            row["TotalPreviousMv_portfolio"],
            row["ClassifDeltaMv_benchmark"],
            row["ClassifPreviousMv_benchmark"]
        ),
        axis=1)

    selection_columns = ["Start Date", "Product description", "Selection Effect"]
    selection_df = selection_df[selection_columns]

    return selection_df
