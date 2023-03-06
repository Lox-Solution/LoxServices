"""All utils functions used in GoogleBigQuery module only."""
import os
import re
from datetime import datetime, timedelta, timezone
from typing import Literal

import pandas as pd
from google.cloud.bigquery import Client, DatasetReference, LoadJobConfig

from lox_services.persistence.config import SERVICE_ACCOUNT_PATH
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
    else:
        raise Exception("You can't pass empty list as parameter")


def replace_nan_with_none_in_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Replace Nans with Nones in a csv file given
    ## Arguments

    - `df`: Dataframe that we want to update

    """
    return df.where(pd.notnull(df), None)


def format_time(time: str):
    """Puts time string to the right format %H:%M:%S"""

    if pd.isna(time):
        return "00:00:00"

    if re.search("^[1-9]:.*", str(time)):
        time = "0" + time

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
        return date + "T" + time


def equal_condition_handle_none_value(key: str, value: str):
    """Generates the good 'equal' condition for a sql query by handling None values."""
    if value is None:
        condition = f"{key} is null"
    else:
        condition = f'{key} = "{value}"'
    return condition


def make_temporary_table(
    df: pd.DataFrame,
    project: str,
    dataset_id: str,
    table_name: str,
    write_disposition: Literal[
        "WRITE_TRUNCATE", "WRITE_APPEND", "WRITE_EMPTY"
    ] = "WRITE_TRUNCATE",
) -> None:
    """
    Make the table out of a dataframe and set it to be temporary. Avoids race condition
    with parallelized execution of scripts.
    ## Arguments
    - `df`: A pandas DataFrame which you would like to upload.
    - `project`: The ID of the BigQuery project.
    - `dataset_id`: The ID of the BigQuery dataset.
    - `table`: The ID of the BigQuery table.
    - `write_disposition`. Specifies the action that occurs if the destination table
    already exists. The following values are supported:
        - WRITE_TRUNCATE: If the table already exists, BigQuery overwrites the table
        data and uses the schema from the query result.
        - WRITE_APPEND: If the table already exists, BigQuery appends the data to the table.
        - WRITE_EMPTY: If the table already exists and contains data, a 'duplicate'
        error is returned in the job result.
    Each action is atomic and only occurs if BigQuery is able to complete the job
    successfully. Creation, truncation and append actions occur as one atomic update
    upon job completion.
    """

    table = ".".join((project, dataset_id, table_name))

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = SERVICE_ACCOUNT_PATH
    client = Client()
    query_job = client.load_table_from_dataframe(
        df, table, job_config=LoadJobConfig(write_disposition=write_disposition)
    )
    query_job.result()
    if query_job.errors is not None:
        raise ValueError(
            f"Error occured when loading data to the table - f{query_job.errors}"
        )

    table_ref = DatasetReference(project, dataset_id).table(table_name)
    table_ref = client.get_table(table_ref)
    table_ref.expires = datetime.now(timezone.utc) + timedelta(hours=1)
    client.update_table(table_ref, ["expires"])  # API request
