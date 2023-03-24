import os

from lox_services.persistence.database.query_handlers import raw_query, select

SCHEMAS_TABLES_PATH = os.path.dirname(__file__)


def get_creation_table_sql_query(dataset: str, table: str) -> str:
    """Gets the creation query for a table with schema data."""
    query = f"""
        SELECT
            table_name,
            ddl
        FROM
            {dataset}.INFORMATION_SCHEMA.TABLES
        WHERE
            table_name = "{table}"
    """
    return select(query).loc[0]["ddl"]


def create_table_with_schema(dataset: str, table: str):
    """Creates a table with the SQL file provided
    ## Arguments
    - `dataset`: The dataset name in which the table will be created. It must correspond to a sub-folder in the schemas folder.
    - `table`: The table name to create. It must correspond to a file in a dataset folder.

    ## Example
    ```python
    create_table_with_schema("LoxData", "Hello")
    ```
    """
    with open(os.path.join(SCHEMAS_TABLES_PATH, dataset, f"{table}.sql")) as sql_file:
        query = sql_file.read()

    query = "CREATE TABLE " + query
    queryjob = raw_query(query)
    return queryjob


def use_new_table_schema(dataset: str, table: str):
    """Use new schema for a table
    ## Arguments
    - `dataset`: The dataset name of the table to update. It must correspond to a sub-folder in the schemas folder.
    - `table`: The table name to update. It must correspond to a file in a dataset folder.

    ## Example
    ```python
    use_new_table_schema("LoxData", "Invoicing")
    ```
    """
    with open(os.path.join(SCHEMAS_TABLES_PATH, dataset, f"{table}.sql")) as sql_file:
        query = sql_file.read()

    query = (
        "CREATE OR REPLACE TABLE "
        + query
        + f"""
        AS
        SELECT *
        FROM {dataset}.{table}
    """
    )
    queryjob = raw_query(query)
    return queryjob


def use_all_new_tables_schemas():
    """Apply table schema on files"""
    datasets = list(
        filter(lambda dir: ".py" not in dir, os.listdir(SCHEMAS_TABLES_PATH))
    )
    datasets.sort()
    for dataset in datasets:
        tables = list(
            map(
                lambda file: file.replace(".sql", ""),
                filter(
                    lambda dir: ".sql" in dir,
                    os.listdir(os.path.join(SCHEMAS_TABLES_PATH, dataset)),
                ),
            )
        )
        tables.sort()
        for table in tables:
            use_new_table_schema(dataset, table)
