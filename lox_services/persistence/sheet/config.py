"""All necessary functions to create a google sheet client instance."""
import os
import gspread
import pandas as pd
from typing import List
from gspread.client import Client
from gspread_dataframe import get_as_dataframe
from lox_services.config.paths import ROOT_PATH


def get_google_sheet_client(
    scopes: List[str] = ["https://www.googleapis.com/auth/drive"],
) -> Client:
    """Returns the google sheet client already configured with a service account"""
    google_sheet_client = gspread.service_account(
        filename=os.path.join(
            ROOT_PATH,
            "Algorithms/Utils/GoogleSheet/lox-google-sheet_service_account.json",
        ),
        scopes=scopes,
    )
    return google_sheet_client


def get_first_sheet_dataframe(spreadsheet: Client) -> pd.DataFrame:
    origin_df: pd.DataFrame = get_as_dataframe(spreadsheet.sheet1)
    return origin_df
