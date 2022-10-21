import datetime
from typing import List, Union

from google.cloud.bigquery.job import QueryJob
from pandas import DataFrame

from lox_services.persistence.database.query_handlers import (
    raw_query,
    select,
    update)


def get_current_max_invoice_number() -> int:
    """Select the max lox invoice number from the database.
        ## Example 
            >>> get_current_max_invoice_number() # 0000-0471 in the database
            >>> # returns 471 
    """
    query = """
        SELECT 
            distinct REPLACE( invoice_number, "-", "") AS number
        
        FROM LoxData.DueInvoices
        
        ORDER BY 1 DESC
        LIMIT 1
        """
    return int(select(query)["number"][0])


def get_signed_companies_with_credits_not_billed(min_invoicing_amount: int) -> DataFrame:
    """Gets the signed companies that have credits in the database with no lox invoice number."""
    query_string = f"""
        WITH companies as(
            SELECT
                refunds.company AS company,
                ROUND(SUM(refunds.total_price),2) AS total_credit
            
            FROM InvoicesData.Refunds REFUNDS
                INNER JOIN LoxData.Invoicing invoicing
                    ON refunds.company = invoicing.company
            
            WHERE credit_date IS NOT NULL
                AND COALESCE(is_lox_claim, True)
                AND lox_invoice_number is null
                AND invoicing.is_signed = true
                
            GROUP BY company
        )
        
        SELECT 
            company
        
        FROM companies
        
        WHERE total_credit > {min_invoicing_amount}
            OR company = "Helloprint"
        
        ORDER BY company
    """
    return select(query_string)


def get_due_invoices_companies_by_month(invoice_date: datetime.date) -> DataFrame:
    """Get the companies and associated invoice numbers for the month of the given invoice date."""
    query_string = f"""
        SELECT
            company,
            invoice_number,
            status,
            invoice_date
        
        FROM LoxData.DueInvoices
        
        WHERE DATE_TRUNC(invoice_date, MONTH) = DATE_TRUNC("{invoice_date}", MONTH)
        
        ORDER BY invoice_number DESC, company
    """ 
    return select(query_string)


def get_company_details_from_invoice_number(invoice_number: str) -> DataFrame:
    """Get company details from the database with an invoice number"""
    query_string = f"""
        SELECT 
            invoicing.company as company_name,
            account_number,
            CASE
                WHEN invoice_company_name IS NULL 
                THEN invoicing.company
                ELSE invoice_company_name
            END AS customer_name,
            COALESCE(street_name,"") AS customer_street,
            COALESCE(vat_number,"") AS customer_vat_number,
            COALESCE(zip_code,"") AS customer_zip_code,
            COALESCE(city_name,"") AS customer_city,
            COALESCE(country_name,"") AS customer_country,
            COALESCE(department,"") AS customer_department,
            invoice_date,
            CAST(
                DATE_ADD(invoice_date, INTERVAL payment_term DAY) 
            as STRING) AS invoice_due_date,
            vat,
            country,
            siret
            
        FROM LoxData.Invoicing invoicing
            INNER JOIN LoxData.DueInvoices due_invoices 
                ON due_invoices.company = invoicing.company
        
        WHERE due_invoices.invoice_number = "{invoice_number}"
    """
    return select(query_string, False)


def get_company_details(company: str)-> DataFrame:
    """Gets the company details stored in the LoxData.Invoicing table for the given company."""
    sql_query = f"""
        SELECT *
        
        FROM LoxData.Invoicing
        
        WHERE company = "{company}"
    """
    all_details = select(sql_query)
    if all_details.shape[0] != 1:
        raise Exception(f"The company details for {company} are wrong.")
    
    return all_details.loc[0]


def get_invoice_summary(invoice_number: str) -> DataFrame:
    """Get the invoice summary from the database."""
    print("Getting invoice summary...")
    query_string = f"""
        SELECT 
            distinct description AS reason,
            orders AS quantity,
            saved_amount AS saved_amount,
            due_amount AS due_amount
        
        FROM LoxData.InvoicesDetails details
            INNER JOIN LoxData.DueInvoices due_invoices
                ON details.invoice_number  = due_invoices.invoice_number
        
        WHERE due_invoices.invoice_number = "{invoice_number}"
        
        ORDER BY 
            SPLIT(reason,"-")[offset(0)] DESC,
            saved_amount DESC
    """
    return select(query_string, False)


