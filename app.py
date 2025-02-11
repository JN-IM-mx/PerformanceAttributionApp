import streamlit as st
import datetime
import pandas as pd
import numpy as np
from analysis.data_preparation import prepare_data
from analysis.brinson_fachler import brinson_fachler, brinson_fachler_instrument
from analysis.brinson_hood_beebower import brinson_hood_beebower, brinson_hood_beebower_instrument
from analysis.effects_analysis import effects_analysis, effects_analysis_instrument
from analysis.contribution import contribution, contribution_instrument
from analysis.grap_smoothing import grap_smoothing
from analysis.modified_frongello_smoothing import modified_frongello_smoothing
from analysis.contribution_smoothing import contribution_smoothing
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
data_source_toggle = st.segmented_control("Performance data source", ["Use TPK data", "Upload csv files"], default="Use TPK data", label_visibility="hidden")

# Load csv data
correct_format = True

classifications_file = "./data/classifications.csv"
if data_source_toggle == "Use TPK data":
    portfolios_file = "./data/portfolios.csv"
    benchmarks_file = "./data/benchmarks.csv"
else:
    correct_format = False
    file_upload_row = st.container(border=True).columns(2)
    portfolios_file = file_upload_row[0].file_uploader("portfolios.csv file", help="File produced by the Performance service")
    benchmarks_file = file_upload_row[1].file_uploader("benchmarks.csv file", help="File produced by the Performance service")

    # Define your expected columns here
    EXPECTED_PORTFOLIOS_COLUMNS = ['Portfolio', 'Instrument', 'ProductTaxonomy', 'Start Date', 'End Date',
                        'DeltaMv', 'PreviousMv', 'DeltaMvPrice', 'DeltaMvTrading', 'DeltaMvCurrency',
                        'DeltaMvGlobalOther', 'DeltaMvRolldown', 'DeltaMvIncome', 'DeltaMvYieldCurves',
                        'DeltaMvCredit']

    EXPECTED_BENCHMARKS_COLUMNS = ['Benchmark', 'Instrument', 'ProductTaxonomy', 'Start Date', 'End Date',
                                  'DeltaMv', 'PreviousMv', 'DeltaMvPrice', 'DeltaMvTrading', 'DeltaMvCurrency',
                                  'DeltaMvGlobalOther', 'DeltaMvRolldown', 'DeltaMvIncome', 'DeltaMvYieldCurves',
                                  'DeltaMvCredit']

    if portfolios_file is not None and benchmarks_file is not None:
        try:
            # Read just the first row to check columns
            df1 = pd.read_csv(portfolios_file, nrows=1)
            df2 = pd.read_csv(benchmarks_file, nrows=1)

            # Clear the uploaded files buffers
            portfolios_file.seek(0)
            benchmarks_file.seek(0)

            # Get the uploaded file's columns
            ptf_uploaded_columns = df1.columns.tolist()
            bm_uploaded_columns = df2.columns.tolist()

            # Check if columns match expected columns
            if ptf_uploaded_columns != EXPECTED_PORTFOLIOS_COLUMNS or bm_uploaded_columns != EXPECTED_BENCHMARKS_COLUMNS:
                st.error('❌ Wrong file format! Please run "PerfContrib.sh --action export" to generate your files in the contribution-client-tool directory')
                col1, col2, col3 = st.columns([1, 3, 1])
                with col2:
                    st.image("https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExNTQyNDBvMWp1bmp0YWE3MDBxdGtoM2trbjV0bmQzbWNrdWZiYnA4ZyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/JfLdIahamXQI0/giphy.gif", width = 600)
                st.stop()
            else:
                correct_format = True
        except Exception as e:
            st.error(f"Error reading file: {str(e)}")
            st.stop()


