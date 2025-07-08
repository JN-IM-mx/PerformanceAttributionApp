from .brinson_fachler import brinson_fachler

def excess_return(row, effect):
    delta_mv_ptf = "DeltaMv" + effect + "_portfolio"
    delta_mv_bm = "DeltaMv" + effect + "_benchmark"
    contrib_ptf = row[delta_mv_ptf] / row["TotalPreviousMv_portfolio"]
    contrib_bm = row[delta_mv_bm] / row["TotalPreviousMv_benchmark"]

    return contrib_ptf - contrib_bm


def effects_analysis(data_df, classification_criteria, effects, credit_mode):
    # Sum all values across the instruments
    attribution_df = data_df.groupby(["Start Date", classification_criteria]).agg({
                           "DeltaMv_portfolio": "sum",
                           "DeltaMvPrice_portfolio": "sum",
                           "DeltaMvTrading_portfolio": "sum",
                           "DeltaMvCurrency_portfolio": "sum",
                           "DeltaMvGlobalOther_portfolio": "sum",
                           "DeltaMvRolldown_portfolio": "sum",
                           "DeltaMvIncome_portfolio": "sum",
                           "DeltaMvYieldCurves_portfolio": "sum",
                           "DeltaMvCredit_portfolio": "sum",
                           "DeltaMv_benchmark": "sum",
                           "DeltaMvPrice_benchmark": "sum",
                           "DeltaMvTrading_benchmark": "sum",
                           "DeltaMvCurrency_benchmark": "sum",
                           "DeltaMvGlobalOther_benchmark": "sum",
                           "DeltaMvRolldown_benchmark": "sum",
                           "DeltaMvIncome_benchmark": "sum",
                           "DeltaMvYieldCurves_benchmark": "sum",
                           "DeltaMvCredit_benchmark": "sum",
                           "PreviousMv_portfolio": "sum",
                           "PreviousMv_benchmark": "sum",
                           "TotalPreviousMv_portfolio": "first",
                           "TotalPreviousMv_benchmark": "first",
                           "TotalReturn_portfolio": "first",
                           "TotalReturn_benchmark": "first"
    }).reset_index()

    attribution_df["Price"] = attribution_df.apply(excess_return, axis=1, args=("Price",))
    attribution_df["Trading"] = attribution_df.apply(excess_return, axis=1, args=("Trading",))
    attribution_df["Currency"] = attribution_df.apply(excess_return, axis=1, args=("Currency",))
    attribution_df["Global other"] = attribution_df.apply(excess_return, axis=1, args=("GlobalOther",))
    attribution_df["Rolldown"] = attribution_df.apply(excess_return, axis=1, args=("Rolldown",))
    attribution_df["Income"] = attribution_df.apply(excess_return, axis=1, args=("Income",))
    attribution_df["Yield curve"] = attribution_df.apply(excess_return, axis=1, args=("YieldCurves",))

    if credit_mode == "brinson":
        # Prepare credit-specific DataFrame for brinson_fachler
        credit_df = attribution_df[["Start Date", classification_criteria,
                                    "DeltaMvCredit_portfolio", "PreviousMv_portfolio", "DeltaMvCredit_benchmark",
                                    "PreviousMv_benchmark", "TotalPreviousMv_portfolio", "TotalReturn_portfolio",
                                    "TotalPreviousMv_benchmark", "TotalReturn_benchmark"]].copy()
        credit_df = credit_df.rename(columns={
            "DeltaMvCredit_portfolio": "DeltaMv_portfolio",
            "DeltaMvCredit_benchmark": "DeltaMv_benchmark"
        })
        credit_brinson = brinson_fachler(credit_df, classification_criteria)
        # Merge allocation/selection back
        attribution_df = attribution_df.merge(
            credit_brinson[["Start Date", classification_criteria, "Allocation", "Selection"]],
            on=["Start Date", classification_criteria],
            how="left"
        )
        attribution_df = attribution_df.rename(columns={
            "Allocation": "Credit allocation",
            "Selection": "Credit selection"
        })
    else:
        attribution_df["Credit"] = attribution_df.apply(excess_return, axis=1, args=("Credit",))

    attribution_df["Excess return"] = attribution_df.apply(excess_return, axis=1, args=("",))

    attribution_df["Residual"] = attribution_df["Excess return"] - attribution_df[effects].sum(axis=1)

    attribution_columns = ["Start Date", classification_criteria] + effects + ["Residual", "Excess return", "TotalReturn_portfolio", "TotalReturn_benchmark"]

    attribution_df = attribution_df[attribution_columns]

    return attribution_df


def effects_analysis_instrument(data_df, classification_criteria, classification_value, effects):
    data_df = data_df[data_df[classification_criteria] == classification_value]
    instruments_columns = ["Start Date",
                           "Product description",
                           "DeltaMv_portfolio",
                           "DeltaMvPrice_portfolio",
                           "DeltaMvTrading_portfolio",
                           "DeltaMvCurrency_portfolio",
                           "DeltaMvGlobalOther_portfolio",
                           "DeltaMvRolldown_portfolio",
                           "DeltaMvIncome_portfolio",
                           "DeltaMvYieldCurves_portfolio",
                           "DeltaMvCredit_portfolio",
                           "DeltaMv_benchmark",
                           "DeltaMvPrice_benchmark",
                           "DeltaMvTrading_benchmark",
                           "DeltaMvCurrency_benchmark",
                           "DeltaMvGlobalOther_benchmark",
                           "DeltaMvRolldown_benchmark",
                           "DeltaMvIncome_benchmark",
                           "DeltaMvYieldCurves_benchmark",
                           "DeltaMvCredit_benchmark",
                           "TotalPreviousMv_portfolio",
                           "TotalPreviousMv_benchmark",
                           "TotalReturn_portfolio",
                           "TotalReturn_benchmark"
                           ]

    instruments_df = data_df[instruments_columns].copy()

    instruments_df["Price"] = instruments_df.apply(excess_return, axis=1, args=("Price",))
    instruments_df["Trading"] = instruments_df.apply(excess_return, axis=1, args=("Trading",))
    instruments_df["Currency"] = instruments_df.apply(excess_return, axis=1, args=("Currency",))
    instruments_df["Global other"] = instruments_df.apply(excess_return, axis=1, args=("GlobalOther",))
    instruments_df["Rolldown"] = instruments_df.apply(excess_return, axis=1, args=("Rolldown",))
    instruments_df["Income"] = instruments_df.apply(excess_return, axis=1, args=("Income",))
    instruments_df["Yield curve"] = instruments_df.apply(excess_return, axis=1, args=("YieldCurves",))
    instruments_df["Credit"] = instruments_df.apply(excess_return, axis=1, args=("Credit",))
    instruments_df["Excess return"] = instruments_df.apply(excess_return, axis=1, args=("",))

    instruments_df["Residual"] = instruments_df["Excess return"] - instruments_df[effects].sum(axis=1)

    instruments_columns = ["Start Date", "Product description"] + effects + ["Residual", "Excess return", "TotalReturn_portfolio", "TotalReturn_benchmark"]


    instruments_df = instruments_df[instruments_columns]

    return instruments_df