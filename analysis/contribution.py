def compute_return( delta_mv,
                    total_return
                    ):
    contribution_return = delta_mv / total_return

    return contribution_return

def contribution(data_df, classification_criteria):

    # Sum all values across the instruments
    contribution_df = data_df.groupby(["Start Date", classification_criteria]).agg({
        "DeltaMv_portfolio": "sum",
        "DeltaMv_benchmark": "sum",
        "TotalPreviousMv_portfolio": "first",
        "TotalReturn_portfolio": "first",
        "TotalPreviousMv_benchmark": "first",
        "TotalReturn_benchmark": "first"
    }).reset_index()

    # Compute contribution of Return for each date
    contribution_df["Return"] = contribution_df.apply(
        lambda row: compute_return(
            row["DeltaMv_portfolio"],
            row["TotalPreviousMv_portfolio"]
        ),
        axis = 1)

    # Compute contribution of BM Return for each date
    contribution_df["BM Return"] = contribution_df.apply(
        lambda row: compute_return(
            row["DeltaMv_benchmark"],
            row["TotalPreviousMv_benchmark"]
        ),
        axis=1)

    contribution_df = contribution_df.reset_index()

    contribution_columns = ["Start Date",
                           classification_criteria,
                           "Return",
                           "BM Return",
                           "TotalReturn_portfolio",
                           "TotalReturn_benchmark"
                           ]
    contribution_df = contribution_df[contribution_columns]

    return contribution_df

def contribution_instrument(data_df, classification_criteria, classification_value):
    # Filter on the value of the classification
    data_df = data_df[data_df[classification_criteria] == classification_value]

    # Sum all values across the instruments
    instruments_df = data_df.groupby(["Start Date", "Product description"]).agg({
        "DeltaMv_portfolio": "sum",
        "DeltaMv_benchmark": "sum",
        "TotalPreviousMv_portfolio": "first",
        "TotalReturn_portfolio": "first",
        "TotalPreviousMv_benchmark": "first",
        "TotalReturn_benchmark": "first"
    }).reset_index()

    # Compute contribution of Return for each date
    instruments_df["Return"] = instruments_df.apply(
        lambda row: compute_return(
            row["DeltaMv_portfolio"],
            row["TotalPreviousMv_portfolio"]
        ),
        axis = 1)

    # Compute contribution of BM Return for each date
    instruments_df["BM Return"] = instruments_df.apply(
        lambda row: compute_return(
            row["DeltaMv_benchmark"],
            row["TotalPreviousMv_benchmark"]
        ),
        axis=1)

    instruments_df = instruments_df.reset_index()

    instrument_contribution_columns = ["Start Date",
                            "Product description",
                            "Return",
                            "BM Return",
                            "TotalReturn_portfolio",
                            "TotalReturn_benchmark"
                            ]
    instruments_df = instruments_df[instrument_contribution_columns]

    return instruments_df