def get_invoice_details(invoice_number: str) -> DataFrame:
    """Get invoice details from the database."""
    print("Getting invoice details...") 
    query_string = f"""
        SELECT DISTINCT 
            carrier,
            reason_refund,
            tracking_number,
            CAST(refunds.invoice_date as STRING) AS invoice_date,
            CAST(credit_date as STRING) AS credit_date,
            COALESCE(credit_invoice_number, refunds.invoice_number) AS credit_invoice_number,
            ROUND(total_price, 2) AS saved_amount,
            CAST(ROUND((invoicing.success_fee_refund/100) * 100, 0) as STRING) || "%" AS fee,
            ROUND(total_price * (invoicing.success_fee_refund/100), 2) AS due_amount
            
        FROM LoxData.InvoicesDetails details
            INNER JOIN LoxData.DueInvoices invoices
                ON details.invoice_number = invoices.invoice_number
            INNER JOIN LoxData.Invoicing invoicing
                ON invoices.company = invoicing.company
            INNER JOIN InvoicesData.Refunds refunds
                ON invoices.invoice_number = refunds.lox_invoice_number
        
        WHERE invoices.invoice_number = "{invoice_number}"
            AND refunds.total_price > 0
        
        ORDER BY 
            refunds.carrier,
            invoice_date DESC,
            credit_date DESC,
            credit_invoice_number,
            refunds.reason_refund,
            saved_amount DESC
    """
    return select(query_string, False)


def update_credited_packages_with_bill_number(company: str, invoice_number: str) -> DataFrame:
    """Updates all the credited packages of the previous month for a company with the given invoice_number.
        The account number 000029130R is skipped because it is an edge case (ask Melvil about it).
    """
    invoiced_refunds_query_string = f"""
        UPDATE InvoicesData.Refunds
        
        SET 
            update_datetime = CURRENT_DATETIME('Europe/Amsterdam'),
            lox_invoice_number = "{invoice_number}"
        
        WHERE
            state = "CREDITED"
            AND company = "{company}"
            AND lox_invoice_number IS NULL
            AND COALESCE(is_lox_claim, True)
            AND credit_date IS NOT NULL
            AND tracking_number NOT IN (
                SELECT distinct tracking_number 
                FROM InvoicesData.Invoices invoices
                WHERE account_number = "000029130R"
                AND carrier = "UPS"
                AND tracking_number is not NULL
            )
    """
    return update(invoiced_refunds_query_string)


def get_detailed_billed_amount(company: str, invoice_number: str) -> DataFrame:
    """Gets the due amount per category for the last month.
        One category can correspond to either the Dashboarding, or the Refund product (per carrier and reason_refund)
    """
    query_string = f"""
        SELECT
            refunds.company as company,
            success_fee_refund,
            "Refunds: " || refunds.carrier || " - " || reason_refund AS description,
            COALESCE(ROUND(SUM(saved_amount), 2),0) AS saved_amount,
            COALESCE(ROUND(SUM(due_amount), 2),0) AS due_amount,
            COUNT(DISTINCT tracking_number) AS orders
        
        FROM (
            SELECT
                refunds.company,
                success_fee_refund,
                carrier,
                refunds.reason_refund,
                refunds.tracking_number,
                refunds.lox_invoice_number,
                ROUND(total_price, 2) AS saved_amount,
                CASE
                    WHEN refunds.invoice_date BETWEEN invoicing.start_trial_period AND invoicing.end_trial_period
                    THEN 0
                    ELSE ROUND(total_price * (invoicing.success_fee_refund/100), 2) 
                END AS due_amount
            FROM InvoicesData.Refunds refunds
            INNER JOIN LoxData.Invoicing AS invoicing
                ON invoicing.company = refunds.company
            WHERE
                state = "CREDITED"
                AND (refunds.lox_invoice_number IS NULL OR 
                    refunds.lox_invoice_number = "{invoice_number}")
                AND invoicing.is_signed = TRUE
                AND credit_date IS NOT NULL
                AND refunds.company = "{company}"
                AND COALESCE(is_lox_claim, True)
                AND tracking_number NOT IN (
                    SELECT distinct tracking_number 
                    FROM InvoicesData.Invoices invoices
                    WHERE account_number = "000029130R"
                    AND carrier = "UPS"
                    AND tracking_number is not NULL
                )
                AND total_price > 0
        ) AS refunds
        
        GROUP BY
            company,
            success_fee_refund,
            description
    
    UNION ALL
    
        SELECT
            invoices.company AS company,
            success_fee_refund,
            "Dashboarding - " || invoicing.dashboard_price||"€ per package" AS description,
            NULL AS saved_amount,
            ROUND(COUNT(DISTINCT tracking_number) * MAX(invoicing.dashboard_price),2) AS due_amount,
            COUNT(DISTINCT tracking_number) AS orders
        
        FROM InvoicesData.Invoices invoices
            INNER JOIN LoxData.Invoicing AS invoicing
                ON invoicing.company = invoices.company
        
        WHERE invoices.company = "{company}"
            AND COALESCE(invoicing.dashboard_price, 0) > 0
            AND invoices.invoice_date BETWEEN
                DATE_TRUNC(DATE_SUB(CURRENT_DATE(), INTERVAL 1 MONTH),MONTH) AND
                DATE_TRUNC(CURRENT_DATE(),MONTH)
        
        GROUP BY
            company,
            success_fee_refund,
            description
    
    ORDER BY
        saved_amount DESC
    """
    return select(query_string, False)


