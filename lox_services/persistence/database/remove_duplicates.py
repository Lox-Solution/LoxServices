from typing import Any, List
import numpy as np
import pandas as pd

from lox_services.persistence.database.query_handlers import select
from lox_services.utils.enums import BQParameterType
from lox_services.utils.general_python import print_error, print_success

# ------InvoicesData Dataset-------
CHUNK_SIZE = (
    50000  # max length of a list that can be passed in argument in a sql request
)


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
    reason_refunds = list(
        set(
            dataframe["reason_refund"].unique().tolist()
            + ["Damaged", "Lost", "Delivery Dispute"]
        )
    )

    dataframe["tracking_number"] = dataframe.tracking_number.astype(str)
    tracking_numbers = dataframe["tracking_number"].tolist()
    query = f"""
    SELECT DISTINCT
        tracking_number || CASE
            WHEN reason_refund IN ("Lost", "Damaged", "Delivery Dispute")
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
        dataframe["reason_refund"].isin({"Lost", "Damaged", "Delivery Dispute"}),
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


def remove_duplicate_deliveries(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Removes duplicate rows from the provided DataFrame based on certain criteria.

    This function checks for duplicate deliveries in the input DataFrame by comparing
    the combination of tracking number, status, and formatted datetime. If duplicates
    are found, they are removed from the DataFrame. The function also ensures that the
    datetime column is formatted correctly for comparison.

    Args:
        dataframe (pd.DataFrame): The input DataFrame containing delivery data.

    Returns:
        pd.DataFrame: A DataFrame with duplicate deliveries removed, if any.
    """
    if dataframe.empty:
        return dataframe

    print("Checks for duplicate rows in db..")
    dataframe = dataframe.dropna(subset=["tracking_number", "status", "date_time"])

    # make sure datetime column is in same string format than the one on BigQuery.
    dataframe["formated_datetime"] = pd.to_datetime(
        dataframe["date_time"].astype(str), errors="ignore"
    ).dt.strftime("%Y-%m-%d %H:%M:%S")

    dataframe["concat_values"] = (
        dataframe["tracking_number"].astype(str)
        + dataframe["status"].astype(str)
        + dataframe["formated_datetime"].astype(str)
    )

    tracking_numbers_to_check = dataframe["tracking_number"].unique().tolist()

    sql_query = """
        SELECT
            tracking_number || status || date_time as concat_values
        FROM
            InvoicesData.Deliveries
        WHERE
        tracking_number IN UNNEST(@tracking_numbers)
    """

    tn_lists = [
        tracking_numbers_to_check[i : i + CHUNK_SIZE]
        for i in range(0, len(tracking_numbers_to_check), CHUNK_SIZE)
    ]
    deliveries_already_in_db = pd.DataFrame(columns=["concat_values"])
    for tn_list in tn_lists:
        deliveries_already_in_db = pd.concat(
            [
                deliveries_already_in_db,
                select(
                    sql_query,
                    print_query=False,
                    parameters=[
                        (
                            "tracking_numbers",
                            BQParameterType.STRING,
                            tn_list,
                        )
                    ],
                ),
            ]
        )
    original_length = len(dataframe.index)
    if not deliveries_already_in_db.empty:
        duplicate_values = deliveries_already_in_db["concat_values"].unique().tolist()
        dataframe = dataframe.loc[~dataframe["concat_values"].isin(duplicate_values)]

    print("Number of rows removed:", original_length - len(dataframe.index))
    return dataframe.drop(columns=["concat_values", "formated_datetime"])


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


# ------UserData Dataset----------


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


# ------LoxData Dataset----------


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


# ------Utils Dataset----------


def remove_duplicate_currency_conversion(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Removes already saved currency conversion dataframe"""
    sql_query = """
        SELECT
            distinct date || currency_code_from || currency_code_to AS existing_entry

        FROM Utils.CurrencyConversion
    """
    already_saved_entries = select(sql_query, False)["existing_entry"].to_list()
    if already_saved_entries:
        dataframe = dataframe.loc[
            ~(
                dataframe["date"].astype(str)
                + dataframe["currency_code_from"]
                + dataframe["currency_code_to"]
            ).isin(already_saved_entries)
        ]
    return dataframe


# ----------CarrierData Dataset----------


def remove_duplicate_package_information(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Removes already saved package information dataframe"""
    tns = dataframe["tracking_number"].unique().tolist()
    sql_query = """
        SELECT
            distinct carrier || company || tracking_number AS existing_entry

        FROM CarrierData.PackageInformation
        WHERE tracking_number IN UNNEST(@tracking_numbers)
    """
    already_saved_entries = select(
        sql_query,
        parameters=(("tracking_numbers", BQParameterType.STRING, tns),),
    )["existing_entry"].tolist()
    if already_saved_entries:
        dataframe["concat_values"] = (
            dataframe["carrier"].astype(str)
            + dataframe["company"].astype(str)
            + dataframe["tracking_number"].astype(str)
        )
        dataframe = dataframe.loc[
            ~dataframe["concat_values"].isin(already_saved_entries)
        ].drop(columns=["concat_values"])
    return dataframe
