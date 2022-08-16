"""Stats on Lox invoices"""
from lox_services.persistence.database.query_handlers import select

sql_query = """
    SELECT 
        DATE_TRUNC(d.invoice_date, MONTH) AS month,
        d.company,
        round(sum(due_amount),2) AS total
    FROM LoxData.InvoicesDetails i
        INNER JOIN LoxData.DueInvoices d
            ON i.invoice_number = d.invoice_number
    GROUP BY month, company
    ORDER BY month desc
"""

data = select(sql_query)
