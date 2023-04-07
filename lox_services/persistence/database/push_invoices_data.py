"""All functions to save invoice data into the database"""
import os
from enum import Enum
from typing import Mapping, List, Tuple

import pandas as pd
import numpy as np

from lox_services.persistence.database.datasets import InvoicesData_dataset
from lox_services.persistence.database.insert import insert_dataframe_into_database
from lox_services.persistence.database.schema import (
    dates_refunds,
    dtypes_deliveries,
    dtypes_invoices,
    dtypes_refunds,
    na_deliveries,
    na_invoices,
    na_refunds,
)
from lox_services.persistence.database.utils import (
    format_time,
    replace_nan_with_none_in_dataframe,
)
from lox_services.utils.enums import Files


def process_df(
    df: pd.DataFrame,
    dtype_cols: Mapping[str, str],
    na_fill_value: Mapping[str, str],
    format_time_cols: bool = False,
    replace_empty_dates: bool = False,
) -> pd.DataFrame:
    """Process dataframes before appending them to a processing batch."""
    # If some columns are missing, add the columns with None values
    missing_columns = set(dtype_cols).difference(set(df.columns))
    if missing_columns:
        df = df.assign(**dict.fromkeys(missing_columns, None))

    # Format time
    if format_time_cols and "date_time" not in df.columns:
        df["time"] = df["time"].apply(format_time)
        df["date_time"] = np.where(
            (df["date"].isna()) | (df["time"].isna()),
            pd.NaT,
            df["date"] + "T" + df["time"],
        )

    df = df.fillna(value=na_fill_value).astype(dtype_cols)

    if replace_empty_dates:
        df[dates_refunds] = df[dates_refunds].replace({"": None})

    return df


def push_run_to_database(
    run_output_folder: str, carrier: str, company: str, account_number_input: str = ""
) -> dict:
    """Add to the database all the important files of the given folder.
    Returns a dictionary reporesenting the run report.
    ## Arguments
    - `run_output_folder`: The output folder that contains files that we will push
    - `carrier_input`: The carrier that was run as a result of the given output folder
    - `company_input`: The company that was run as a result of the given output folder
    - `account_number_input` : the account_number that was run, REQUESTED for colissimo

    ## Returns
        - A report of the inserted files.

    ## Example
        >>> report = push_run_to_database(output_folder, "UPS")
    """
    if account_number_input == "" and carrier == "Colissimo":
        raise Exception("Account number need to be put in the function's parameters")

    if account_number_input != "" and carrier != "Colissimo":
        account_number_input = ""

    date_format = "YYYY-MM-DD"

    list_files_to_push: List[Tuple[pd.DataFrame, Enum]] = []

    invoice_path = os.path.join(run_output_folder, Files.INVOICES.value)
    if os.path.exists(invoice_path):
        # Read the invoice file and check the datetime format
        df_invoice: pd.DataFrame = pd.read_csv(
            invoice_path,
            infer_datetime_format=date_format,
            header=0,
            dtype={"postal_code_reciever": str},
        )
        # In case postal_code_reciever falsely gets interpreted as a float
        df_invoice["postal_code_reciever"] = df_invoice[
            "postal_code_reciever"
        ].str.removesuffix(".0")

        if not df_invoice.empty:
            df_invoice = process_df(df_invoice, dtypes_invoices, na_invoices)

            list_files_to_push.append((df_invoice, InvoicesData_dataset.Invoices))

    # Prepare deliveries data
    deliveries_path = os.path.join(
        run_output_folder, account_number_input, Files.DELIVERIES.value
    )
    if os.path.exists(deliveries_path):
        # Read the delivery file and check the datetime format
        df_deliveries: pd.DataFrame = pd.read_csv(
            deliveries_path,
            converters=dtypes_deliveries,
            infer_datetime_format=date_format,
            header=0,
        )
        if not df_deliveries.empty:

            df_deliveries = process_df(
                df_deliveries, dtypes_deliveries, na_deliveries, format_time_cols=True
            )

            list_files_to_push.append(
                (df_deliveries, InvoicesData_dataset.Deliveries),
            )

    refunds_path = os.path.join(
        run_output_folder, account_number_input, Files.REFUNDS.value
    )
    # Prepare refunds data
    if os.path.exists(refunds_path):
        # Read the refund file and check the datetime format
        df_refund: pd.DataFrame = pd.read_csv(
            refunds_path, infer_datetime_format=date_format, header=0
        )
        if not df_refund.empty:
            df_refund = process_df(
                df_refund, dtypes_refunds, na_refunds, replace_empty_dates=True
            )
            list_files_to_push.append((df_refund, InvoicesData_dataset.Refunds))

    report = {}
    for dataframe, table in list_files_to_push:
        dataframe = replace_nan_with_none_in_dataframe(dataframe)
        number_inserted_rows = insert_dataframe_into_database(
            dataframe=dataframe, table=table
        )  # API request
        report[table.name] = number_inserted_rows

    print("report:\n", report)
    return report
