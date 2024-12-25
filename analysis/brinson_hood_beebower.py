def compute_allocation(delta_mv_ptf,
                           previous_mv_ptf,
                           total_previous_mv_ptf,
                           delta_mv_bm,
                           previous_mv_bm,
                           total_previous_mv_bm,
                           ):

    weight_ptf = previous_mv_ptf / total_previous_mv_ptf

    if previous_mv_bm != 0:
        # Standard Brinson-Hood-Beebower formula
        weight_bm = previous_mv_bm / total_previous_mv_bm
        return_bm = delta_mv_bm / previous_mv_bm
        allocation_effect = (weight_ptf - weight_bm) * return_bm
    else:
        # Exception case: contribution_i
        allocation_effect = delta_mv_ptf / total_previous_mv_ptf
    return allocation_effect


def compute_selection(delta_mv_ptf,
                      previous_mv_ptf,
                      delta_mv_bm,
                      previous_mv_bm,
                      total_previous_mv_bm
                      ):
    if previous_mv_ptf != 0 and previous_mv_bm != 0:
        # Standard Brinson-Hood-Beebower formula
        weight_bm = previous_mv_bm / total_previous_mv_bm
        return_ptf = delta_mv_ptf / previous_mv_ptf
        return_bm = delta_mv_bm / previous_mv_bm
        selection_effect = weight_bm * (return_ptf - return_bm)
    else:
        # Exception case: selection is zero
        selection_effect = 0
    return selection_effect


def compute_interaction(delta_mv_ptf,
                            previous_mv_ptf,
                            total_previous_mv_ptf,
                            delta_mv_bm,
                            previous_mv_bm,
                            total_previous_mv_bm
                            ):
    if previous_mv_ptf != 0 and previous_mv_bm != 0:
        # Standard Brinson-Hood-Beebower formula
        weight_ptf = previous_mv_ptf / total_previous_mv_ptf
        weight_bm = previous_mv_bm / total_previous_mv_bm
        return_ptf = delta_mv_ptf / previous_mv_ptf
        return_bm = delta_mv_bm / previous_mv_bm
        interaction_effect = (weight_ptf - weight_bm) * (return_ptf - return_bm)
    else:
        # Exception case: interaction is zero
        interaction_effect = 0
    return interaction_effect


def compute_selection_by_instrument(delta_mv_classif_ptf,
                            previous_mv_classif_ptf,
                            delta_mv_bm,
                            previous_mv_bm,
                            total_previous_mv_bm
                            ):
    if previous_mv_bm != 0 and previous_mv_classif_ptf != 0:
        weight_bm = previous_mv_bm / total_previous_mv_bm
        return_classif_ptf = delta_mv_classif_ptf / previous_mv_classif_ptf
        return_bm = delta_mv_bm / previous_mv_bm
        selection = weight_bm * (return_classif_ptf - return_bm)
    else:
        selection = 0

    return selection

def compute_interaction_by_instrument(previous_mv_ptf,
                              total_previous_mv_ptf,
                              delta_mv_classif_ptf,
                              previous_mv_classif_ptf,
                              previous_mv_bm,
                              total_previous_mv_bm,
                              delta_mv_classif_bm,
                              previous_mv_classif_bm
                            ):
    if previous_mv_classif_ptf != 0 and previous_mv_classif_bm != 0:
        weight_ptf = previous_mv_ptf / total_previous_mv_ptf
        weight_bm = previous_mv_bm / total_previous_mv_bm
        return_classif_ptf = delta_mv_classif_ptf / previous_mv_classif_ptf
        return_classif_bm = delta_mv_classif_bm / previous_mv_classif_bm
        interaction = (weight_ptf - weight_bm) * (return_classif_ptf - return_classif_bm)
    else:
        interaction = 0

    return interaction