def get_company_from_invoice_number(invoice_number: str) -> Union[str, None]:
    """Gets the  company for the given invoice number.
        If the invoice number is not attributed, then returns None.
    """
    sql_query = f"""
        SELECT company
        
        FROM LoxData.DueInvoices
        
        WHERE invoice_number = "{invoice_number}"
    """
    query_result = select(sql_query)
    if query_result.shape[0] == 0:
        return None
    
    return query_result.loc[0]["company"]


def delete_invoices_details(invoice_number: str) -> QueryJob:
    """Deletes all invoices details for the given invoice number."""
    delete_query = f"""
        DELETE FROM LoxData.InvoicesDetails
        
        WHERE invoice_number = "{invoice_number}"
    """
    return raw_query(delete_query)


def get_not_paid_invoices(month: datetime.date) -> DataFrame:
    """Gets the company and the corresponding invoice number for the given month.
        The invoice status must be "Not paid".
    """
    sql_query = f"""
        SELECT 
            company,
            invoice_number
        
        FROM LoxData.DueInvoices
        
        WHERE DATE_TRUNC(invoice_date, MONTH) = DATE_TRUNC("{month}", MONTH)
            AND status = "Not paid"
        
        ORDER BY invoice_number
    """
    return select(sql_query)


def update_invoice_to_sent(company: str, lox_invoice_number: str) -> None:
    """Updates the invoice status to "Sent" for the given company and invoice number."""
    sql_query = f"""
        UPDATE LoxData.DueInvoices
        
        SET 
            update_datetime = CURRENT_DATETIME('Europe/Amsterdam'),
            status = "Sent"
        
        WHERE company = "{company}"
            AND invoice_number = "{lox_invoice_number}"
    """
    return update(sql_query)


def set_is_not_lox_claim_for_tracking_numbers(company: str, lox_invoice_number: str, tracking_numbers: List[str]) -> DataFrame:
    """Updates the invoice number to NULL for the given company, invoice number, and tracking numbers."""
    sql_query = f'''
        UPDATE InvoicesData.Refunds
        
        SET 
            update_datetime = CURRENT_DATETIME('Europe/Amsterdam'),
            lox_invoice_number = null,
            is_lox_claim = false
        
        WHERE company = "{company}"
            AND lox_invoice_number = "{lox_invoice_number}"
            AND tracking_number IN UNNEST({tracking_numbers})
    '''
    return update(sql_query)


def update_invoice_date_to_today(company: str, bill_number: str) -> None:
    """Updates the invoice date to today for the given company and invoice number."""
    sql_query = f"""
        UPDATE LoxData.DueInvoices
        
        SET 
            update_datetime = CURRENT_DATETIME('Europe/Amsterdam'),
            invoice_date = CURRENT_DATE('Europe/Amsterdam')
        
        WHERE company = "{company}"
            AND invoice_number = "{bill_number}"
    """
    return update(sql_query)


def update_due_amount_with_fee(bill_number: str, new_fee: float) -> None:
    """Updates the due amount with the given fee for the given invoice number."""
    sql_query = f"""
        UPDATE LoxData.InvoicesDetails
        
        SET 
            update_datetime = CURRENT_DATETIME('Europe/Amsterdam'),
            due_amount = ROUND(saved_amount * {new_fee}, 2)
        
        WHERE invoice_number = "{bill_number}"
    """
    return update(sql_query)
