"""All functions to manage the invoices saved in Google Cloud Storage."""
import os
import numpy

import pandas as pd

from lox_services.finance.billing.constants import BILLING_ASSETS_FOLDER, MANDATORY_BILLING_FIELDS
from lox_services.persistence.database.queries.billing import get_company_details
from lox_services.persistence.storage.storage import upload_file
from lox_services.utils.general_python import print_error

CREDIT_WAYS_PATH = os.path.join(BILLING_ASSETS_FOLDER, "credit_ways.csv")

def store_lox_invoice(company: str, language: str, path_to_pdf: str) -> None:
    """Saves the pdf invoice in Google Cloud Storage `lox_invoices` bucket. The filename stored si the same as local. If the file exists already it will be overridden.
        ## Arguments
        - `company`: The company concerned by the invoice.
        - `language`: The language of the invoice.
        - `path_to_pdf`: The local path to the pdf file.
    """
    file_name = path_to_pdf.split('/')[-1]
    destination_path = f"{company}/{language}/{file_name}"
    upload_file("lox_invoices", path_to_pdf, destination_path)


def _get_credit_way_by_carrier_and_reason_refund(carrier: str, reason_refund: str) -> str:
    """Returns the credit way for a given carrier and reason refund."""
    credit_ways = pd.read_csv(CREDIT_WAYS_PATH)
    try:
        way = credit_ways.loc[
            (credit_ways["carrier"] == carrier) 
            & (credit_ways["reason_refund"] == reason_refund),
        "credited_by"].values[0]
    except IndexError:  # If the carrier or reason refund is not in the credit_ways file
        way = "Credit line"
    
    return way


def populate_details_with_credit_way(details: pd.DataFrame) -> pd.DataFrame:
    """Populates the details dataframe with the credit way."""
    details["credited_by"] = details.apply(
        lambda row: _get_credit_way_by_carrier_and_reason_refund(row["carrier"], row["reason_refund"]),
        axis=1
    )
    return details


def is_company_mandatory_billing_data_filled(company: str) -> None:
    """Checks if the mandatory billing data for a given company is filled.
        ## Arguments
        - `company`: The company concerned by the billing.

        ## Returns
        - True if the mandatory billing data is filled.
        - Raises an exception with details otherwise.
    """
    details = get_company_details(company)
    mandatory_not_filled = []
    invoicing_email_not_filled = 0
    invoicing_email_empty = 0
    auto_email: bool = details["auto_email"]
    
    for field in MANDATORY_BILLING_FIELDS:
        value = details[field]
        if field == "invoicing_emails":
            value: numpy.ndarray
            if auto_email is not True:
                continue
            
            if not numpy.any(value):
                invoicing_email_not_filled += 1
                continue
            
            for element in value:
                email_address = element["email_address"]
                if email_address is None or pd.isna(email_address) or email_address == "":
                    invoicing_email_empty += 1
        
        elif pd.isna(value) or value is None or value == "": # "", NaN, None
            mandatory_not_filled.append(field)
    
    exception_message = "" # We do this to cumulate Exception messages so that the customer team can update multiple fields at once.
    if len(mandatory_not_filled) != 0:
        exception_message += f"- mandatory_not_filled: The following mandatory billing fields for {company} are not filled: {mandatory_not_filled} -"

    if invoicing_email_not_filled != 0:
        exception_message += f"- invoicing_email_not_filled: The invoicing emails for {company} are not filled ({invoicing_email_not_filled}) -"
    
    if invoicing_email_empty != 0:
        exception_message += f"- invoicing_email_empty: The invoicing email addresses for {company} are empty ({invoicing_email_empty}) -"
        
    if len(exception_message) != 0:
        print_error(exception_message)
        raise Exception(exception_message)
    
    return None
