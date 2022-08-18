"""All material needed to generate the update query."""
from typing import Tuple

import pandas as pd
from lox_services.config.paths import OUTPUT_FOLDER
from lox_services.persistence.database.datasets import TestEnvironment_dataset
from lox_services.persistence.database.insert import insert_dataframe_into_database
from lox_services.persistence.database.query_handlers import update
from lox_services.utils.general_python import print_success
from lox_services.persistence.database.queries.refunds import delete_refunds_for_tracking_numbers_and_reason_refund, select_all_non_credited_refunds_from_tracking_number_list, select_refunds_by_tracking_numbers

def _generate_set_field(row, where, set_and_where):
    """Generates the set field of a update SQL query"""
    result = ""
    for name, values in row.iteritems():
        if isinstance(values, str):
            # make sure that the value doesn't contains special characters
            values = values.replace('\n', ' ').replace('\r', '')
        if type(values) in [int, float, bool]:
            encapsulator = ""
        else:
            encapsulator = "'"
        if (name not in map(lambda e: e["field"], where)) or (name in set_and_where):
            if result != "":
                result+= ", "
            result += f"{name} = {encapsulator}{values}{encapsulator}"
    
    return result


def _generate_where_field(row: pd.Series, where):
    """Generates the where field of a SQL query"""
    result = ""
    for element in where:
        if result != "":
            result+= " AND "
        field_name = element["field"]
        operator = element["operator"]
        try:
            value = element["value"]
            result += f"{field_name} {operator} {value}"
        except Exception:
            if (type(row[field_name]) in [int, float, bool]) or (operator == 'IN'):
                affix = ""
            else :
                affix = "'"
            result += f"{field_name} {operator} {affix}{row[field_name]}{affix}"
    return result


