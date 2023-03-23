LoxData.InvoicesDetails
(
    invoice_number STRING NOT NULL, --REQUIRED
    description STRING NOT NULL, --REQUIRED
    due_amount FLOAT64 NOT NULL, --REQUIRED
    saved_amount FLOAT64,
    orders INT64,
    insert_datetime DATETIME NOT NULL, --REQUIRED
    update_datetime DATETIME
)
