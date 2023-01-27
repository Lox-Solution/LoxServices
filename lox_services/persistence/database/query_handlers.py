"""All functions to query the database."""
import os
import re
import time
from typing import Optional

from google.cloud.bigquery import Client, QueryJobConfig
from google.cloud.bigquery.job import QueryJob
from pandas import DataFrame

from lox_services.persistence.config import SERVICE_ACCOUNT_PATH
from lox_services.persistence.database.exceptions import BadQueryTypeException, MissingUpdateDatetimeException
import lox_services.utils.general_python as gpy
from lox_services.utils.enums import Colors
from lox_services.utils.metadata import get_function_callers


def raw_query(query: str, print_query: bool = True, job_config: Optional[QueryJobConfig] = None) -> QueryJob:
    """Excecutes a query with Google BigQuery, without any checks.
        Adds some metadata at the beginning of the query.
        ## Arguments
        - `query`: String representation of the query to be executed.
        - `print_query`: Tells whether or not to print the query before executing it.

        ## Example
            >>> raw_query("SELECT * FROM InvoicesData.Refunds LIMIT 10")

        ## Return
        The the query job from Google BigQuery. It needs some actions to be rendered
        as a dataframe (.result().to_dataframe()).
    """
    meta_data = None
    meta_parents = get_function_callers()
    if len(meta_parents) > 2:
        meta_data = meta_parents[2]

    elif len(meta_parents) > 1:
        if meta_parents[1] not in {"select", "update"}:
            # if raw_query is being called directly, which should be avoided
            meta_data = meta_parents[1]

    if meta_data is not None:
        query = f"#{meta_data}\n{query}"

    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.path.join(SERVICE_ACCOUNT_PATH)
    if print_query:
        print(gpy.colorize(
            query,
            Colors.Magenta
        ))

    bigquery_client = Client()
    query_job = bigquery_client.query(query, job_config=job_config)
    query_job.result()
    return query_job


def select(query: str, print_query: bool = True, job_config: Optional[QueryJobConfig] = None) -> DataFrame:
    """Checks if the query begings with a SELECT statement. If so the query is being executed.
        ## Arguments
        - `query`: String representation of the query to be executed.
        - `print_query`: Tells whether or not to print the query before executing it.

        ## Example
            >>> select("SELECT * FROM InvoicesData.Refunds LIMIT 10")

        ## Return
        The result of the select query as a dataframe.
    """
    if not (query.lstrip().startswith("SELECT") or query.lstrip().startswith("WITH")):
        raise BadQueryTypeException('SELECT or WITH')

    return raw_query(query, print_query, job_config).result().to_dataframe()


def update(query: str, print_query: bool = True) -> int:
    """Checks if the query begings with a UPDATE statement. If so the query is being executed.
        ## Arguments
        - `query`: String representation of the query to be executed.
        - `print_query`: Tells whether or not to print the query before executing it.

        ## Example
            >>> update("UPDATE InvoicesData.Refunds SET state='Test' WHERE company='Test'")

        ## Return
        The result of the update query is a number of affected rows.
    """
    if not query.lstrip().startswith("UPDATE"):
        raise BadQueryTypeException('UPDATE')

    if not re.match("(\n| )*(UPDATE).*(\n| )(SET)(\n| ).*(update_datetime)( )?(=).*(\n| )(WHERE)(\n| ).*", query,
                    re.DOTALL):
        raise MissingUpdateDatetimeException(query)

    count = 0
    query_success = False
    result = None
    while not query_success:
        try:
            result = raw_query(query, print_query)
            print("Rows affected:", result.num_dml_affected_rows)
            result_returned = result.num_dml_affected_rows
            query_success = True
        except Exception as error:
            error_msg = error.__dict__["_errors"][0]["message"]
            if "concurrent update" in error_msg:
                count += 1
                time.sleep(5)
                print("error concurent update attempt ", count)
                if count > 4:
                    raise error
            else:
                raise error
    if result_returned is not None:
        return result_returned
    else:
        raise Exception("Error processing update: ", query)


def delete(query: str, print_query: bool = True) -> DataFrame:
    """Checks if the query begings with a DELETE statement. If so the query is being executed.

        ## Arguments

        - `query`: String representation of the query to be executed.

        - `print_query`: Tells whether or not to print the query before executing it.

        ## Example

            >>> select("DELETE InvoicesData.Refunds WHERE tracking_number = '1467BDYV'")

        ## Return

        The result of the select query as a dataframe.
    """
    if not query.lstrip().startswith("DELETE"):
        raise BadQueryTypeException('DELETE')

    result = raw_query(query, print_query)
    print("Rows deleted:", result.num_dml_affected_rows)

