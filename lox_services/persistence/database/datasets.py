"""Contains all datasets of the database"""
import os
from enum import Enum
from typing import Union

from google.cloud.bigquery import Client

from lox_services.persistence.config import SERVICE_ACCOUNT_PATH

class InvoicesData_dataset(Enum):
    "Class that represents the classes present in InvoicesData dataset"
    ClientInvoicesData = "ClientInvoicesData"
    ContractData = "ContractData"
    Deliveries = "Deliveries"
    DeliverySLAs = "DeliverySLAs"
    Invoices = "Invoices"
    InvoicesSave = "InvoicesSave"
    Refunds = "Refunds"


class InvoicesDataLake_dataset(Enum):
    "Class that represents the classes present in InvoicesDataLake dataset"
    UPS_DataLake = "UPS_DataLake"
    DHL_DataLake = "DHL_DataLake"


class LoxData_dataset(Enum):
    "Class that represents the classes present in LoxData dataset"
    DueInvoices = "DueInvoices"
    Invoicing = "Invoicing"
    InvoicesDetails = "InvoicesDetails"
    Targets = "Targets"


class UserData_dataset(Enum):
    "Class that represents the classes present in UserData dataset"
    Users = "Users"
    UsersActivity = "UsersActivity"
    CustomerSatisfaction = "CustomerSatisfaction"
    CustomerData = "CustomerData"
    Credentials = "Credentials"
    ChronopostAccounts = "ChronopostAccounts"


class Mapping_dataset(Enum):
    "Class that represents the classes present in Mapping dataset"
    StatusMapping = "StatusMapping"


class TestEnvironment_dataset(Enum):
    "Class that represents the classes present in TestEnvironment dataset"
    Packages = "Packages"
    Package_charges = "Package_charges"
    Invoices = "Invoices"
    Locations = "Locations"
    Dimensions = "Dimensions"
    Statuses = "Statuses"
    Delivery_steps = "Delivery_steps"
    Service_level_agreements = "Service_level_agreements"
    Refunds = "Refunds"
    Refunds_copy = "Refunds_copy"

def get_big_query_datasets():
    "Function that fetches all the datasets present in BigQuery"
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.path.join(SERVICE_ACCOUNT_PATH)
    client = Client()
    return list(client.list_datasets())


def get_data_lake_table_with_carrier(carrier : str) -> str:
    """Returns the table corresponding to the specified carrier."""
    for table in InvoicesDataLake_dataset:
        if carrier + "_DataLake" == table.value:
            return table


DatasetTypeAlias = Union[
    InvoicesData_dataset,
    Mapping_dataset,
    LoxData_dataset,
    UserData_dataset,
    TestEnvironment_dataset,
    InvoicesDataLake_dataset
]