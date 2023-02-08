"""All functions to save invoice data into the database"""
import os
from enum import Enum
from typing import List, Tuple

import pandas as pd

from lox_services.persistence.database.datasets import InvoicesData_dataset
from lox_services.persistence.database.insert import insert_dataframe_into_database
from lox_services.persistence.database.schema import (
    dates_refunds,
    dtypes_deliveries,
    dtypes_invoices,
    dtypes_refunds,
    na_deliveries,
    na_invoices,
    na_refunds)
from lox_services.persistence.database.utils import format_time, format_datetime, replace_nan_with_none_in_dataframe
from lox_services.utils.enums import Files


def push_run_to_database(run_output_folder, carrier, company, account_number_input: str = "") -> dict:
    """Add to the database all the important files of the given folder.
        Returns a dictionary reporesenting the run report.
        ## Arguments        
        - `run_output_folder`: The output folder that contains files that we will push
        - `carrier_input`: The carrier that was run as a result of the given output folder        
        - `company_input`: The company that was run as a result of the given output folder        
        - `account_number_input` : the account_number that was run, REQUESTED for colissimo
        
        ## Returns
            - A report of the inserted files.
        
        ## Example        
            >>> report = push_run_to_database(output_folder, "UPS")
    """
    if account_number_input == "" and carrier=="Colissimo":
        raise Exception("Account number need to be put in the function's parameters")
    
    if account_number_input != "" and carrier!="Colissimo":
        account_number_input = ""
    
    date_format = "YYYY-MM-DD"
        
    list_files_to_push: List[Tuple[pd.DataFrame, Enum]] = []
    
    invoice_path = os.path.join(run_output_folder, Files.INVOICES.value)
    if os.path.exists(invoice_path):
        #Read the invoice file and check the datetime format
        df_invoice: pd.DataFrame = pd.read_csv(invoice_path, infer_datetime_format = date_format, header=0,dtype={"postal_code_reciever" : str})
        if df_invoice.shape[0] > 0:
            #If some columns are missing, add the columns with None values
            for column in dtypes_invoices:
                if column not in df_invoice.columns:
                    df_invoice.loc[:,column] = None
            
            #"Make sure that the columns have the good type
            df_invoice = df_invoice.fillna(value=na_invoices).astype(dtypes_invoices)
            
            list_files_to_push.append(
                (df_invoice,  InvoicesData_dataset.Invoices)
            )
    
    # Prepare deliveries data
    deliveries_path = os.path.join(run_output_folder,account_number_input, Files.DELIVERIES.value)
    if os.path.exists(deliveries_path):
        #Read the delivery file and check the datetime format
        df_deliveries: pd.DataFrame = pd.read_csv(
            deliveries_path,
            converters= dtypes_deliveries,
            infer_datetime_format = date_format,
            header=0
        )
        if df_deliveries.shape[0] > 0:
            for column in dtypes_deliveries:
                if column not in df_deliveries.columns:
                    df_deliveries.loc[:,column] = None
            
            #Format time
            if "date_time" not in df_deliveries.columns:
                df_deliveries.loc[:,'time'] = df_deliveries['time'].apply(format_time)
                df_deliveries.loc[:,'date_time'] = df_deliveries.apply(lambda x: format_datetime(x['date'], x['time']), axis=1)
            df_deliveries = df_deliveries.fillna(value=na_deliveries).astype(dtypes_deliveries)
            
            
            list_files_to_push.append(
                (df_deliveries, InvoicesData_dataset.Deliveries),
            )
            
        
    refunds_path = os.path.join(run_output_folder, account_number_input,Files.REFUNDS.value)
    # Prepare refunds data
    if os.path.exists(refunds_path):
        #Read the refund file and check the datetime format
        df_refund: pd.DataFrame = pd.read_csv(refunds_path, infer_datetime_format = date_format, header=0)
        if df_refund.shape[0] > 0:
            #If some columns are missing, add the columns with None values
            for column in dtypes_refunds:
                if column not in df_refund.columns:
                    print(column)
                    df_refund.loc[:,column] = None
            
            #"Make sure that the columns have the good type
            df_refund = df_refund.fillna(value=na_refunds).astype(dtypes_refunds)
            
            for column in dates_refunds:
                df_refund[column] = df_refund[column].apply(lambda x: x if x!="" else None)

            list_files_to_push.append(
                (df_refund,  InvoicesData_dataset.Refunds)
            )
    
    
    report = {}
    for dataframe, table in list_files_to_push:
        dataframe = replace_nan_with_none_in_dataframe(dataframe)
        number_inserted_rows = insert_dataframe_into_database(dataframe = dataframe, table = table) # API request
        report[table.name] = number_inserted_rows
    
    print("report:\n", report)
    return report
