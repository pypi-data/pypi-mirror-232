import pandas as pd
import logging
from abbr import STATE_ABBREVIATIONS

logging.basicConfig(
    level=logging.INFO,  # Set the logging level to DEBUG, you can change this if you want
    format='%(levelname)s:%(message)s'  
)

def state_abbr(df, columns=None):
    """
    Replace state abbreviations or full state names in specified columns of a pandas DataFrame with AP style abbreviations.

    Args:
        df (pandas.DataFrame): The DataFrame containing state abbreviations or full state names to be replaced.
        columns (list or None): A list of column names to parse. If None, all string columns are processed.

    Returns:
        pandas.DataFrame: A new DataFrame with state abbreviations replaced by AP style abbreviations.
    """
    
    # Create a copy of the input DataFrame to avoid modifying the original
    cleaned_df = df.copy()
    
    if columns is None:
        columns_to_process = cleaned_df.select_dtypes(include='object').columns
    else:
        columns_to_process = columns
    
    # iterate through the selected columns
    for column in columns_to_process:
        logging.info(f"Processing column: {column}")
        
        for state_key, ap_style_abbr in STATE_ABBREVIATIONS.items():
            
            cleaned_df[column] = cleaned_df[column].str.replace(
                r'\b' + state_key + r'\b|\b' + ap_style_abbr.lower() + r'\b',
                ap_style_abbr,
                case=False,  # case-insensitive replacement
                regex=True  
            )
        
        cleaned_df[column] = cleaned_df[column].str.strip()
    
    return cleaned_df
