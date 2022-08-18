"""All functions to generate Lox invoices
"""
import os
from datetime import datetime
from typing import List, Optional

import pandas as pd

from lox_services.config.paths import OUTPUT_FOLDER
from lox_services.finance.billing.constants import BILLING_ASSETS_FOLDER, MIN_INVOICING_AMOUNT
from lox_services.finance.billing.utils import populate_details_with_credit_way, store_lox_invoice
from lox_services.pdf.writer import (
    generate_pdf_file_from_html_css,
    dataframe_to_html_without_pandas_style)
from lox_services.persistence.database.queries.billing import (
    get_company_details_from_invoice_number,
    get_current_max_invoice_number,
    get_detailed_billed_amount,
    get_due_invoices_companies_by_month,
    get_invoice_details,
    get_invoice_summary,
    get_signed_companies_with_credits_not_billed,
    update_credited_packages_with_bill_number)
from lox_services.persistence.database.datasets import LoxData_dataset
from lox_services.persistence.database.insert import insert_dataframe_into_database
from lox_services.translation.enums import TranslationModules
from lox_services.translation.translate import get_translations
from lox_services.utils.general_python import (
    Colors,
    colorize,
    format_snake_case_to_human_upper_case,
    format_amount_to_human_string,
    get_file_size,
    print_success,
    safe_mkdir)


#############################################################################################
#                                   WATCH OUT !                                             #
#                                                                                           #
#              Before this time, the "bills" were called "lox invoices",                    #
#              but due to common confusion with the invoices                                #
#              from our customers, we decided to call them "bills" instead.                 #
#              This is the reason why you will see database attributes named                #
#              lox_invoice_number/invoice_number instead of bill/bill_number.               #
#                                                                                           #
#############################################################################################


def get_new_bill_numbers() -> pd.DataFrame:
    """Gets the new bill numbers for the database (DueInvoices) if none exists for the selected invoice_date."""
    invoice_date = datetime.today().date()
    
    due_invoices = get_signed_companies_with_credits_not_billed(MIN_INVOICING_AMOUNT)
    due_invoices["invoice_date"] = invoice_date
    due_invoices["status"] = "Not paid"
    due_invoices["invoice_number"] = None
    
    already_generated_due_invoices = get_due_invoices_companies_by_month(invoice_date)
    already_generated_companies = already_generated_due_invoices["company"].to_list()
    to_drop = []
    for index, due_invoices_row in due_invoices.iterrows():
        company = due_invoices_row["company"]
        if company in already_generated_companies:
            to_drop.append(index)
            invoice_number = already_generated_due_invoices[already_generated_due_invoices["company"] == company]["invoice_number"]
            due_invoices_row["invoice_number"] = invoice_number
    
    new_due_invoices = due_invoices.drop(index=to_drop).reset_index(drop=True)
    
    max_lox_invoice_number = get_current_max_invoice_number()
    for index, row in new_due_invoices.iterrows():
        company = row["company"]
        max_lox_invoice_number += 1
        full_lox_invoice_number = str(max_lox_invoice_number).zfill(8)
        formatted_lox_invoice_number = full_lox_invoice_number[0:4] + "-" + full_lox_invoice_number[4:8]
        print("New bill:", company, formatted_lox_invoice_number)
        new_due_invoices.at[index, "invoice_number"] = formatted_lox_invoice_number
    
    result = pd.concat([
            already_generated_due_invoices,
            new_due_invoices
        ],
        ignore_index = True
    )\
    .sort_values(by=["invoice_number"])\
    .reset_index(drop=True)
    
    return result


def generate_bill_details(company: str, bill_number: str) -> int:
    """Generates the bill details for a given company and it's bill number.
        Updates the Refunds table attribute "lox_invoice_number" with the given bill number.

        ## Keyword Arguments
        - `company`: The company to generate the bill details for.
        - `bill_number`: The bill number to generate the bill details for.
        
        ## Returns
        - The number of rows inserted into the database.
    
    """
    print(f"\nGenerating bill details for {company} with bill number {bill_number}.")
    bill_details = get_detailed_billed_amount(company, bill_number)
    bill_details["invoice_number"] = bill_number
    
    #If the due amount is inferior to €10, we don't generate the invoice details
    if bill_details["due_amount"].sum() < MIN_INVOICING_AMOUNT and company != 'Helloprint':
        print(colorize(f"{company} bill is skipped because due amount is inferior to {MIN_INVOICING_AMOUNT}.", Colors.Cyan))
        return 0
    
    bill_details = bill_details.astype({"orders": int}) # important! default is Int64 (not json serializable)
    
    return insert_dataframe_into_database(bill_details, LoxData_dataset.InvoicesDetails)


