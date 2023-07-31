"""Contains the function to insert dataframes into the database."""
from datetime import datetime
from pprint import pformat
import re
from typing import Literal
import os

import numpy as np
import pandas as pd
from google.cloud.bigquery import Client, LoadJobConfig
from lox_services.config.env_variables import get_env_variable

from lox_services.persistence.config import SERVICE_ACCOUNT_PATH
from lox_services.persistence.database.exceptions import (
    MissingColumnsException,
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
from lox_services.persistence.database.query_handlers import select
from lox_services.persistence.database.utils import generate_id
from lox_services.persistence.storage.constants import INVOICE_BASE_URL
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


def prepare_refunds_test_enviromnent(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Prepare the refunds to be push on the new environment:
    ## Arguments
    - `dataframe`: The dataframe containing the invoice numbers to check.

    ## Example
        >>> prepare_refunds_test_enviromnent(df)

    ## Returns
    - The dataframe ready to be pushed
    """
    if "package_id" not in dataframe.columns:
        if "invoice_number" in dataframe.columns:
            dataframe["package_id"] = dataframe.apply(
                lambda x: generate_id(
                    [x.carrier, x.company, x.invoice_number, x.tracking_number]
                ),
                axis=1,
            )
        else:
            dataframe["package_id"] = dataframe.apply(
                lambda x: generate_id(
                    [x.carrier, x.company, "null", x.tracking_number]
                ),
                axis=1,
            )
    dataframe["request_amount"] = dataframe["total_price"]
    return dataframe


def remove_duplicate_invoices(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Removes invoices that have already been saved in the database.
    ## Arguments
    - `dataframe`: The dataframe containing the invoice numbers to check.

    ## Example
        >>> remove_duplicate_invoices(df)

    ## Returns
    - The dataframe without the invoice numbers already uploaded.
    """
    original_size = len(dataframe.index)
    dataframe["invoice_number"] = dataframe["invoice_number"].astype(str)
    company = dataframe.iloc[0]["company"]
    carrier = dataframe.iloc[0]["carrier"]
    query = f"""
        SELECT DISTINCT invoice_number

        FROM InvoicesData.Invoices

        WHERE carrier = "{carrier}"
            AND company = "{company}"
            AND invoice_number IN UNNEST({dataframe['invoice_number'].unique().tolist()})
    """
    already_pushed = select(query)
    # Remove invoice numbers that were already pushed to BQ
    dataframe = dataframe[
        ~(dataframe["invoice_number"]).isin(already_pushed["invoice_number"])
    ]

    print(
        f"{original_size - len(dataframe.index)} invoice rows deleted before saving to the database."
    )
    print("Result:\n", dataframe)
    return dataframe


def remove_duplicate_refunds(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Removes rows for which the package has already a refund for the same reason, or one related (Lost & Damaged).
    Removes duplicates in the dataframe as well.
    ## Arguments
    - `dataframe`: refunds dataframe that needs to be checked.

    ## Example
        >>> remove_duplicate_refunds(refunds_df)

    ## Returns
    The dataframe cleaned from potential duplicates
    """
    original_size = len(dataframe.index)
    print(f"Checking {original_size} refunds...")
    # Drop duplicates for dummy duplicates, with 'keep' different than False
    dataframe = dataframe.copy().drop_duplicates(
        subset=["tracking_number", "reason_refund"]
    )
    print(dataframe.iloc[0])
    carrier = dataframe.iloc[0]["carrier"]
    company = dataframe.iloc[0]["company"]
    dataframe["reason_refund"] = dataframe.reason_refund.astype(str)
    reason_refunds = dataframe["reason_refund"].unique().tolist()

    dataframe["tracking_number"] = dataframe.tracking_number.astype(str)
    tracking_numbers = dataframe["tracking_number"].tolist()
    query = f"""
    SELECT DISTINCT
        tracking_number || CASE
            WHEN reason_refund IN ("Lost", "Damaged", "Delivery Dispute: Lost", "Delivery Dispute: Damaged")
                THEN 'Lost or Damaged'
                ELSE reason_refund
            END
        AS existing_combo

    FROM InvoicesData.Refunds

    WHERE company = "{company}"
        AND carrier = "{carrier}"
        AND tracking_number IN UNNEST({tracking_numbers})
        AND reason_refund IN UNNEST({reason_refunds})
    """
    print(query)
    existing_data_dataframe = select(query)
    # Lost or damaged trick
    dataframe["smart_reason_refund"] = np.where(
        dataframe["reason_refund"].isin(
            {"Lost", "Damaged", "Delivery Dispute: Lost", "Delivery Dispute: Damaged"}
        ),
        "Lost or Damaged",
        dataframe["reason_refund"],
    )
    # Duplicate check
    dataframe = dataframe.drop_duplicates(
        subset=["tracking_number", "smart_reason_refund"], keep=False
    )
    # Remove rows where the tracking number and reason refund is already present in the database
    dataframe = dataframe[
        ~(dataframe["tracking_number"] + dataframe["smart_reason_refund"]).isin(
            existing_data_dataframe["existing_combo"]
        )
    ]
    dataframe.drop(columns=["smart_reason_refund"], inplace=True)
    print(
        f"{original_size - len(dataframe.index)} refund rows deleted before saving to the database."
    )
    print("Result:\n", dataframe)
    return dataframe


def remove_duplicate_client_invoice_data(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Removes duplicates from client invoices dataframe"""
    tracking_numbers = dataframe["tracking_number"].to_list()
    sql_query = f"""
        SELECT
            tracking_number

        FROM InvoicesData.ClientInvoicesData

        WHERE tracking_number IN UNNEST({tracking_numbers})
    """
    already_saved_tracking_numbers = select(sql_query, False)[
        "tracking_number"
    ].to_list()
    if already_saved_tracking_numbers:
        dataframe = dataframe.loc[
            ~dataframe["tracking_number"].isin(already_saved_tracking_numbers)
        ]
    return dataframe


def remove_duplicate_invoices_from_client_to_carrier(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """Removes duplicates from InvoicesFromClientToCarrier dataframe"""
    carrier = dataframe.iloc[0]["carrier"]
    company = dataframe.iloc[0]["company"]
    tracking_numbers = dataframe["tracking_number"].to_list()
    sql_query = f"""
        SELECT
            tracking_number

        FROM UserData.InvoicesFromClientToCarrier

        WHERE company = "{company}"
            AND carrier = "{carrier}"
            AND tracking_number IN UNNEST({tracking_numbers})
    """
    already_saved_tracking_numbers = select(sql_query, False)[
        "tracking_number"
    ].to_list()
    if already_saved_tracking_numbers:
        dataframe = dataframe.loc[
            ~dataframe["tracking_number"].isin(already_saved_tracking_numbers)
        ]
    return dataframe


def remove_duplicate_NestedAccountNumbers(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Removes already saved account numbers dataframe"""
    carrier = dataframe.iloc[0]["carrier"]
    company = dataframe.iloc[0]["company"]
    sql_query = f"""
        SELECT
            distinct account_number

        FROM UserData.NestedAccountNumbers

        WHERE company = "{company}"
            AND carrier = "{carrier}"
    """
    already_saved_account_numbers = select(sql_query, False)["account_number"].to_list()
    if already_saved_account_numbers:
        print(
            f"Account numbers {already_saved_account_numbers} are already saved in table."
        )
        dataframe = dataframe.loc[
            ~dataframe["account_number"].isin(already_saved_account_numbers)
        ]
    return dataframe


def remove_duplicate_currency_conversion(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Removes already saved currency conversion dataframe"""
    sql_query = """
        SELECT
            distinct date || currency_code_from || currency_code_to AS existing_entry

        FROM Utils.CurrencyConversion
    """
    already_saved_entries = select(sql_query, False)["existing_entry"].to_list()
    if already_saved_entries:
        print(
            f"Currency conversion entries {already_saved_entries} are already saved in table."
        )
        dataframe = dataframe.loc[
            ~(
                dataframe["date"].astype(str)
                + dataframe["currency_code_from"]
                + dataframe["currency_code_to"]
            ).isin(already_saved_entries)
        ]
    return dataframe


def client_invoice_data_quality_check(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Performs data quality check on client invoices dataframe"""
    missing_columns = list(
        {
            "company",
            "carrier",
            "tracking_number",
            "data_source",
            "is_original_invoice",
        }.difference(set(dataframe.columns))
    )
    if missing_columns:
        raise MissingColumnsException(", ".join(missing_columns))
    # Check value invoice_url
    for invoice_url in dataframe["invoice_url"].to_list():
        if not pd.isna(invoice_url) and not re.match(
            r"(https://storage.cloud.google.com).*", invoice_url
        ):
            raise ValueError(f"invoice_url has to start by {INVOICE_BASE_URL}")

    # Check value is_original_invoice
    is_original_invoice_wrong_values = dataframe[
        ~dataframe["is_original_invoice"].isin([True, False])
    ]
    if not is_original_invoice_wrong_values.empty:
        wrong_values = (
            is_original_invoice_wrong_values["is_original_invoice"].unique().tolist()
        )
        raise ValueError(
            f"Incorrect values {wrong_values} for field is_original_invoice. Only True or False are authorized"
        )

    dataframe["quantity"] = pd.to_numeric(dataframe["quantity"])
    dataframe["net_amount"] = pd.to_numeric(dataframe["net_amount"])
    dataframe = dataframe.loc[~(dataframe["quantity"] < 0)]
    dataframe.loc[dataframe["quantity"] == 0, "quantity"] = 1
    dataframe.loc[dataframe["net_amount"] == 0, "net_amount"] = 1
    return dataframe


def check_lox_invoice_not_exists(dataframe: pd.DataFrame) -> None:
    """Check if the lox invoice number doesn't already exist in the database.
    ## Arguments
    - `dataframe`: The dataframe containing the lox invoice number to check.

    ## Example
        >>> check_lox_invoice_not_exists(df)

    ## Returns
    - Nothing if the check is successful.
    - Raises Exception otherwise.
    """
    invoice_number = dataframe.iloc[0]["invoice_number"]
    query = f"""
        SELECT
            invoice_number

        FROM LoxData.DueInvoices

        WHERE invoice_number = "{invoice_number}"
    """
    already_saved = select(query, False)
    if not already_saved.empty:
        print_error(
            f"The Lox invoice number {invoice_number} has already been attributed!"
        )
        raise Exception(
            "Cannot save in the Database. Lox invoice number has already been attributed."
        )
    else:
        print_success("Due Invoices checks are good.")


def check_duplicate_invoices_details(dataframe: pd.DataFrame) -> None:
    """Check if the invoices details have not already been added.
    ## Arguments
    - `dataframe`: The dataframe containing the invoices details.

    ## Example
        >>> check_duplicate_invoices_details(df)

    ## Returns
    - Nothing if the check is successful.
    - Raises Exception otherwise.
    """
    invoice_numbers = list(set(dataframe["invoice_number"].to_list()))
    if len(invoice_numbers) > 1:  # We do this to have a better handle over the check
        raise Exception("Cannot save the details for more than one invoice_number.")
    else:
        invoice_number = invoice_numbers[0]

    descriptions = tuple(dataframe["description"])
    if len(descriptions) == 1:
        descriptions = str(descriptions).replace(",", "")
    query_string = f"""
        SELECT
            invoice_number

        FROM LoxData.InvoicesDetails

        WHERE invoice_number = "{invoice_number}"
            AND description IN {descriptions}
    """
    already_saved = select(query_string, False)
    if not already_saved.empty:
        print_error("These invoices details have already been saved!")
        raise ValueError(
            "Cannot save in the Database. Invoices details have already been saved."
        )

    print_success("Invoices details checks are good.")


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
