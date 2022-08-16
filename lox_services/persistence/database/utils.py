"""All utils functions used in GoogleBigQuery module only."""
from datetime import datetime
import re
import pandas as pd

from lox_services.utils.general_python import print_error

def generate_id(columns: list) -> str:
    """Generates an id with column names
        ## Arguments
        
        - `columns`: Columns that we want to concatenate to create the id
    
        ## Returns
        A string containing the id
    """
    new_id = ""
    if len(columns) > 0:
        for column in columns:
            if column is None or pd.isna(column):
                new_id += "null"
            else: 
                new_id += str(column)
            new_id += "_"
        return new_id[:-1]
    else :
        raise Exception("You can't pass empty list as parameter")


def replace_nan_with_none_in_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Replace Nans with Nones in a csv file given
        ## Arguments
        
        - `df`: Dataframe that we want to update
    
    """
    return df.where(pd.notnull(df), None)


def format_time(time: str):
    "Puts time string to the right format %H:%M:%S"
    
    if pd.isna(time):
        return "00:00:00"
    
    if re.search("^[1-9]:.*", str(time)):
        time = "0"+time
    
    try: 
        time = datetime.strftime(datetime.strptime(time, "%H:%M"), "%H:%M:%S")
        return time
    except Exception:
        pass
    
    try:
        time = datetime.strftime(datetime.strptime(time, "%H:%M:%S"), "%H:%M:%S")
        return time
    except Exception:
        message = f"Not good format: {time}"
        print_error(message)
        # raise Exception(message) from exception        
        return "00:00:00"


def format_datetime(date: datetime.date, time: datetime.time):
    """Generates the a datetime format if the date is not nul
    
        ## Arguments:
        - `date`: date use for the formating 
        - `time`: time use for the formating 
        
        ## Returns:
        - The concatenated datetime 
        - A NaT variable if one variable is empty
    """
    
    if pd.isna(time) or pd.isna(date):
        return pd.NaT
    else:
        return date + 'T' + time


def equal_condition_handle_none_value(key: str, value: str):
    """Generates the good 'equal' condition for a sql query by handling None values."""
    if value is None:
        condition = f'{key} is null'
    else:
        condition = f'{key} = "{value}"'
    return condition
