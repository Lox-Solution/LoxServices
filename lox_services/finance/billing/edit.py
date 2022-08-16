from typing import List, Tuple, Union
import pandas as pd

from lox_services.finance.billing.generate import generate_and_store_bill_documents, generate_bill_details
from lox_services.persistence.database.queries.billing import (
    delete_invoices_details, 
    set_is_not_lox_claim_for_tracking_numbers,
    update_due_amount_with_fee,
    update_invoice_date_to_today)
from lox_services.persistence.database.datasets import LoxData_dataset
from lox_services.persistence.database.insert import insert_dataframe_into_database
from lox_services.utils.general_python import print_success

def update_bill_by_deletion(company: str, bill_number: str) -> Union[str, None]:
    """Updates the invoice details corresponding to the invoice number with the new credits.
    """    
    print(f"Deleting bill details for bill: {bill_number}...")
    delete_invoices_details(bill_number)
    
    print("Regenerating the invoice details...")
    generate_bill_details(
        company,
        bill_number
    )
    
    print_success(f"{bill_number} updated successfully!")
    return company


def update_bill_fee(company: str, bill_number: str, new_fee: float) -> None:
    """Updates the bill fee.
        Saves the bill to Google Cloud Storage.
        
        ## Arguments
        - `company`: The company name of the customer.
        - `bill_number`: The bill number to update the fee of.
        - `new_fee`: The new fee to update the bill with.
    """
    print(f"Updating bill {bill_number} fee to {new_fee}...")
    update_due_amount_with_fee(bill_number, new_fee)
    generate_and_store_bill_documents(company, bill_number)


def remove_tracking_numbers_from_bill(company: str, bill_number: str, tracking_numbers: List[str]) -> int:
    """Removes the given tracking numberS from a bill by:
        - Updating the Refunds table attribute 'lox_invoice_number' to null
            and 'is_lox_claim' to False for the given tracking numbers and bill number
        - Deleting the billing details (InvoicesDetails table) for the given bill number
        - Generating the new billing details (InvoicesDetails table again)
        - Generating and storing the billing documents
        
        # Arguments
        - `bill_number`: The bill number to remove the tracking numbers from.
        - `tracking_numbers`: The tracking numbers to remove.

        # Returns
        - The number of tracking numbers removed. If 0, then it didn't work.
    """
    print("Removing lox claims from the Refunds table...")
    set_is_not_lox_claim_for_tracking_numbers(
        company,
        bill_number,
        tracking_numbers
    )
    
    number_of_updated =  update_bill_by_deletion(company, bill_number)
    generate_and_store_bill_documents(company, bill_number)
    return number_of_updated


def add_credit_notes_to_bill(company: str, bill_number: str, credit_notes: List[Tuple[str, float]]) -> None:
    """Credits the given credit notes to the given bill.
        Adds the credit notes to the InvoicesDetails table.
        Updates the invoice date.
        Saves the bill to Google Cloud Storage.
        
        ## Arguments
        - `company`: The company name of the customer.
        - `bill_number`: The bill number to credit the credit notes to.
        - `credit_notes`: The credit notes to credit.
        
        ## Example
            >>> credit_notes_to_bill(
                    "Helloprint",
                    "0000-0000",
                    [
                        ("March bill - 1Z821E846897040980", -30.12),
                        ("Partnership discount - January", -500.0)
                    ]
                )
    """
    print(f"Adding credit notes ({len(credit_notes)}) to bill {bill_number}...")
    credit_notes_df = pd.DataFrame(credit_notes, columns=["description", "due_amount"])
    
    credit_notes_df["invoice_number"] = bill_number
    credit_notes_df["orders"] = 1
    credit_notes_df["saved_amount"] = None
    
    credit_notes_df["description"] = credit_notes_df["description"].apply(
        lambda description: "Credit: " + description.replace("Credit: ", "")
    )
    print(credit_notes_df)
    insert_dataframe_into_database(credit_notes_df, LoxData_dataset.InvoicesDetails)
    update_invoice_date_to_today(company, bill_number)
    generate_and_store_bill_documents(company, bill_number)


def add_customer_bill_reference_to_lox_bill(company: str, lox_bill_number: str, customer_bill_number: str) -> None:
    """Adds the customer own bill number to the Lox bill.
        Updates the invoice date.
        Saves the bill to Google Cloud Storage.
        
        ## Arguments
        - `company`: The company name of the customer.
        - `lox_bill_number`: The Lox bill number to add the customer own bill number to.
        - `customer_bill_number`: The customer own bill number to add to the Lox bill.
    """
    print(f"Adding customer own bill number {customer_bill_number} to Lox bill {lox_bill_number}...")
    generate_and_store_bill_documents(company, lox_bill_number, customer_bill_number)

