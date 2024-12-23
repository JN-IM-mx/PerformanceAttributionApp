import pandas as pd

def prepare_data(ptf_list, bm, ptf_df, bm_df):
    # Filter ptf_df on portfolios in ptf_list and remove unneeded columns
    ptf_df = ptf_df[ptf_df["Portfolio"].isin(ptf_list)]
    ptf_df = ptf_df.drop(["Portfolio", "ProductTaxonomy", "End Date"], axis=1)
    ptf_df = ptf_df.groupby(["Start Date", "Instrument"]).sum().reset_index()

    # Filter bm_df on portfolios in bm_list and remove unneeded columns
    bm_df = bm_df[bm_df["Benchmark"] == bm]
    bm_df = bm_df.drop(["Benchmark", "ProductTaxonomy", "End Date"], axis=1)

    merged_df = pd.merge(ptf_df, bm_df, how="outer", on=["Instrument", "Start Date"], suffixes=("_portfolio", "_benchmark")).fillna(0)
    return merged_df


def add_classification(df, classifications_df, classification_criteria):
    classification_columns = ["Product", "Product description", classification_criteria]
    classifications_df = classifications_df[classification_columns]
    df = pd.merge(df, classifications_df, left_on="Instrument", right_on="Product", how="left").fillna(
        "Cash")
    return df
    df
