import datetime
import pandas as pd
from analysis.data_preparation import prepare_data, add_classification
from analysis.brinson_fachler import brinson_fachler
from analysis.brinson_fachler_instrument import brinson_fachler_instrument
from analysis.brinson_hood_beebower import brinson_hood_beebower
from analysis.total_returns import total_returns
from analysis.grap_smoothing import grap_smoothing
from utils.styling import highlight_total_row

# File paths
classifications_file = "./data/equities_classifications.csv"
portfolios_file = "./data/portfolios.csv"
benchmarks_file = "./data/benchmarks.csv"

# Test parameters
model = "Brinson-Fachler"
reference_date = datetime.date(2019, 12, 31)
portfolios = ["EUR EQ LARGE CP"]
# portfolios = ["LIQ EUR CORP"]
benchmark = "EURO STOXX 50"
# benchmarks = ["IBOXX E LIQ COR"]
classification_criteria = "GICS sector"

# Load and transform data
portfolio_df = pd.read_csv(portfolios_file)
benchmark_df = pd.read_csv(benchmarks_file)
classifications_df = pd.read_csv(classifications_file)

data = prepare_data(portfolios, benchmark, portfolio_df,benchmark_df)
data = add_classification(data, classifications_df, classification_criteria)

attribution_df = brinson_fachler(data, classification_criteria)
print(attribution_df.to_string())

classification_value = "Financials"

instrument_selection_df = brinson_fachler_instrument(data, classification_criteria, classification_value)

print(instrument_selection_df.to_string())

# brinson_fachler_result = brinson_fachler(prepared_data, classification_criteria)
# total_returns_df = total_returns(brinson_fachler_result, reference_date)
#
# print(total_returns_df)


