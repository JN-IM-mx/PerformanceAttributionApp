import datetime
import pandas as pd
from analysis.data_preparation import prepare_data
from analysis.brinson_fachler import brinson_fachler, brinson_fachler_instrument
from analysis.brinson_hood_beebower import brinson_hood_beebower, brinson_hood_beebower_instrument
from analysis.grap_smoothing import grap_smoothing

# File paths
classifications_file = "./data/classifications.csv"
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
classification_value = "Financials"

# Load and transform data
portfolio_df = pd.read_csv(portfolios_file)
benchmark_df = pd.read_csv(benchmarks_file)
classifications_df = pd.read_csv(classifications_file)

data_df = prepare_data(portfolios, benchmark, portfolio_df,benchmark_df, classifications_df)

attribution_df = brinson_fachler(data_df, classification_criteria)
instruments_df = brinson_fachler_instrument(data_df, classification_criteria, classification_value)

attribution_df2 = brinson_hood_beebower(data_df, classification_criteria)
instruments_df2 = brinson_hood_beebower_instrument(data_df, classification_criteria, classification_value)

grap_attribution_df = grap_smoothing(attribution_df, reference_date, classification_criteria)
grap_instrument_df = grap_smoothing(instruments_df, reference_date, "Product description")
grap_attribution_df2 = grap_smoothing(attribution_df2, reference_date, classification_criteria)
grap_instrument_df2 = grap_smoothing(instruments_df2, reference_date, "Product description")

print(grap_attribution_df.tail().to_string())
print(grap_attribution_df2.tail().to_string())
print(grap_instrument_df.tail().to_string())
print(grap_instrument_df2.tail().to_string())