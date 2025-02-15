import streamlit as st
import pandas as pd


def load_csv_files(data_source, file_upload_row):

    classifications_file = "./data/classifications.csv"
    classifications_df = pd.read_csv(classifications_file)

    if data_source == "Use TPK data":
        portfolios_file = "./data/portfolios.csv"
        benchmarks_file = "./data/benchmarks.csv"
        portfolios_df = pd.read_csv(portfolios_file)
        benchmarks_df = pd.read_csv(benchmarks_file)
    else:
        portfolios_file = file_upload_row[0].file_uploader("portfolios.csv file",
                                                           help="File produced by the Performance service")
        benchmarks_file = file_upload_row[1].file_uploader("benchmarks.csv file",
                                                           help="File produced by the Performance service")

        if portfolios_file is not None and benchmarks_file is not None:
            portfolios_df = pd.read_csv(portfolios_file)
            benchmarks_df = pd.read_csv(benchmarks_file)
        else:
            portfolios_df = pd.DataFrame()
            benchmarks_df = pd.DataFrame()


    return classifications_df, portfolios_df, benchmarks_df



def validate_dataframes(portfolios_df, benchmarks_df):

        correct_format = False

        expected_portfolios_columns = ['Portfolio', 'Instrument', 'ProductTaxonomy', 'Start Date', 'End Date',
                                       'DeltaMv', 'PreviousMv', 'DeltaMvPrice', 'DeltaMvTrading', 'DeltaMvCurrency',
                                       'DeltaMvGlobalOther', 'DeltaMvRolldown', 'DeltaMvIncome', 'DeltaMvYieldCurves',
                                       'DeltaMvCredit']

        expected_benchmark_columns = ['Benchmark', 'Instrument', 'ProductTaxonomy', 'Start Date', 'End Date',
                                       'DeltaMv', 'PreviousMv', 'DeltaMvPrice', 'DeltaMvTrading', 'DeltaMvCurrency',
                                       'DeltaMvGlobalOther', 'DeltaMvRolldown', 'DeltaMvIncome', 'DeltaMvYieldCurves',
                                       'DeltaMvCredit']

        try:
            # # Read just the first row to check columns
            # df1 = pd.read_csv(portfolios_file, nrows=1)
            # st.write(df1)
            # df2 = pd.read_csv(benchmarks_file, nrows=1)
            # st.write(df2)

            # Clear the uploaded files buffers
            # portfolios_file.seek(0)
            # benchmarks_file.seek(0)

            # Get the uploaded file's columns
            ptf_uploaded_columns = portfolios_df.columns.tolist()
            bm_uploaded_columns = benchmarks_df.columns.tolist()

            # Check if columns match expected columns
            if ptf_uploaded_columns != expected_portfolios_columns or bm_uploaded_columns != expected_benchmark_columns:
                st.error(
                    '❌ Wrong file format! Please run "PerfContrib.sh --action export" to generate your files in the contribution-client-tool directory')
                col1, col2, col3 = st.columns([1, 3, 1])
                with col2:
                    st.image(
                        "https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExNTQyNDBvMWp1bmp0YWE3MDBxdGtoM2trbjV0bmQzbWNrdWZiYnA4ZyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/JfLdIahamXQI0/giphy.gif",
                        width=600)
                st.stop()
            else:
                correct_format = True
        except Exception as e:
            st.error(f"Error reading file: {str(e)}")
            st.stop()

        return correct_format

