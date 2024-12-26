def style_dataframe(df, decimals):
    """
    Styles the given DataFrame by:
      1. Formatting float columns to 'decimals' decimal places.
      2. Highlighting the last row in light grey and making it bold.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame to style.
    decimals : int, optional
        The number of decimal places to format float columns. Default is 2.

    Returns
    -------
    pd.io.formats.style.Styler
        A Styler object with the desired formatting applied.
    """
    # 1. Create a dictionary that formats only float columns to the desired decimals
    format_dict = {}
    numeric_cols = df.select_dtypes(exclude="object").columns
    for col in numeric_cols:
        format_dict[col] = f"{{:.{decimals}%}}"

    # 2. Function to highlight the last row
    def highlight_last_row(row):
        # Check if row index is the last row in the DataFrame
        if row.name == df.index[-1]:
            return ["background-color: #F0F2F6; font-weight: bold;"] * len(row)
        else:
            return [""] * len(row)

    # Combine all styling in one chain
    styled = (
        df.style
          .format(format_dict)                   # Apply number formatting
          .apply(highlight_last_row, axis=1)     # Highlight last row
    )
    return styled


def dataframe_height(df):
    return (len(df.index) + 1) * 35 + 3
