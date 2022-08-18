from datetime import datetime
from typing import List

from pandas import DataFrame

from lox_services.persistence.database.query_handlers import select


def select_all_non_credited_refunds_from_tracking_number_list(tracking_numbers: List[str], carrier: str, company: str) -> DataFrame:
    """get all the the tracking_number that are not marked as credited in database from a tracking_number list, the carrier and the company"""
    select_query = f"""
        SELECT * FROM TestEnvironment.Refunds_copy
        WHERE tracking_number in UNNEST({tracking_numbers})
            AND carrier = "{carrier}"
            AND company = "{company}"
            AND state != "CREDITED"
        """
    return select(select_query)


def select_refunds_by_tracking_numbers(company: str, carrier: str, tracking_numbers: List[str]):
    """Selects refunds by tracking number."""
    query_string = f"""
        SELECT DISTINCT 
            tracking_number
        
        FROM InvoicesData.Refunds
        
        WHERE tracking_number IN UNNEST({tracking_numbers})
            AND carrier = "{carrier}"
            AND company = "{company}"
    """
    return select(query_string)
