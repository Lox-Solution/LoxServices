InvoicesData.Transits
(
    company STRING NOT NULL, --REQUIRED
    carrier STRING NOT NULL, --REQUIRED
    tracking_number STRING NOT NULL,
    transit_time_days FLOAT64,
    is_late BOOL,
    insert_datetime DATETIME NOT NULL, --REQUIRED
    update_datetime DATETIME
)