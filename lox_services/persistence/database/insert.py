"""Contains the function to insert dataframes into the database."""
from datetime import datetime
from pprint import pprint
from pytz import timezone
import os
from sys import path

import numpy as np
import pandas as pd
from google.cloud.bigquery import Client

from lox_services.persistence.config import SERVICE_ACCOUNT_PATH
from lox_services.persistence.database.datasets import (
    InvoicesData_dataset,
    InvoicesDataLake_dataset,
    LoxData_dataset, Mapping_dataset,
    TestEnvironment_dataset,
    DatasetTypeAlias,
    UserData_dataset)
from lox_services.persistence.database.query_handlers import select
from lox_services.persistence.database.utils import generate_id
from lox_services.utils.general_python import print_error, print_success
from lox_services.persistence.database.exceptions import InvalidDataException
# pylint: disable=line-too-long

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.path.join(SERVICE_ACCOUNT_PATH)

def insert_dataframe_into_database(dataframe: pd.DataFrame, table: DatasetTypeAlias):
    """Inserts every row of the dataframe into the database. 
        Does duplicate checks for specific tables (Invoices, Refunds).
        ## Arguments
        - `dataframe`: The dataframe to insert into the database. Must have good column names.
        - `table`: The database table name. It must be one of the datasets.
        
        ## Example
            >>> insert_dataframe_into_database(df, InvoicesData_dataset.Invoices)
        
        ## Returns 
        - The number of inserted rows.
        - An Exception if a check didn't pass. 
    """
    dataset = ""
    if not isinstance(dataframe, pd.DataFrame):
        print_error('dataframe argument must be a DataFrame.')
        return 0
    
    print(f"Trying to save a dataframe ({dataframe.shape[0]} rows) to Google BigQuery table {table.name}")
    if not dataframe.empty:
        if isinstance(table, InvoicesData_dataset):
            dataset = "InvoicesData"
            dataframe = remove_duplicate_headers_dataframe(dataframe)
            if table.name == "Invoices":
                dataframe = remove_duplicate_invoices(dataframe)
            if table.name == "Refunds":
                dataframe = remove_duplicate_refunds(dataframe)
            if table.name == "ClientInvoicesData":
                dataframe = remove_duplicate_client_invoice_data(dataframe)
        elif isinstance(table, LoxData_dataset):
            dataset = "LoxData"
            if table.name == "DueInvoices":
                check_lox_invoice_not_exists(dataframe)
            if table.name == "InvoicesDetails":
                check_duplicate_invoices_details(dataframe)
        elif isinstance(table, Mapping_dataset):
            dataset = "Mapping"
        elif isinstance(table, InvoicesDataLake_dataset):
            dataset = "InvoicesDataLake"
        elif isinstance(table, UserData_dataset):
            dataset = "UserData"
        elif isinstance(table, TestEnvironment_dataset):
            dataset="TestEnvironment"
            if table.name == "Refunds":
                dataframe = prepare_refunds_test_enviromnent(dataframe)
                dataframe = remove_duplicate_refunds(dataframe, test_environment = True)
        else :
            raise TypeError("'table' param must be an instance of one of the tables Enum.")
    
    if not dataframe.empty:
        print_success(f"Checks done - Saving dataframe ({dataframe.shape[0]} rows) to Google BigQuery table {table.name}")
        bigquery_client = Client()
        # Prepares a reference to the dataset
        dataset_ref = bigquery_client.dataset(dataset)
        # Select the table where you want to push the data
        table_ref = dataset_ref.table(table.name)
        table = bigquery_client.get_table(table_ref)
        dataframe = dataframe.where(pd.notnull(dataframe), None)
        current_datetime = datetime.now(timezone('Europe/Amsterdam')).strftime('%Y-%m-%dT%H:%M:%S.%f')
        if 'insert_datetime' not in dataframe.columns:
            dataframe['insert_datetime'] = current_datetime
        else:
            dataframe['insert_datetime'] = dataframe['insert_datetime'].astype(str)
        dataframe['update_datetime'] = current_datetime
        errors = bigquery_client.insert_rows_from_dataframe(
            table=table, 
            dataframe=dataframe,
            ignore_unknown_values=True,
        )[0]
        
        if len(errors) > 0:
            pprint(errors)
            raise InvalidDataException(f"{len(errors)} errors occured while inserting dataframe into {table}.")
        
        print_success("Success, everything has been inserted.")
    else:
        print("Empty dataframe, insert aborted because unnecessary.")
    
    return dataframe.shape[0]