# App logic when input files are loaded
if correct_format:

    # User settings
    settings_row = st.columns(6)
    model = settings_row[0].selectbox("Model", ["Brinson-Fachler", "Brinson-Hood-Beebower", "Equity contribution", "Fixed Income attribution", "Fixed Income contribution"])
    if model == "Brinson-Fachler" or model == "Brinson-Hood-Beebower" or model == "Fixed Income attribution":
        smoothing_algorithm = settings_row[1].selectbox("Smoothing algorithm", ["GRAP (Frongello)", "Modified Frongello"])
    else:
        smoothing_algorithm = "Contribution"
    reference_date = settings_row[2].date_input("Start date", datetime.date(2019, 12, 31))
    decimal_places = settings_row[3].selectbox("Decimal places", (2, 4, 8, 12))

    # Load the performance data and classifications files
    portfolio_df = pd.read_csv(portfolios_file)
    benchmark_df = pd.read_csv(benchmarks_file)
    classifications_df = pd.read_csv(classifications_file)

    # Retrieve the list of portfolios and benchmarks from the dataframes
    portfolios = portfolio_df["Portfolio"].unique()
    portfolios = np.sort(portfolios)
    benchmarks = benchmark_df["Benchmark"].unique()
    benchmarks = np.sort(benchmarks)


    if data_source_toggle == "Use TPK data":
        if model == "Brinson-Fachler" or model == "Brinson-Hood-Beebower" or model == "Equity contribution":
            default_portfolio = "EUR EQ LARGE CP"
            default_benchmark_index = 0
        else:
            default_portfolio = "LIQ EUR CORP"
            default_benchmark_index = 1
    else:
        default_portfolio = portfolios[0]
        default_benchmark_index = 0

    # Allow the user to select the list of portfolios and benchmarks to perform the analysis on
    selected_portfolios = settings_row[4].multiselect("Portfolios", portfolios, default_portfolio)
    selected_benchmark = settings_row[5].selectbox("Benchmark", benchmarks,index=default_benchmark_index)

    # Selection of effects for the Effects analysis model
    if model == "Fixed Income attribution":
        effects_full_list = ["Income", "Yield curve", "Credit", "Rolldown", "Trading", "Global other"]
        default_effects = ["Income", "Yield curve", "Credit"]
        effects = st.multiselect("Effects", effects_full_list, default_effects)

    # Create 2 rows and 2 columns, left column is for allocation criteria/instrument, right for analysis results
    analysis_master_row = st.columns([0.25, 0.75])
    analysis_detail_row = st.columns([0.25, 0.75])

    if len(selected_portfolios) > 0:
        # Radio button in the left pane, allowing to select a classification criteria
        if model == "Fixed Income attribution" or model == "Fixed Income contribution":
            classification_criteria = analysis_master_row[0].radio(
                "Allocation criteria",
                ["S&P rating", "Fitch rating", "Moody's rating", "GICS sector", "GICS industry group", "GICS industry", "GICS sub-industry", "Region", "Country"],
            )
        else:
            classification_criteria = analysis_master_row[0].radio(
                "Allocation criteria",
                ["GICS sector", "GICS industry group", "GICS industry", "GICS sub-industry", "Region", "Country"],
            )


        # Prepare the data
        data_df = prepare_data(selected_portfolios, selected_benchmark, portfolio_df, benchmark_df, classifications_df)
        # Apply the model
        if model == "Brinson-Fachler":
            attribution_df = brinson_fachler(data_df, classification_criteria)
        elif model == "Brinson-Hood-Beebower":
            attribution_df = brinson_hood_beebower(data_df, classification_criteria)
        elif model == "Fixed Income attribution":
            attribution_df = effects_analysis(data_df, classification_criteria, effects)
        else:
            attribution_df = contribution(data_df, classification_criteria)

        # Apply the smoothing algorithm
        if smoothing_algorithm == "GRAP (Frongello)":
            master_attribution_df = grap_smoothing(attribution_df, reference_date, classification_criteria)
        elif smoothing_algorithm == "Modified Frongello":
            master_attribution_df = modified_frongello_smoothing(attribution_df, reference_date, classification_criteria)
        else:
            master_attribution_df = contribution_smoothing(attribution_df, reference_date, classification_criteria)

        # Display main analysis results
        if model =="Fixed Income attribution" or model == "Equity contribution" or model == "Fixed Income contribution":
            analysis_master_row[1].markdown(f"**{model}**:")
        else:
            analysis_master_row[1].markdown(f"**{model} attribution**:")

        analysis_master_row[1].dataframe(
            style_dataframe(master_attribution_df, decimal_places),
            hide_index=True,
            width=1000,
            height=dataframe_height(master_attribution_df)
        )

        # Allow user to drill down by classification
        classification_values = [val for val in master_attribution_df[classification_criteria].to_list() if
                                val not in ["Total"]]
        classification_value = analysis_detail_row[0].radio(f"Select a {classification_criteria}:",
                                                            classification_values)

        # Drill-down analysis for specific classification
        # Apply the model
        if model == "Brinson-Fachler":
            instruments_df = brinson_fachler_instrument(data_df, classification_criteria, classification_value)
        elif model == "Brinson-Hood-Beebower":
            instruments_df = brinson_hood_beebower_instrument(data_df, classification_criteria, classification_value)
        elif model == "Fixed Income attribution":
            instruments_df = effects_analysis_instrument(data_df, classification_criteria, classification_value, effects)
        else:
            instruments_df = contribution_instrument(data_df, classification_criteria, classification_value)

        # Apply the smoothing algorithm
        if smoothing_algorithm == "GRAP (Frongello)":
            details_instruments_df = grap_smoothing(instruments_df, reference_date,"Product description")
        elif smoothing_algorithm == "Modified Frongello":
            details_instruments_df = modified_frongello_smoothing(instruments_df, reference_date, "Product description")
        else:
            details_instruments_df = contribution_smoothing(instruments_df, reference_date, "Product description")

        if model == "Brinson-Fachler":
            analysis_detail_row[1].markdown("**Instrument selection details**:")
        elif model == "Brinson-Hood-Beebower":
            analysis_detail_row[1].markdown("**Instrument selection and interaction details**:")
        elif model == "Fixed Income attribution":
            analysis_detail_row[1].markdown("**Instrument effects analysis**:")
        else:
            analysis_detail_row[1].markdown("**Instrument contribution**:")

        analysis_detail_row[1].dataframe(
            style_dataframe(details_instruments_df, decimal_places),
            hide_index=True,
            width=1000,
            height=dataframe_height(details_instruments_df)
        )
