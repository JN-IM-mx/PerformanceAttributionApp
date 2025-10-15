"""
Performance Attribution and Contribution Reconciliation Application

A Streamlit web application for analyzing portfolio performance against benchmarks
using various attribution models and contribution analysis methods.
"""
import streamlit as st
from config.settings import PAGE_CONFIG, CLASSIFICATION_CRITERIA
from utils import load_csv_files, validate_dataframes, style_dataframe, dataframe_height
from ui.components import render_settings
from ui.analysis_runner import run_analysis

# Configure Streamlit page
st.set_page_config(**PAGE_CONFIG)

# Page title
st.markdown("### :bar_chart: Performance Attribution and Contribution Reconciliation")
st.text("")
st.text("")

# File upload section
file_upload_row = st.columns(2)
settings_row1 = st.columns(5)

data_source_toggle = settings_row1[0].pills(
    "Data source",
    ["Use TPK data", "Upload csv files"],
    default="Use TPK data"
)

# Load CSV files
classifications_df, portfolio_df, benchmark_df = load_csv_files(
    data_source_toggle,
    file_upload_row
)

# Validate dataframes
correct_format = False
if not portfolio_df.empty and not benchmark_df.empty:
    correct_format = validate_dataframes(portfolio_df, benchmark_df)

# Main application logic
if correct_format:
    # Render settings panel and get user selections
    settings = render_settings(portfolio_df, benchmark_df, data_source_toggle)

    # Add vertical spacing
    st.text("")
    st.text("")

    # Check if portfolios are selected
    if len(settings['portfolios']) > 0:
        # Create layout columns
        analysis_master_row = st.columns([0.25, 0.75])
        analysis_details_row = st.columns([0.25, 0.75])
    # User settings
    asset_class = settings_row1[1].pills("Asset class", ["Equity", "Fixed income"], default="Equity")
    contribution_attribution = settings_row1[2].pills("Analysis", ["Attribution", "Contribution"], default="Attribution")

    # Model selection in case of Attribution analysis
    if contribution_attribution == "Attribution":
        if asset_class == "Equity":
            model = settings_row1[3].pills("Model", ["Brinson-Fachler", "Brinson-Hood-Beebower"], default="Brinson-Fachler")
        else:
            model = settings_row1[3].pills("Model", ["Standard fixed income attribution", "with Brinson Fachler on credit (POC)"], default="Standard fixed income attribution")
            # Define effects list based on fixed income model
            effects_full_list = ["Income", "Yield curve", "Credit", "Rolldown", "Trading", "Global other"]
            if model == "Standard fixed income attribution":
                effects = st.multiselect("Effects", effects_full_list, ["Rolldown", "Income", "Yield curve", "Credit"])
            else:
                effects_brinson = effects_full_list.copy()
                credit_index = effects_brinson.index("Credit")
                effects_brinson[credit_index:credit_index+1] = ["Credit allocation", "Credit selection"]
                effects = st.multiselect("Effects", effects_brinson, ["Rolldown", "Income", "Yield curve", "Credit allocation", "Credit selection"])
                effects_brinson_instrument = list(dict.fromkeys(["Credit" if effect in ["Credit allocation", "Credit selection"] else effect for effect in effects]))
        smoothing_algorithm = settings_row1[4].pills("Smoothing algorithm", ["Frongello", "Modified Frongello"], default="Frongello")

    # Second row of user settings: portfolios, benchmarks, performance period and decimals
    settings_row2 = st.columns(5)

    # Portfolios and benchmark to be loaded
    # Retrieve the list of portfolios and benchmarks from the dataframes
    portfolios = portfolio_df["Portfolio"].unique()
    portfolios = np.sort(portfolios)
    benchmarks = benchmark_df["Benchmark"].unique()
    benchmarks = np.sort(benchmarks)

    # Define the default portfolios and benchmark
    if data_source_toggle == "Use TPK data":
        if asset_class == "Equity":
            default_portfolio = "EUR EQ LARGE CP"
            default_benchmark_index = 0
        else:
            default_portfolio = "LIQ EUR CORP"
            default_benchmark_index = 1
    else:
        default_portfolio = portfolios[0]
        default_benchmark_index = 0


    # Allow the user to select the list of portfolios and benchmarks to perform the analysis on
    selected_portfolios = settings_row2[0].multiselect("Portfolios", portfolios, default_portfolio)
    selected_benchmark = settings_row2[1].selectbox("Benchmark", benchmarks,index=default_benchmark_index)

    # Reference date selection using predefined performance periods
    # Note these are hardcoded dates based on the tpk data
    performance_period = settings_row2[2].pills("Performance period", ["1Y", "YTD","6M","1M", "MTD", "WTD", "1D", "Custom"], default="YTD")
    performance_period_date_dict = {
        "1Y": datetime.date(2019, 11, 1),
        "YTD": datetime.date(2020, 1, 1),
        "6M": datetime.date(2020, 5, 1),
        "1M": datetime.date(2020, 10, 1),
        "MTD": datetime.date(2020, 10, 1),
        "WTD": datetime.date(2020, 10, 5),
        "1D": datetime.date(2020, 10, 6)
    }

    if performance_period == "Custom":
        start_date = settings_row2[2].date_input("Select start date", datetime.date(2020, 1, 1))
        end_date = settings_row2[2].date_input("Select end date", datetime.date(2020, 10, 6))
    else:
        start_date = performance_period_date_dict[performance_period]
        end_date = pd.to_datetime(portfolio_df["End Date"]).max()

    decimal_places = settings_row2[3].segmented_control("Decimal places", [2, 4, 8, 12], default=2)

    # Add some vertical space
    st.text("")
    st.text("")

    # Create 2 rows and 2 columns, left column is for allocation criteria/instrument, right for analysis results
    analysis_master_row = st.columns([0.25, 0.75])
    analysis_details_row = st.columns([0.25, 0.75])

    if len(selected_portfolios) > 0:
        # Radio button in the left pane, allowing to select a classification criteria
        if asset_class == "Fixed income":
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
        data_df = prepare_data(selected_portfolios, selected_benchmark, portfolio_df, benchmark_df, classifications_df, start_date, end_date)

        # Apply the requested analysis
        if contribution_attribution == "Contribution":
            master_df = contribution(data_df, classification_criteria)
            master_df = contribution_smoothing(master_df, classification_criteria)
        else:
            # Apply the model (without any smoothing)
            if model == "Brinson-Fachler":
                master_df = brinson_fachler(data_df, classification_criteria)
            elif model == "Brinson-Hood-Beebower":
                master_df = brinson_hood_beebower(data_df, classification_criteria)
            elif model == "Standard fixed income attribution":
                master_df = effects_analysis(data_df, classification_criteria, effects, credit_mode="standard")
            elif model == "with Brinson Fachler on credit (POC)":
                master_df = effects_analysis(data_df, classification_criteria, effects, credit_mode="brinson")

            # Apply the smoothing
            if smoothing_algorithm == "Frongello":
                master_df = grap_smoothing(master_df, classification_criteria)
            elif smoothing_algorithm == "Modified Frongello":
                master_df = modified_frongello_smoothing(master_df, classification_criteria)

        # Render classification criteria selector
        classification_criteria = analysis_master_row[0].radio(
            "Allocation criteria",
            CLASSIFICATION_CRITERIA[settings['asset_class']]
        )

        # Run the analysis
        master_df, get_instruments = run_analysis(
            settings,
            portfolio_df,
            benchmark_df,
            classifications_df,
            classification_criteria
        )

        # Display master-level results
        analysis_master_row[1].markdown("**Performance analysis:**")
        analysis_master_row[1].dataframe(
            style_dataframe(master_df, settings['decimals']),
            hide_index=True,
            width=1000,
            height=dataframe_height(master_df)
        )

        # Get classification values for drill-down
        classification_values = [
            val for val in master_df[classification_criteria].to_list()
            if val not in ["Total"]
        ]

        # Render classification value selector
        classification_value = analysis_details_row[0].radio(
            f"Select a {classification_criteria}:",
            classification_values
        )

        # Get instrument-level details
        details_df = get_instruments(classification_value)

        # Display instrument-level results
        analysis_details_row[1].markdown("**Instruments details:**")
        # Drill-down analysis for specific classification
        # Allow user to drill down by classification
        classification_values = [val for val in master_df[classification_criteria].to_list() if
                                 val not in ["Total"]]
        classification_value = analysis_details_row[0].radio(f"Select a {classification_criteria}:",
                                                             classification_values)

        # Apply the requested analysis at instrument level
        if contribution_attribution == "Contribution":
            instruments_df = contribution_instrument(data_df, classification_criteria, classification_value)
            details_instruments_df = contribution_smoothing(instruments_df, "Product description")
        else:
            # Apply the model (without any smoothing)
            if model == "Brinson-Fachler":
                instruments_df = brinson_fachler_instrument(data_df, classification_criteria, classification_value)
            elif model == "Brinson-Hood-Beebower":
                instruments_df = brinson_hood_beebower_instrument(data_df, classification_criteria, classification_value)
            elif model == "Standard fixed income attribution":
                instruments_df = effects_analysis_instrument(data_df, classification_criteria, classification_value, effects)
            elif model == "with Brinson Fachler on credit (POC)":
                instruments_df = effects_analysis_instrument(data_df, classification_criteria, classification_value, effects_brinson_instrument)

            # Apply the smoothing
            if smoothing_algorithm == "Frongello":
                details_instruments_df = grap_smoothing(instruments_df,"Product description")
            elif smoothing_algorithm == "Modified Frongello":
                details_instruments_df = modified_frongello_smoothing(instruments_df, "Product description")

        analysis_details_row[1].markdown("**Instruments details**:")
        analysis_details_row[1].dataframe(
            style_dataframe(details_df, settings['decimals']),
            hide_index=True,
            width=1000,
            height=dataframe_height(details_df)
        )
