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
        analysis_details_row[1].dataframe(
            style_dataframe(details_df, settings['decimals']),
            hide_index=True,
            width=1000,
            height=dataframe_height(details_df)
        )
