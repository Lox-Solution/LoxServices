LoxData.DueInvoices
(
    company STRING NOT NULL, --REQUIRED
    invoice_date DATE NOT NULL, --REQUIRED
    status STRING NOT NULL, --REQUIRED
    invoice_number STRING NOT NULL, --REQUIRED
    insert_datetime DATETIME NOT NULL, --REQUIRED
    update_datetime DATETIME
)