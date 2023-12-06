import re
import pandas as pd

from lox_services.persistence.database.exceptions import MissingColumnsException
from lox_services.persistence.storage.constants import INVOICE_BASE_URL


def client_invoice_data_quality_check(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Performs data quality check on client invoices dataframe"""
    missing_columns = list(
        {
            "company",
            "carrier",
            "tracking_number",
            "data_source",
            "is_original_invoice",
            "quantity",
            "net_amount",
        }.difference(set(dataframe.columns))
    )
    if missing_columns:
        raise MissingColumnsException(", ".join(missing_columns))

    if "invoice_url" in dataframe.columns:
        # Check value invoice_url
        for invoice_url in dataframe["invoice_url"].to_list():
            if not pd.isna(invoice_url) and not re.match(
                r"(https://storage.cloud.google.com).*", invoice_url
            ):
                raise ValueError(f"invoice_url has to start by {INVOICE_BASE_URL}")

    # Check value is_original_invoice
    is_original_invoice_wrong_values = dataframe[
        ~dataframe["is_original_invoice"].isin([True, False])
    ]
    if not is_original_invoice_wrong_values.empty:
        wrong_values = (
            is_original_invoice_wrong_values["is_original_invoice"].unique().tolist()
        )
        raise ValueError(
            f"Incorrect values {wrong_values} for field is_original_invoice. Only True or False are authorized"
        )

    dataframe["quantity"] = pd.to_numeric(dataframe["quantity"])
    dataframe["net_amount"] = pd.to_numeric(dataframe["net_amount"])
    dataframe = dataframe.loc[~(dataframe["quantity"] < 0)]
    dataframe.loc[dataframe["quantity"] == 0, "quantity"] = 1
    dataframe.loc[dataframe["net_amount"] == 0, "net_amount"] = 1
    
    # If the original currency and amount are not set, set them to EUR
    if "original_currency_code" not in dataframe.columns:
        dataframe["original_currency_code"] = "EUR"
    if "original_net_amount" not in dataframe.columns:
        dataframe["original_net_amount"] = dataframe["net_amount"]
    
    return dataframe
