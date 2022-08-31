import pandas as pd
from gspread.client import Client
from gspread.exceptions import SpreadsheetNotFound
from gspread.models import Spreadsheet
from gspread_dataframe import get_as_dataframe

from lox_services.persistence.sheet.config import get_google_sheet_client


def create_spreadsheet(gc: Client, *, name: str) -> Spreadsheet:
    """Creates a google sheet and share it automaticaly with loxteam@loxsolution.com as owner"""
    print(f"Creating spreadsheet {name} ...")
    spread_sheet = gc.create(name)
    spread_sheet.share(
        'loxteam@loxsolution.com',
        perm_type='user',
        role='writer'
    )
    print("Done.")
    return spread_sheet