def prepare_refunds_test_enviromnent(dataframe: pd.DataFrame) -> pd.DataFrame:
    """"Prepare the refunds to be push on the new environment:
        ## Arguments
        - `dataframe`: The dataframe containing the invoice numbers to check.
        
        ## Example
            >>> prepare_refunds_test_enviromnent(df)
        
        ## Returns 
        - The dataframe ready to be pushed
    """
    if 'package_id' not in dataframe.columns:
        if 'invoice_number' in dataframe.columns:
            dataframe['package_id'] =  dataframe.apply(lambda x: generate_id([x.carrier, x.company, x.invoice_number, x.tracking_number]), axis=1)
        else:
            dataframe['package_id'] =  dataframe.apply(lambda x: generate_id([x.carrier, x.company, "null", x.tracking_number]), axis=1)
    dataframe['request_amount'] = dataframe['total_price']
    return dataframe


def remove_duplicate_invoices(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Removes invoices that have already been saved in the database.
        ## Arguments
        - `dataframe`: The dataframe containing the invoice numbers to check.
        
        ## Example
            >>> remove_duplicate_invoices(df)
        
        ## Returns 
        - The dataframe without the invoice numbers already uploaded.
    """
    original_size = dataframe.shape[0]
    dataframe['invoice_number'] = dataframe["invoice_number"].astype(str)
    company = dataframe.iloc[0]['company']
    carrier = dataframe.iloc[0]['carrier']
    query = f"""
        SELECT DISTINCT invoice_number 
        
        FROM InvoicesData.Invoices
        
        WHERE carrier = "{carrier}"
            AND company = "{company}"
            AND invoice_number IN UNNEST({dataframe['invoice_number'].unique().tolist()})
    """
    already_pushed = select(query)
    # Remove invoice numbers that were already pushed to BQ
    dataframe = dataframe[~(dataframe['invoice_number']).isin(already_pushed['invoice_number'])]
    
    print(f"{original_size - dataframe.shape[0]} invoice rows deleted before saving to the database.")
    print("Result:\n", dataframe)
    return dataframe


def remove_duplicate_refunds(dataframe: pd.DataFrame, test_environment: bool = False) -> pd.DataFrame:
    """Removes rows for which the package has already a refund for the same reason, or one related (Lost & Damaged). 
        Removes duplicates in the dataframe as well.
        ## Arguments
        - `dataframe`: refunds dataframe that needs to be checked.
        
        ## Example
            >>> remove_duplicate_refunds(refunds_df)
        
        ## Returns
        The dataframe cleaned from potential duplicates
    """
    original_size = dataframe.shape[0]
    print(f"Checking {original_size} refunds...")
    #Drop duplicates for dummy duplicates, with 'keep' different than False
    dataframe = dataframe.copy().drop_duplicates(subset=['tracking_number','reason_refund'])
    print(dataframe.iloc[0])
    carrier = dataframe.iloc[0]['carrier']
    company = dataframe.iloc[0]['company']
    dataframe['reason_refund'] = dataframe.reason_refund.astype(str)
    reason_refunds = dataframe['reason_refund'].unique().tolist()
    
    if test_environment:
        dataframe['package_id'] = dataframe.package_id.astype(str)
        package_ids = dataframe['package_id'].tolist()
        query = f"""
        SELECT DISTINCT 
            package_id || CASE 
                WHEN reason_refund = 'Lost' OR reason_refund = 'Damaged' 
                    THEN 'Lost or Damaged' 
                    ELSE reason_refund 
                END 
            AS existing_combo
        
        FROM TestEnvironment.Refunds refunds
        
        WHERE package_id IN UNNEST({package_ids})
            AND reason_refund IN UNNEST({reason_refunds})
        """
        print(query)
        existing_data_dataframe = select(query)
        #Lost or damaged trick
        dataframe["smart_reason_refund"] = dataframe["reason_refund"].apply(lambda x: 'Lost or Damaged' if x in ('Lost','Damaged') else x)
        #Duplicate check
        dataframe = dataframe.drop_duplicates(
            subset=['tracking_number','smart_reason_refund'],
            keep=False
        )
        # Remove rows where the tracking number and reason refund is already present in the database
        dataframe = dataframe[~(dataframe['package_id'] + dataframe['smart_reason_refund']).isin(existing_data_dataframe['existing_combo'])]
    else:
        dataframe['tracking_number'] = dataframe.tracking_number.astype(str)
        tracking_numbers = dataframe['tracking_number'].tolist()
        query = f"""
        SELECT DISTINCT 
            tracking_number || CASE 
                WHEN reason_refund = 'Lost' OR reason_refund = 'Damaged' 
                    THEN 'Lost or Damaged' 
                    ELSE reason_refund 
                END 
            AS existing_combo
        
        FROM InvoicesData.Refunds
        
        WHERE company = "{company}"
            AND carrier = "{carrier}"
            AND tracking_number IN UNNEST({tracking_numbers})
            AND reason_refund IN UNNEST({reason_refunds})
        """
        print(query)
        existing_data_dataframe = select(query)
        #Lost or damaged trick
        dataframe["smart_reason_refund"] = dataframe["reason_refund"].apply(lambda x: 'Lost or Damaged' if x in ('Lost','Damaged') else x)
        #Duplicate check
        dataframe = dataframe.drop_duplicates(
            subset=['tracking_number','smart_reason_refund'],
            keep=False
        )
        # Remove rows where the tracking number and reason refund is already present in the database
        dataframe = dataframe[~(dataframe['tracking_number'] + dataframe['smart_reason_refund']).isin(existing_data_dataframe['existing_combo'])]
    print(f"{original_size - dataframe.shape[0]} refund rows deleted before saving to the database.")
    print("Result:\n", dataframe)
    return dataframe


def remove_duplicate_client_invoice_data(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Removes duplicates from client invoices dataframe"""
    carrier = dataframe.iloc[0]['carrier']
    company = dataframe.iloc[0]['company']
    tracking_numbers = dataframe["tracking_number"].to_list()
    sql_query = f"""
        SELECT 
            tracking_number
        
        FROM InvoicesData.ClientInvoicesData
        
        WHERE company = "{company}"
            AND carrier = "{carrier}"
            AND tracking_number IN UNNEST({tracking_numbers})
    """
    already_saved_tracking_numbers = select(sql_query, False)["tracking_number"].to_list()
    if len(already_saved_tracking_numbers) > 0:
        dataframe = dataframe.loc[~dataframe["tracking_number"].isin(already_saved_tracking_numbers)]
    return dataframe


def check_lox_invoice_not_exists(dataframe: pd.DataFrame) -> None:
    """Check if the lox invoice number doesn't already exist in the database.
        ## Arguments
        - `dataframe`: The dataframe containing the lox invoice number to check.
        
        ## Example
            >>> check_lox_invoice_not_exists(df)
        
        ## Returns 
        - Nothing if the check is successful.
        - Raises Exception otherwise.
    """
    invoice_number = dataframe.iloc[0]['invoice_number']
    query = f"""
        SELECT 
            invoice_number 
        
        FROM LoxData.DueInvoices
        
        WHERE invoice_number = "{invoice_number}"
    """
    already_saved = select(query,False)
    if already_saved.shape[0] > 0:
        print_error(f"The Lox invoice number {invoice_number} has already been attributed!")
        raise Exception("Cannot save in the Database. Lox invoice number has already been attributed.")
    else:
        print_success("Due Invoices checks are good.")


def check_duplicate_invoices_details(dataframe: pd.DataFrame) -> None:
    """Check if the invoices details have not already been added.
        ## Arguments
        - `dataframe`: The dataframe containing the invoices details.
        
        ## Example
            >>> check_duplicate_invoices_details(df)
        
        ## Returns 
        - Nothing if the check is successful.
        - Raises Exception otherwise.
    """
    invoice_numbers = list(set(dataframe["invoice_number"].to_list()))
    if len(invoice_numbers) > 1: #We do this to have a better handle over the check
        raise Exception("Cannot save the details for more than one invoice_number.")
    else:
        invoice_number = invoice_numbers[0]
        
    descriptions = tuple(dataframe['description'])
    if len(descriptions) == 1:
        descriptions = str(descriptions).replace(",","")
    query_string = f"""
        SELECT 
            invoice_number 
        
        FROM LoxData.InvoicesDetails
        
        WHERE invoice_number = "{invoice_number}"
            AND description IN {descriptions}
    """
    already_saved = select(query_string, False)
    if not already_saved.empty:
        print_error("These invoices details have already been saved!")
        raise Exception("Cannot save in the Database. Invoices details have already been saved.")
        
    print_success("Invoices details checks are good.")


def remove_duplicate_headers_dataframe(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Removes rows that are similar to the header and are not in the first line of the given dataframe
        ## Arguments
        - `dataframe`: dataframe that needs to be checked.
        
        ## Example
            >>> remove_duplicate_headers_dataframe(refunds_df)
        
        ## Returns
        The dataframe cleaned from potential header duplicates
    """
    for index, row in dataframe.iterrows():
        # If the entire row is similar to the header
        if np.array_equal(row.values, dataframe.columns.values):
            # Remove the row from the dataframe
            dataframe.drop(index, inplace=True)
            
    return dataframe


def remove_duplicate_headers_csv_file(csv_path: path) -> None:
    """Removes rows from the file if they are similar to the header and are not the header
        ## Arguments
        - `file`: path to the file csv that needs to be checked
        
        ## Example
            >>> remove_duplicate_headers_csv_file(csv_path)
    """
    # Save the header values
    header = open(csv_path,'r').readlines()[0]
    # Get all lines that are after the header
    all_lines = open(csv_path,'r').readlines()[1:]
    # Open the file in write mode ( delete the content )
    f = open(csv_path,'w')
    # Write the header in the empty file
    f.write(header)
    # Write all the following rows if they are diferent than the header
    for line in all_lines:
        if header != line:
            f.write(line)