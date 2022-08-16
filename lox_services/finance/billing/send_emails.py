"""All functions to send Lox invoices by email."""
from datetime import date, datetime, timedelta
import os
import locale
from typing import List

import pandas as pd

from lox_services.config.paths import OUTPUT_FOLDER
from lox_services.email.send import send_emails_from_loxsolution_account
from lox_services.finance.billing.constants import BILLING_ASSETS_FOLDER, ACCOUNTANT_EMAIL, LOX_CC_EMAIL, LOX_FR_CC_EMAIL
from lox_services.persistence.database.queries.billing import get_not_paid_invoices, update_invoice_to_sent
from lox_services.persistence.database.queries.invoicing import get_invoicing_details
from lox_services.translation.enums import TranslationModules
from lox_services.translation.templates import insert_variables
from lox_services.translation.translate import get_translations
from lox_services.utils.general_python import print_error


def send_email_with_invoice_documents(
    *,
    company: str,
    bill_number: str,
    **_
):
    """
        - Sends the Lox invoices with the pdf as parameter to the company contact via email.
            The company `auto_email` attribute must be set to True.
        - Send a copy (cc) to one of Lox's CC emails depending on the language.
        - Sends a hidden copy (bcc) to the accountant.
        - The content is an html document.
        - The attachments are the pdf invoice and csv details.
    """
    billing_details = get_invoicing_details(company)
    auto_email = billing_details["auto_email"]
    if pd.isna(auto_email) or not auto_email:
        print(f"Skipping email sending for {company}")
        return None

    language: str = billing_details['country']
    translations = get_translations(language, TranslationModules.BILLING_EMAIL)
    locale.setlocale(locale.LC_TIME, translations["local_language"])
    month_date = datetime.today() - timedelta(days=31)
    month = (month_date).strftime("%B").capitalize()
    year = month_date.strftime("%Y")
    
    email_template_path  = os.path.join(BILLING_ASSETS_FOLDER, "email_template.html")
    with open(email_template_path, 'r') as file:
        email_html_template = file.read()
    
    style_sheet_path = os.path.join(BILLING_ASSETS_FOLDER, "email_style.css")
    with open(style_sheet_path, 'r') as file:
        email_css_style = file.read()
    
    translations_with_variables = insert_variables(
        translations,
        company= company,
        month= month,
        year= year,
        lox_invoice_number= bill_number
    )
    complete_html = insert_variables(
        { "html": email_html_template },
        **translations_with_variables
    )
    
    recipients: List[str] = list(map(
        lambda object: object["email_address"],
        billing_details["invoicing_emails"]
    ))
    subject = translations_with_variables["subject"]
    content = str(complete_html['html']).replace("<style></style>", f"<style>{email_css_style}</style>")
    
    cc_email_address = LOX_FR_CC_EMAIL if language == "FR" else LOX_CC_EMAIL
    bcc_email_address = ACCOUNTANT_EMAIL
    
    pdf_invoice_file_path: str = os.path.join(OUTPUT_FOLDER, "LoxInvoices", company, language, f"{bill_number}.pdf")
    csv_invoice_file_path = pdf_invoice_file_path.replace(".pdf", ".csv")
    
    try:
        print("Sending official email...")
        send_emails_from_loxsolution_account(
            sender_email_address="finance@loxsolution.com",
            receiver_email_addresses=recipients,
            subject=subject,
            content=content,
            attachments=[
                csv_invoice_file_path,
                pdf_invoice_file_path
            ],
            cc_email_addresses=[cc_email_address],
            bcc_email_addresses=[bcc_email_address],
        )
    
    except FileNotFoundError:
        print_error(f"Attachment not found, skip email sending failed for {company}.")
        return
    
    update_invoice_to_sent(company, bill_number) #TODO: This doesn't work if the bill has just been generated due to recent insertion


def manual_invoice_sending(month: date, skip_companies: List[str] = None, only_companies: List[str] = None):
    """Send manually invoices for a given month."""
    targets = get_not_paid_invoices(month)
    for _, row in targets.iterrows():
        company = row["company"]
        invoice_number = row["invoice_number"]
        if (
            (skip_companies is not None and company in skip_companies) or 
            (only_companies is not None and company not in only_companies)
        ):
            continue

        print(f"Sending bill {invoice_number} by email to {company}...")
        send_email_with_invoice_documents(
            company=company,
            bill_number=invoice_number,
        )
    
    return None

