"""Contains the function to insert dataframes into the database."""
from datetime import datetime
from pprint import pformat
from typing import Literal
import os

import pandas as pd
from google.cloud.bigquery import Client, LoadJobConfig
from lox_services.config.env_variables import get_env_variable

from lox_services.persistence.config import SERVICE_ACCOUNT_PATH
from lox_services.persistence.database.exceptions import (
    InvalidDataException,
)
from lox_services.persistence.database.datasets import (
    InvoicesData_dataset,
    InvoicesDataLake_dataset,
    LoxData_dataset,
    Mapping_dataset,
    DatasetTypeAlias,
    UserData_dataset,
    Utils_dataset,
)
from lox_services.persistence.database.quality_checks import (
    client_invoice_data_quality_check,
)
from lox_services.persistence.database.remove_duplicates import (
    check_duplicate_invoices_details,
    check_lox_invoice_not_exists,
    remove_duplicate_NestedAccountNumbers,
    remove_duplicate_client_invoice_data,
    remove_duplicate_currency_conversion,
    remove_duplicate_deliveries,
    remove_duplicate_invoices,
    remove_duplicate_invoices_from_client_to_carrier,
    remove_duplicate_refunds,
)
from lox_services.utils.general_python import print_error, print_success

# pylint: disable=line-too-long

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(SERVICE_ACCOUNT_PATH)


def add_metadata_columns(dataframe: pd.DataFrame, write_method: str) -> pd.DataFrame:
    """Adds the metadata columns to the dataframe.
    ## Arguments
        -dataframe: The dataframe to add the columns to.
        -write_method: Which GBQ client method gets called.

    ## Returns the dataframe with the extra columns
    """
    current_datetime = datetime.now()
    for metadata_columns in ["insert_datetime", "update_datetime"]:
        # If the insertion metod is load_table_from_dataframe, the colum must be a datetime
        if write_method == "load_table_from_dataframe":
            dataframe[metadata_columns] = current_datetime
        else:
            dataframe[metadata_columns] = current_datetime.strftime(
                "%Y-%m-%dT%H:%M:%S.%f"
            )

    return dataframe