def _populate_bill_details(company: str, bill_number: str) -> int:
    """ Populates the bill details (InvoicesDetails & DueInvoices) for a given company and it's bill number.
        # Argmuments
        - `company`: The company to generate the bill details for.
        - `bill_number`: The bill number to generate the bill details for.

        # Returns
        - The number of rows inserted in the InvoicesDetails table.
    """
    number_of_billed_rows = generate_bill_details(
        company,
        bill_number,
    )
    
    if number_of_billed_rows == 0:
        return 0
    
    # We add the due invoice after the details, because the amount check is in the bill details generation
    due_invoice = pd.DataFrame({
        "company": [company],
        "invoice_number": [bill_number],
        "invoice_date": [datetime.today().date()],
        "status": ["Not paid"],
        "insert_datetime": [datetime.now()],
    })
    insert_dataframe_into_database(due_invoice, LoxData_dataset.DueInvoices)

    return number_of_billed_rows


def generate_and_store_bill_documents(company: str, bill_number: str, customer_bill_number: Optional[str] = None) -> List[str]:
    """Generates the Lox bill as pdf file and saves it in Google Cloud Storage.
        Generates the invoice details csv locally.
        
        ## Arguments
        - `company`: Company concerned by the pdf generation.
        - `lox_invoice_number`: The invoice number to use. It must exist in the database.
        - `customer_bill_number`: The customer's bill number, can be None.
        
        ## Example
            >>> generate_and_save_bill(
                company="Suitsupply",
                lox_invoice_number="0000-0196",
            )
        
        ## Returns
        - The absolute paths to the pdf files generated.
    """
    style_path = os.path.join(BILLING_ASSETS_FOLDER, 'invoice_style.css')
    with open(os.path.join(BILLING_ASSETS_FOLDER, 'invoice_template.html'), 'r') as file:
        original_html_template = file.read()
    
    customer_details = get_company_details_from_invoice_number(bill_number)
    if customer_details.shape[0] == 0:
        print("Invoice number not found in due invoices (while getting customer details).")
        print("Skipping invoice generation")
        return
    
    vat = customer_details.iloc[0]["vat"]
    invoice_summary = get_invoice_summary(bill_number)
    invoice_details = get_invoice_details(bill_number)
    total_saved_amount = round(invoice_summary["saved_amount"].sum(), 2)
    total = round(invoice_summary["due_amount"].sum(), 2)
    vat_value = round(vat / 100 * total, 2)
    total_with_vat = round(total*(1 + vat / 100), 2)
    paths_to_pdfs = []
    languages = ['EN']
    country = customer_details.iloc[0]["country"].upper()
    if country != "EN":
        languages.append(country)
    
    for language in languages:
        # pylint: disable=cell-var-from-loop
        def format_amount_to_human_string_with_language(value):
            return format_amount_to_human_string(value, language)
        
        other_fields = [
            ("invoice_number", bill_number),
            ("customer_bill_number", customer_bill_number),
            ("invoice_reason", "Lox monthly invoice"),
            ("total_saved_amount", format_amount_to_human_string_with_language(total_saved_amount)),
            ("total_with_vat", format_amount_to_human_string_with_language(total_with_vat)),
        ]
        
        translations = get_translations(language, TranslationModules.BILLING_INVOICE)
        def _translate_column_names(string: str):
            """Lambda function created because it can take only one argument"""
            t_string = f"t_{string}" #We use this make sure we don't take non-translated words
            try:
                #pylint: disable=cell-var-from-loop
                return translations[t_string]
            except KeyError:
                return string
        
        html_template = original_html_template
        
        # Translation insertion in template
        # WATCH OUT ! There are templates in the translations !
        for name, value in translations.items():
            html_template = html_template.replace(f"{{{name}}}",str(value))
        
        # Data insertion in template
        for name, value in list(customer_details.iloc[0].items())+other_fields:
            if value is not None:
                if name == "customer_bill_number":
                    value = f"{translations.get('t_customer_bill_number')}: {value}"
            
                if name == "siret":
                    value = f"{translations.get('t_siret')}: {value}"
            
            if value is None or pd.isna(value) or value == "None" or value != value:
                value = ''
            
            # Some names will be skipped because they are not in the template
            html_template = html_template.replace(f"{{{name}}}", str(value))
        
        invoice_summary_tmp = invoice_summary.append(
            [pd.DataFrame({
                'reason': ['Sub-total', 'VAT', 'Total'],
                'quantity': ['', f"{vat} %", ''],
                'saved_amount': [total_saved_amount, '', ''],
                'due_amount': [total, vat_value, total_with_vat]
            })],
            ignore_index=True
        )
        
        # invoice_summary_table
        invoice_summary_tmp["saved_amount"] = invoice_summary_tmp["saved_amount"].apply(format_amount_to_human_string_with_language)
        invoice_summary_tmp["due_amount"] = invoice_summary_tmp["due_amount"].apply(format_amount_to_human_string_with_language)
        invoice_summary_tmp = invoice_summary_tmp.rename(columns=_translate_column_names)
        invoice_summary_tmp = invoice_summary_tmp.rename(columns=format_snake_case_to_human_upper_case)
        print(f"Generating HTML for the invoice summary table - {language}...")
        html_invoice_summary_table = dataframe_to_html_without_pandas_style(invoice_summary_tmp)
        html_template = html_template.replace("{invoice_summary_table}",html_invoice_summary_table)
        
        # invoice_details_table
        print(f"Generating HTML for the invoice details table - {language}...")
        invoice_details_tmp = invoice_details
        invoice_details_tmp = invoice_details_tmp.rename(columns=_translate_column_names)
        invoice_details_tmp = invoice_details_tmp.rename(columns=format_snake_case_to_human_upper_case)
        html_invoice_details_table = dataframe_to_html_without_pandas_style(invoice_details_tmp)
        number_of_pages = int(html_invoice_details_table.count('<tr>') / 37) + 1
        html_template = html_template.replace("{invoice_details_table}",html_invoice_details_table)
        path_to_pdf = f"{OUTPUT_FOLDER}/LoxInvoices/{company}/{language}/{bill_number}.pdf"
        safe_mkdir(path_to_pdf)
        print(f"Generating the pdf ({number_of_pages} pages) in {path_to_pdf} ...")  
        generate_pdf_file_from_html_css(
            BILLING_ASSETS_FOLDER,
            html_template,
            style_path,
            path_to_pdf
        )
        size = get_file_size(path_to_pdf)
        print_success(f"{bill_number}.pdf ({size[0]} {size[1]}) created - {language}")
        
        # Generate the csv locally
        if country == language:
            csv_invoice_file_path = path_to_pdf.replace(".pdf", ".csv")
            populate_details_with_credit_way(invoice_details).to_csv(csv_invoice_file_path, index=False)
            print_success("CSV generated successfully.")
        
        paths_to_pdfs.append(path_to_pdf)
        
        print("Saving in Google Cloud Storage...")
        store_lox_invoice(company, language, path_to_pdf)
    
    return paths_to_pdfs


def main(*,
    company: str,
    bill_number: str,
    **_
) -> List[str]:
    """Orchestrates the creation of billing documents (csv and pdf) for the given company by:
        - Populating the database with the billing details.
        - Updating the Refunds table with the bill numbers.
        - Generating the billing documents.
        
        # Keyword Arguments
        - `company`: The company name.
        - `bill_number`: The bill number.
        
        # Returns
        - A list of paths to the generated pdfs.
    """
    print("Populating the database with the billing details...")
    number_of_billed_row = _populate_bill_details(company, bill_number)
    if number_of_billed_row == 0:
        return []
    
    update_credited_packages_with_bill_number(company, bill_number)
    
    print("Generating the billing documents, and saving them to Google Cloude Storage...")
    return generate_and_store_bill_documents(company, bill_number)

