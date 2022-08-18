InvoicesData.DeliverySLAs
(
    carrier STRING NOT NULL, --REQUIRED
    country_code_sender STRING,
    country_code_receiver STRING,
    description STRING,
    days_max INT64,
    time_max TIME OPTIONS(description="The time after which a package is late."),
    insert_datetime DATETIME NOT NULL, --REQUIRED
    update_datetime DATETIME
)