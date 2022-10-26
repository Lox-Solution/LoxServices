import pandas as pd
from gspread.client import Client
from gspread.models import Spreadsheet

from lox_services.config.constants import LOX_TEAM_EMAIL


def create_spreadsheet(gc: Client, *, name: str) -> Spreadsheet:
    """Creates a google sheet and share it automaticaly with loxteam@loxsolution.com as owner"""
    print(f"Creating spreadsheet {name} ...")
    spread_sheet = gc.create(name)
    spread_sheet.share(
        LOX_TEAM_EMAIL,
        perm_type='user',
        role='writer'
    )
    print("Done.")
    return spread_sheet
