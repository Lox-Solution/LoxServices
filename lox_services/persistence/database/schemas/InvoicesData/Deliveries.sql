InvoicesData.Deliveries
(
    tracking_number STRING NOT NULL, --REQUIRED
    status STRING NOT NULL, --REQUIRED
    final_status STRING,
    date_time DATETIME,
    alternative_tracking_number STRING,
    location STRING,
    quantity INT64,
    is_return BOOL,
    url STRING,
    insert_datetime DATETIME NOT NULL, --REQUIRED
    update_datetime DATETIME
)
