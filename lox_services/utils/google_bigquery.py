from datetime import datetime, timezone, timedelta

import pandas as pd
from google.cloud.bigquery import Client, DatasetReference, LoadJobConfig as LoadConfig


def make_temporary_table(
    project: str,
    dataset_id: str,
    table_name: str,
    dframe: pd.DataFrame,
    write_disposition: str = "WRITE_TRUNCATE",
) -> None:
    """Make the table out of a dataframe and set it to be temporary. Avoids race condition
    with parallelization."""

    table = ".".join((project, dataset_id, table_name))

    bigquery_client = Client()

    bigquery_client.load_table_from_dataframe(
        dframe, table, job_config=LoadConfig(write_disposition=write_disposition)
    ).result()

    table_ref = DatasetReference(project, dataset_id).table(table_name)
    table_ref = bigquery_client.get_table(table_ref)
    table_ref.expires = datetime.now(timezone.utc) + timedelta(hours=1)
    bigquery_client.update_table(table_ref, ["expires"])  # API request
