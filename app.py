import streamlit as st
import datetime
import pandas as pd
import numpy as np
from analysis.data_preparation import prepare_data
from analysis.brinson_fachler import brinson_fachler, brinson_fachler_instrument
from analysis.brinson_hood_beebower import brinson_hood_beebower, brinson_hood_beebower_instrument
from analysis.grap_smoothing import grap_smoothing
from utils.styling import style_dataframe, dataframe_height

# Streamlit page configuration
st.set_page_config(
    page_title="Performance attribution",
    page_icon=":bar_chart:",
    layout="wide"
)

# Page title
st.markdown("### :bar_chart: Performance attribution")

# Use TPK data or custom data
data_source_toggle = st.segmented_control("",["Use TPK data", "Upload csv files"], default="Use TPK data")

# Load csv data
classifications_file = "./data/classifications.csv"
if data_source_toggle == "Use TPK data":
    portfolios_file = "./data/portfolios.csv"
    benchmarks_file = "./data/benchmarks.csv"
else:
    file_upload_row = st.container(border=True).columns(2)
    portfolios_file = file_upload_row[0].file_uploader("portfolios.csv file", help="File produced by the Performance service")
    benchmarks_file = file_upload_row[1].file_uploader("benchmarks.csv file", help="File produced by the Performance service")

# App logic when input files are loaded
if portfolios_file is not None and benchmarks_file is not None:

    # User settings
    settings_row = st.columns(5)
    model = settings_row[0].selectbox("Model", ["Brinson-Fachler", "Brinson-Hood-Beebower"])
    reference_date = settings_row[1].date_input("Start date", datetime.date(2019, 12, 31))
    decimal_places = settings_row[2].selectbox("Decimal places", (2, 4, 8, 12))

    # Load the data files, replacing NaNs with zeros
    portfolio_df = pd.read_csv(portfolios_file)
    benchmark_df = pd.read_csv(benchmarks_file)
    classifications_df = pd.read_csv(classifications_file)

    # Retrieve the list of portfolios and benchmarks from the dataframes
    portfolios = portfolio_df["Portfolio"].unique()
    portfolios = np.sort(portfolios)
    benchmarks = benchmark_df["Benchmark"].unique()
    benchmarks = np.sort(benchmarks)


    if data_source_toggle == "Use TPK data":
        default_portfolio = "EUR EQ LARGE CP"
    else:
        default_portfolio = portfolios[0]

    # Allow the user to select the list of portfolios and benchmarks to perform the analysis on
    selected_portfolios = settings_row[3].multiselect("Portfolios", portfolios, default_portfolio)
    selected_benchmark = settings_row[4].selectbox("Benchmark", benchmarks,index=0)

    # Create 2 rows and 2 columns, left column is for allocation criteria/instrument, right for analysis results
    analysis_master_row = st.columns([0.25, 0.75])
    analysis_detail_row = st.columns([0.25, 0.75])

    if len(selected_portfolios) > 0:
        # Radio button in the left pane, allowing to select a classification criteria
        classification_criteria = analysis_master_row[0].radio(
            "Allocation criteria",
            ["GICS sector", "GICS industry group", "GICS industry", "GICS sub-industry", "Region", "Country"],
        )

        # Prepare the data
        data_df = prepare_data(selected_portfolios, selected_benchmark, portfolio_df, benchmark_df, classifications_df)

        if model == "Brinson-Fachler":
            attribution_df = brinson_fachler(data_df, classification_criteria)
        else:
            attribution_df = brinson_hood_beebower(data_df, classification_criteria)

        grap_attribution_df = grap_smoothing(attribution_df, reference_date, classification_criteria)

        # Display main analysis results
        analysis_master_row[1].markdown(f"**{model} Attribution**:")
        analysis_master_row[1].dataframe(
            style_dataframe(grap_attribution_df, decimal_places),
            hide_index=True,
            width=800,
            height=dataframe_height(grap_attribution_df)
        )

        # Allow user to drill down by classification
        classification_values = [val for val in grap_attribution_df[classification_criteria].to_list() if
                                 val not in ["Cash", "Total"]]
        classification_value = analysis_detail_row[0].radio(f"Select a {classification_criteria}:",
                                                            classification_values)

        # Drill-down analysis for specific classification
        if model == "Brinson-Fachler":
            instruments_df = brinson_fachler_instrument(data_df, classification_criteria, classification_value)
        else:
            instruments_df = brinson_hood_beebower_instrument(data_df, classification_criteria, classification_value)

        grap_instruments_df = grap_smoothing(instruments_df, reference_date, "Product description")

        if model == "Brinson-Fachler":
            analysis_detail_row[1].markdown("**Instrument Selection Details**:")
        else:
            analysis_detail_row[1].markdown("**Instrument Selection and Interaction Details**:")

        analysis_detail_row[1].dataframe(
            style_dataframe(grap_instruments_df, decimal_places),
            hide_index=True,
            width=700,
            height=dataframe_height(grap_instruments_df)
        )
