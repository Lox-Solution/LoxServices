from typing import List

import pandas as pd

from lox_services.persistence.database import query_handlers


def select_all_carrier_invoices_information(company: str, carrier: str) -> pd.DataFrame:
    """Get all the information about the invoices dropped by clients 
        ## Arguments
        - `company`: The name of the company being ran.
        - `carrier`: The name of the carrier being ran.
        
        ## Example
            >>> select_all_carrier_invoices_information("Company","Chronopost")
        
        ## Returns
            >>> the dataframe containing the information.
    """
    query_string = f"""
        SELECT  *
        
        FROM UserData.DroppedFiles
        
        WHERE company = "{company}"
            AND carrier = "{carrier}"
            AND is_carrier_invoice = True
        """
    return query_handlers.select(query_string)

    