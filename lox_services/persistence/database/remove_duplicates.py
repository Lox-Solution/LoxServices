import numpy as np
import pandas as pd

from lox_services.persistence.database.query_handlers import select
from lox_services.utils.general_python import print_error, print_success

# ------InvoicesData Dataset-------


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