def brinson_hood_beebower(data_df, classification_criteria):
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
    attribution_df["Allocation Effect"] = attribution_df.apply(
        lambda row: compute_allocation(
            row["DeltaMv_portfolio"],
            row["PreviousMv_portfolio"],
            row["TotalPreviousMv_portfolio"],
            row["DeltaMv_benchmark"],
            row["PreviousMv_benchmark"],
            row["TotalPreviousMv_benchmark"],
        ),
        axis = 1)

    attribution_df["Selection Effect"] = attribution_df.apply(
        lambda row: compute_selection(
            row["DeltaMv_portfolio"],
            row["PreviousMv_portfolio"],
            row["DeltaMv_benchmark"],
            row["PreviousMv_benchmark"],
            row["TotalPreviousMv_benchmark"],
        ),
        axis=1)

    attribution_df["Interaction Effect"] = attribution_df.apply(
        lambda row: compute_selection(
            row["DeltaMv_portfolio"],
            row["PreviousMv_portfolio"],
            row["DeltaMv_benchmark"],
            row["PreviousMv_benchmark"],
            row["TotalPreviousMv_benchmark"],
        ),
        axis=1)

    attribution_df = attribution_df.reset_index()
    attribution_columns = ["Start Date",
                           classification_criteria,
                           "Allocation Effect",
                           "Selection Effect",
                           "Interaction Effect",
                           "TotalReturn_portfolio",
                           "TotalReturn_benchmark"
                           ]
    attribution_df = attribution_df[attribution_columns]

    return attribution_df


def brinson_hood_beebower_instrument(data_df, classification_criteria, classification_value):
    data_df = data_df[data_df[classification_criteria] == classification_value]

    instruments_columns = ["Start Date",
                         classification_criteria,
                         "Product description",
                         "PreviousMv_portfolio",
                         "DeltaMv_portfolio",
                         "TotalPreviousMv_portfolio",
                         "PreviousMv_benchmark",
                         "DeltaMv_benchmark",
                         "TotalPreviousMv_benchmark",
                         "TotalReturn_portfolio",
                         "TotalReturn_benchmark"
                         ]

    instruments_df = data_df[instruments_columns].copy()

    # Compute delta and previous MVs per date at classification level
    instruments_df["ClassifPreviousMv_portfolio"] = instruments_df.groupby("Start Date")["PreviousMv_portfolio"].transform("sum")
    instruments_df["ClassifDeltaMv_portfolio"] = instruments_df.groupby("Start Date")["DeltaMv_portfolio"].transform("sum")
    instruments_df["ClassifPreviousMv_benchmark"] = instruments_df.groupby("Start Date")["PreviousMv_benchmark"].transform("sum")
    instruments_df["ClassifDeltaMv_benchmark"] = instruments_df.groupby("Start Date")["DeltaMv_benchmark"].transform("sum")


    instruments_df["Selection Effect"] = instruments_df.apply(
        lambda row: compute_selection_by_instrument(
            row["ClassifDeltaMv_portfolio"],
            row["ClassifPreviousMv_portfolio"],
            row["DeltaMv_benchmark"],
            row["PreviousMv_benchmark"],
            row["TotalPreviousMv_benchmark"]
        ),
        axis=1)

    instruments_df["Interaction Effect"] = instruments_df.apply(
        lambda row: compute_interaction_by_instrument(
            row["PreviousMv_portfolio"],
            row["TotalPreviousMv_portfolio"],
            row["ClassifDeltaMv_portfolio"],
            row["ClassifPreviousMv_portfolio"],
            row["PreviousMv_benchmark"],
            row["TotalPreviousMv_benchmark"],
            row["ClassifDeltaMv_benchmark"],
            row["ClassifPreviousMv_benchmark"]
        ),
        axis=1)

    instruments_columns = ["Start Date",
                           "Product description",
                           "Selection Effect",
                           "Interaction Effect",
                           "TotalReturn_portfolio",
                           "TotalReturn_benchmark"]
    instruments_df = instruments_df[instruments_columns]

    return instruments_df