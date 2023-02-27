InvoicesData.Refunds
(
    company STRING NOT NULL, --REQUIRED
    carrier STRING NOT NULL, --REQUIRED
    reason_refund STRING NOT NULL, --REQUIRED
    state STRING NOT NULL, --REQUIRED
    invoice_number STRING,
    invoice_date DATE,
    total_price FLOAT64,
    tracking_number STRING,
    reference STRING,
    service_level STRING,
    real_weight FLOAT64,
    real_size STRING,
    status STRING,
    request_open_days INT64,
    request_date DATE,
    confirm_date DATE,
    credit_date DATE,
    declined_date DATE,
    reminder_date_01 DATE,
    reminder_date_02 DATE,
    last_contact_date DATE,
    dispute_date DATE,
    credit_invoice_number STRING,
    lox_invoice_number STRING,
    claim_number STRING,
    is_lox_claim BOOL,
    is_client_created BOOL,
    reason_declined STRING,
    credit_discovery_date DATE,
    insert_datetime DATETIME NOT NULL, --REQUIRED
    update_datetime DATETIME,
    original_credit_amount FLOAT64,
    original_credit_currency STRING
)
