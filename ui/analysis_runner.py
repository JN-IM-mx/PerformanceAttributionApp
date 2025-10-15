"""
Analysis orchestration logic for running attribution and contribution analysis.
"""
from analysis import prepare_data
from .model_registry import (
    MODEL_REGISTRY,
    CONTRIBUTION_REGISTRY,
    SMOOTHING_REGISTRY,
    CONTRIBUTION_SMOOTHING
)


def run_analysis(settings, portfolio_df, benchmark_df, classifications_df, classification_criteria):
    """
    Run the analysis based on user settings.

    Args:
        settings: Dictionary containing user selections
        portfolio_df: Portfolio data DataFrame
        benchmark_df: Benchmark data DataFrame
        classifications_df: Classifications data DataFrame
        classification_criteria: Selected classification criteria

    Returns:
        Tuple of (master_df, instrument_function) where instrument_function
        can be called to get instrument-level details
    """
    # Prepare the data
    data_df = prepare_data(
        settings['portfolios'],
        settings['benchmark'],
        portfolio_df,
        benchmark_df,
        classifications_df,
        settings['start_date'],
        settings['end_date']
    )

    if settings['analysis_type'] == "Contribution":
        master_df, instrument_func = _run_contribution_analysis(
            data_df,
            classification_criteria
        )
    else:
        master_df, instrument_func = _run_attribution_analysis(
            data_df,
            classification_criteria,
            settings['model'],
            settings['smoothing'],
            settings.get('effects', None)
        )

    return master_df, instrument_func


def _run_contribution_analysis(data_df, classification_criteria):
    """
    Run contribution analysis.
    """
    # Run master-level analysis
    master_df = CONTRIBUTION_REGISTRY["master"](data_df, classification_criteria)
    master_df = CONTRIBUTION_SMOOTHING(master_df, classification_criteria)

    # Create instrument-level function
    def get_instruments(classification_value):
        instruments_df = CONTRIBUTION_REGISTRY["instrument"](
            data_df,
            classification_criteria,
            classification_value
        )
        return CONTRIBUTION_SMOOTHING(instruments_df, "Product description")

    return master_df, get_instruments


def _run_attribution_analysis(data_df, classification_criteria, model, smoothing, effects=None):
    """
    Run attribution analysis with specified model and smoothing.
    """
    # Get model functions from registry
    model_funcs = MODEL_REGISTRY[model]

    # Run master-level analysis
    if model == "Fixed income attribution":
        master_df = model_funcs["master"](data_df, classification_criteria, effects)
    else:
        master_df = model_funcs["master"](data_df, classification_criteria)

    # Apply smoothing
    smoothing_func = SMOOTHING_REGISTRY[smoothing]
    master_df = smoothing_func(master_df, classification_criteria)

    # Create instrument-level function
    def get_instruments(classification_value):
        if model == "Fixed income attribution":
            instruments_df = model_funcs["instrument"](
                data_df,
                classification_criteria,
                classification_value,
                effects
            )
        else:
            instruments_df = model_funcs["instrument"](
                data_df,
                classification_criteria,
                classification_value
            )

        # Apply smoothing to instruments
        return smoothing_func(instruments_df, "Product description")

    return master_df, get_instruments
