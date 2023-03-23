UserData.Credentials
(
    carrier STRING NOT NULL, --REQUIRED
    company STRING NOT NULL, --REQUIRED
    username STRING NOT NULL, --REQUIRED
    password STRING NOT NULL, --REQUIRED
    is_sub_account BOOL NOT NULL, --REQUIRED
    ready_for_airflow BOOL NOT NULL, --REQUIRED
    first_run BOOL NOT NULL, --REQUIRED
    is_wrong_credentials BOOL,
    to_claim BOOL,
    label STRING,
    portal_url STRING,
    account_number STRING,
    language STRING,
    contact_email STRING,
    contact_name STRING,
    content STRING,
    contact_phone STRING,
    is_receiving_invoices BOOL,
    insert_datetime DATETIME NOT NULL, --REQUIRED
    update_datetime DATETIME,
    contacted BOOL,
    no_claim_by_reasons ARRAY<STRING> OPTIONS(description = "An array of reasons that should not be claimed")
)
