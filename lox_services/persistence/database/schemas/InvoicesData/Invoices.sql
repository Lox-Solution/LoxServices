InvoicesData.Invoices
(
    company STRING NOT NULL, --REQUIRED
    carrier STRING NOT NULL, --REQUIRED
    invoice_number STRING NOT NULL, --REQUIRED
    invoice_date DATE NOT NULL, --REQUIRED
    original_net_amount FLOAT64,-- NOT NULL, --REQUIRED NOT OK
    original_currency_code STRING,-- NOT NULL, --REQUIRED NOT OK
    net_amount FLOAT64 NOT NULL, --REQUIRED
    type_charges STRING NOT NULL, --REQUIRED
    description STRING NOT NULL, --REQUIRED
    account_number STRING,
    reference STRING,
    tracking_number STRING,
    url STRING,
    quantity INT64,
    amount FLOAT64,
    incentive_amount FLOAT64,
    discount FLOAT64,
    country_code_sender STRING,
    country_code_receiver STRING,
    postal_code_receiver STRING,
    weight FLOAT64,
    length FLOAT64,
    width FLOAT64,
    height FLOAT64,
    type_weight STRING,
    zone STRING,
    lead_tracking_number STRING,
    is_return BOOL,
    original_amount FLOAT64,
    insert_datetime DATETIME NOT NULL, --REQUIRED
    update_datetime DATETIME
)