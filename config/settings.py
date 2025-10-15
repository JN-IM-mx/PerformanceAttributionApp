"""
Configuration settings and constants for the application.
"""
import datetime

# Streamlit page configuration
PAGE_CONFIG = {
    "page_title": "Performance contribution and attribution",
    "page_icon": ":bar_chart:",
    "layout": "wide"
}

# Performance period date mappings
# Note: These are hardcoded dates based on the TPK sample data
PERFORMANCE_PERIODS = {
    "1Y": datetime.date(2019, 11, 1),
    "YTD": datetime.date(2020, 1, 1),
    "6M": datetime.date(2020, 5, 1),
    "1M": datetime.date(2020, 10, 1),
    "MTD": datetime.date(2020, 10, 1),
    "WTD": datetime.date(2020, 10, 5),
    "1D": datetime.date(2020, 10, 6)
}

# Default portfolio and benchmark selections for TPK data
DEFAULT_PORTFOLIOS = {
    "Equity": {
        "portfolio": "EUR EQ LARGE CP",
        "benchmark_index": 0
    },
    "Fixed income": {
        "portfolio": "LIQ EUR CORP",
        "benchmark_index": 1
    }
}

# Classification criteria by asset class
CLASSIFICATION_CRITERIA = {
    "Equity": [
        "GICS sector",
        "GICS industry group",
        "GICS industry",
        "GICS sub-industry",
        "Region",
        "Country"
    ],
    "Fixed income": [
        "S&P rating",
        "Fitch rating",
        "Moody's rating",
        "GICS sector",
        "GICS industry group",
        "GICS industry",
        "GICS sub-industry",
        "Region",
        "Country"
    ]
}

# Fixed income effects analysis options
FIXED_INCOME_EFFECTS = {
    "full_list": ["Income", "Yield curve", "Credit", "Rolldown", "Trading", "Global other"],
    "default": ["Income", "Yield curve", "Credit"]
}

# Custom date range defaults (for custom period selection)
CUSTOM_DATE_DEFAULTS = {
    "start_date": datetime.date(2020, 1, 1),
    "end_date": datetime.date(2020, 10, 6)
}
