"""All queries to get data about invoicing information."""
from pandas import DataFrame

from lox_services.persistence.database.query_handlers import select


def get_invoicing_details(company: str) -> DataFrame:
    """Returns invoicing details for a company."""
    sql_query = f"""
        SELECT *
        FROM LoxData.Invoicing invoicing
        WHERE company = "{company}"
    """
    return select(sql_query, False).loc[0]
