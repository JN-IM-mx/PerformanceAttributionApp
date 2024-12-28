def style_dataframe(df, decimals):

    # Create a dictionary that formats only float columns to the desired decimals
    format_dict = {}
    numeric_cols = df.select_dtypes(exclude="object").columns
    for col in numeric_cols:
        format_dict[col] = f"{{:.{decimals}%}}"

    # Function to highlight the last row
    def highlight_last_row(row):
        # Check if row index is the last row in the DataFrame
        if row.name == df.index[-1]:
            return ["background-color: #F0F2F6; font-weight: bold;"] * len(row)
        else:
            return [""] * len(row)

    # Function to apply red font for negative numeric values
    def highlight_negative(val):
        try:
            # Attempt to convert to float and check if negative
            val_float = float(val)
            color = "red" if val_float < 0 else "black"
        except ValueError:
            # Handle non-numeric values
            color = "black"
        return f"color: {color}"

    # Combine all styling in one chain
    styled = (
        df.style
          .format(format_dict)                   # Apply number formatting
          .apply(highlight_last_row, axis=1)     # Highlight last row
          .applymap(highlight_negative)
    )
    return styled


def dataframe_height(df):
    return (len(df.index) + 1) * 35 + 3