def insert_dataframe_into_database(
    dataframe: pd.DataFrame,
    table: DatasetTypeAlias,
    write_method: Literal[
        "insert_rows_from_dataframe", "load_table_from_dataframe"
    ] = "insert_rows_from_dataframe",
    write_disposition: Literal[
        "WRITE_TRUNCATE", "WRITE_APPEND", "WRITE_EMPTY"
    ] = "WRITE_APPEND",
) -> int:
    """Inserts every row of the dataframe into the database.
    Does duplicate checks for specific tables (Invoices, Refunds).
    ## Arguments
    - `dataframe`: The dataframe to insert into the database. Must have good column names.
    - `table`: The database table name. It must be one of the datasets.
    - 'write_method': Which GBQ client method gets called. 'load_table_from_dataframe' avoids
    bugs related to handling nullable PyArrow datatypes like Int64.
    - `write_disposition`. Specifies the action that occurs if the destination table
    already exists when using the 'load_table_from_dataframe' method. The following values
    are supported:
        - WRITE_TRUNCATE: If the table already exists, BigQuery overwrites the table
        data and uses the schema from the query result.
        - WRITE_APPEND: If the table already exists, BigQuery appends the data to the table.
        - WRITE_EMPTY: If the table already exists and contains data, a 'duplicate'
        error is returned in the job result.
    Each action is atomic and only occurs if BigQuery is able to complete the job
    successfully. Creation, truncation and append actions occur as one atomic update
    upon job completion.

    ## Example
        >>> insert_dataframe_into_database(df, InvoicesData_dataset.Invoices)

    ## Returns
    - The number of inserted rows.
    - An Exception if a check didn't pass.
    """
    if (
        write_disposition == "WRITE_TRUNCATE"
        and get_env_variable("ENVIRONMENT") == "production"
    ):
        raise ValueError("WRITE_TRUNCATE is not allowed in production environment.")

    if not isinstance(dataframe, pd.DataFrame):
        print_error("dataframe argument must be a DataFrame.")
        return 0

    if dataframe.empty:
        print("Empty dataframe, insert aborted because unnecessary.")
        return 0

    print(
        f"Trying to save a dataframe ({len(dataframe.index)} rows) to Google BigQuery table {table.name}"
    )
    if isinstance(table, InvoicesData_dataset):
        dataset = "InvoicesData"
        dataframe = remove_duplicate_headers_dataframe(dataframe)
        if table.name == "Invoices":
            dataframe = remove_duplicate_invoices(dataframe)
        if table.name == "Refunds":
            dataframe = remove_duplicate_refunds(dataframe)
        if table.name == "ClientInvoicesData":
            dataframe = remove_duplicate_client_invoice_data(dataframe)
            dataframe = client_invoice_data_quality_check(dataframe)
        if table.name == "Deliveries":
            dataframe = remove_duplicate_deliveries(dataframe)

    elif isinstance(table, LoxData_dataset):
        dataset = "LoxData"
        if table.name == "DueInvoices":
            check_lox_invoice_not_exists(dataframe)
        if table.name == "InvoicesDetails":
            check_duplicate_invoices_details(dataframe)
    elif isinstance(table, Mapping_dataset):
        dataset = "Mapping"
    elif isinstance(table, InvoicesDataLake_dataset):
        dataset = "InvoicesDataLake"
    elif isinstance(table, UserData_dataset):
        dataset = "UserData"
        if table.name == "InvoicesFromClientToCarrier":
            dataframe = remove_duplicate_invoices_from_client_to_carrier(dataframe)

        if table.name == "NestedAccountNumbers":
            dataframe = remove_duplicate_NestedAccountNumbers(dataframe)
    elif isinstance(table, Utils_dataset):
        dataset = "Utils"
        if table.name == "CurrencyConversion":
            dataframe = remove_duplicate_currency_conversion(dataframe)
    else:
        raise TypeError("'table' param must be an instance of one of the tables Enum.")

    if dataframe.empty:
        print("Empty dataframe, insert aborted because unnecessary.")
        return 0

    print_success(
        f"Checks done - Saving dataframe ({len(dataframe.index)} rows) to Google BigQuery table {table.name}"
    )
    bigquery_client = Client()
    # Prepares a reference to the dataset
    dataset_ref = bigquery_client.dataset(dataset)
    # Select the table where you want to push the data
    table_ref = dataset_ref.table(table.name)
    table = bigquery_client.get_table(table_ref)
    dataframe = dataframe.where(pd.notnull(dataframe), None)

    # Add metadata columns
    dataframe = add_metadata_columns(dataframe, write_method)

    if write_method == "insert_rows_from_dataframe":
        errors = bigquery_client.insert_rows_from_dataframe(
            table=table,
            dataframe=dataframe,
            ignore_unknown_values=True,
        )[0]

        if errors:
            raise InvalidDataException(
                f"{pformat(errors)}\n{len(errors)} errors occured while inserting dataframe into {table}."
            )
    else:
        job_config = LoadJobConfig(write_disposition=write_disposition)
        load_job = bigquery_client.load_table_from_dataframe(
            dataframe,
            f"{table.project}.{table.dataset_id}.{table.table_id}",
            job_config=job_config,
        ).result()

        if load_job.errors:
            raise InvalidDataException(
                f"{pformat(load_job.errors)}\n{len(load_job.errors)} errors occured while "
                f"inserting dataframe into {table} with method {write_disposition}."
            )

    print_success("Success, everything has been inserted.")

    return len(dataframe.index)


def remove_duplicate_headers_dataframe(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Removes rows that are similar to the header and are not in the first line of the given dataframe
    ## Arguments
    - `dataframe`: dataframe that needs to be checked.

    ## Example
        >>> remove_duplicate_headers_dataframe(refunds_df)

    ## Returns
    The dataframe cleaned from potential header duplicates
    """
    return dataframe.loc[~(dataframe == dataframe.columns).all(axis="columns")]