def _split_dataframe(dataframe: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Splits the dataframe into 2 df.
        First one contains the rows that are already known and need to be updated with is_lox_claim=True.
        Second one contains the rows that are not known and need to be insert with is_lox_claim=False
    """
    if dataframe.empty:
        return dataframe, None
        
    print("Splitting the dataframe...")
    tracking_numbers = dataframe["tracking_number"].tolist()
    carrier = dataframe["carrier"][0]
    company = dataframe["company"][0]
    lox_claimed_tracking_numbers = select_refunds_by_tracking_numbers(
        company,
        carrier,
        tracking_numbers
    )["tracking_number"].tolist()
    known = dataframe.loc[dataframe['tracking_number'].isin(lox_claimed_tracking_numbers)]
    unkown = dataframe.loc[~dataframe['tracking_number'].isin( lox_claimed_tracking_numbers)]
    print(type(unkown))
    print_success(f"Splitted successfully. {known.shape[0]} known tracking numbers, {unkown.shape[0]} unknown tracking numbers.")
    return known, unkown


def update_credits_by_deletion(*,
    dataframe: pd.DataFrame,
    not_update: list = [],
    update_fields: list = [],
    carrier: str = '',
    company: str = ''
) -> list:
    
    if dataframe.empty:
        print("empty dataframe, skipping function")
        return
    
    if 'tracking_number' not in dataframe.columns or 'reason_refund' not in dataframe.columns:
        raise Exception('Update by deletion needs columns tracking_number & reason_refund.')
    
    
    tracking_numbers = dataframe['tracking_number'].unique().tolist()
    
    df_refunds = select_all_non_credited_refunds_from_tracking_number_list(tracking_numbers, carrier, company)
    
    dataframe = dataframe.drop(not_update, axis=1)
    columns_to_update = list(set(update_fields) | set(['tracking_number', 'reason_refund']))
    dataframe = dataframe[columns_to_update]
    
    df_refunds.drop(columns=update_fields, inplace=True)
    
    dataframe  = dataframe.join(df_refunds.set_index(['tracking_number', 'reason_refund']),on=['tracking_number', 'reason_refund'], how='right')
    # dataframe.reset_index(inplace = True, drop=True)
    dataframe.to_csv(f'{OUTPUT_FOLDER}/update-deletion/{company}-join.csv', index=False)  # To remove after end of testing. 
    
    print("dataframe", dataframe)
    
    dataframe['request_open_days'] = dataframe['request_open_days'].fillna(0).astype(int)
    dataframe['is_lox_claim'] = dataframe['is_lox_claim'].astype(bool)
    
    print(dataframe.dtypes) 
    
    reason_refunds  = dataframe['reason_refund'].unique().tolist()
    for reason_refund in reason_refunds:
        tracking_numbers = dataframe[dataframe['reason_refund']==reason_refund]['tracking_number'].unique().tolist()
    
    #---------------------DANGER-ZONE-----------------------------
        delete_refunds_for_tracking_numbers_and_reason_refund(tracking_numbers, reason_refund, carrier, company)
        
    insert_dataframe_into_database(dataframe = dataframe, table = TestEnvironment_dataset.Refunds_copy) # API request
    #--------------------END-DANGER-ZONE----------------------------


def update_from_dataframe(*,
    dataset: str,
    table: str,
    dataframe: pd.DataFrame,
    where: list,
    set_and_where: list = [],
    not_update: list = [],
    update_only: list = None,
) -> list:
    """ Generate SQL queries and send them to the Google BigQuery database.
        ## Arguments
        -`dataset`: The name of the dataset to update
        -`table`: The name of the table to update
        -`dataframe`: The dataframe that will be used to set the values
        -`where`:
            An object that helps creating the query.
            It takes fields from the dataset and apply an operator to match.
            If the 'value' operator is set, then it will take that value to look for in the dataframe
            instead of the row value.
        -`set_and_where`: A list of fields that will be updated even though they are used in the where clause.
        -`not_update`: List of fields that should not be updated
        -`update_only`: List of the only fields that should be updated
        
        ## Examples
            >>> example_1 = pd.DataFrame(data={
                    "location_id":["sender_location_id","receiver_location_id"],
                    "country_code":["FR","NL"],
                    "city":["Montpellier","Rotterdam"],
                    "postal_code":["34090","3012GD"],
                })
            >>> update_from_dataframe(
                    dataset="TestEnvironment",
                    table="Refunds",
                    dataframe=example_1,
                    where=[
                    {
                        "field":"location_id",
                        "operator": "=",
                    },{
                        "field":"country_code",
                        "operator": "NOT IN",
                        "value": "('FR')",
                    }],
                    set_and_where=['country_code']
                )
            # Queries sent to GBQ:
            #
            #   UPDATE TestEnvironment.Refunds
            #   SET country_code = 'FR', city = 'Montpellier', postal_code = '34090'
            #   WHERE location_id = 'sender_location_id' AND country_code NOT IN ('FR')
            #
            #   UPDATE TestEnvironment.Refunds
            #   SET country_code = 'NL', city = 'Rotterdam', postal_code = '3012GD'
            #   WHERE location_id = 'receiver_location_id' AND country_code NOT IN ('FR')
        
        ## Returns
        - The errors that occured while updating if there were some.
    """
    print(f"Updating '{table}' table from the '{dataset}' dataset...")
    
    # if table == "Refunds" and dataframe.shape[0] > 1: #Check if exists, if not insert with is_lox_claim=False
    #     dataframe, unknown_dataframe = _split_dataframe(dataframe)
    #     dataframe.loc["is_lox_claim"] = True
    #     unknown_dataframe.loc["is_lox_claim"] = False
    #     insert_dataframe_into_database(unknown_dataframe, InvoicesData_dataset.Refunds)
    
    results = []
    dataframe = dataframe.drop(not_update, axis=1)
    if not update_only is None:
        dataframe = dataframe[list(set(list(map(lambda x: x["field"],where + update_only))))]
    
    current_datetime_string = ""
    if "update_datetime" not in dataframe.columns:
        current_datetime_string = "update_datetime = CURRENT_DATETIME('Europe/Amsterdam'),"
    
    for index, row in dataframe.iterrows():
        print(f"Updating {index+1}/{dataframe.shape[0]} ...")
        query = f"""
        UPDATE {dataset}.{table}
        
        SET {current_datetime_string}
            {_generate_set_field(row, where, set_and_where)}
        
        WHERE {_generate_where_field(row, where)}
        """
        results.append(update(query))
    
    return results
