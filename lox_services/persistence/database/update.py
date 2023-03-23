"""All material needed to generate the update query."""
from typing import Tuple

import pandas as pd
from lox_services.persistence.database.constants import BQ_CURRENT_DATETIME
from lox_services.persistence.database.query_handlers import update


def _generate_set_field(row, where, set_and_where):
    """Generates the set field of a update SQL query"""
    result = ""
    for name, values in row.iteritems():
        if isinstance(values, str):
            # make sure that the value doesn't contains special characters
            values = values.replace("\n", " ").replace("\r", "")
        if type(values) in [int, float, bool]:
            encapsulator = ""
        else:
            encapsulator = "'"
        if (name not in map(lambda e: e["field"], where)) or (name in set_and_where):
            if result != "":
                result += ", "
            result += f"{name} = {encapsulator}{values}{encapsulator}"

    return result


def _generate_where_field(row: pd.Series, where):
    """Generates the where field of a SQL query"""
    result = ""
    for element in where:
        if result != "":
            result += " AND "
        field_name = element["field"]
        operator = element["operator"]
        try:
            value = element["value"]
            result += f"{field_name} {operator} {value}"
        except Exception:
            if (type(row[field_name]) in [int, float, bool]) or (operator == "IN"):
                affix = ""
            else:
                affix = "'"
            result += f"{field_name} {operator} {affix}{row[field_name]}{affix}"
    return result


def update_from_dataframe(
    *,
    dataset: str,
    table: str,
    dataframe: pd.DataFrame,
    where: list,
    set_and_where: list = [],
    not_update: list = [],
    update_only: list = None,
) -> list:
    """Generate SQL queries and send them to the Google BigQuery database.
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

    results = []
    dataframe = dataframe.drop(not_update, axis=1)
    if not update_only is None:
        dataframe = dataframe[
            list(set(list(map(lambda x: x["field"], where + update_only))))
        ]

    current_datetime_string = ""
    if "update_datetime" not in dataframe.columns:
        current_datetime_string = f"update_datetime = {BQ_CURRENT_DATETIME},"

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
