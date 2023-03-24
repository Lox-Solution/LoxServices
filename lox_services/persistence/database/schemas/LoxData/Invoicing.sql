LoxData.Invoicing
(
    company STRING NOT NULL OPTIONS(description="The company name. Used internally."), --REQUIRED
    is_signed BOOL NOT NULL OPTIONS(description="True: The company is signed. False otherwise."), --REQUIRED
    auto_email BOOL OPTIONS(description="True: Bills are automatically sent. False: A manual sendout has to be done."),
    invoice_company_name STRING OPTIONS(description="The name chosen by the company to be displayed on the bills."),
    country STRING OPTIONS(description="The country code of the company."),
    success_fee_refund INT64 OPTIONS(description="Success fee in percentage. Ex: 30 = 30% of fee."),
    account_number INT64,
    payment_term INT64,
    invoicing_interval INT64,
    starting_date DATE,
    ending_date DATE,
    start_trial_period DATE,
    end_trial_period DATE,
    cap STRING,
    vat INT64,
    street_name STRING,
    zip_code STRING,
    country_name STRING,
    dashboard BOOL,
    vat_number STRING,
    department STRING,
    IBAN STRING,
    bank_name STRING,
    bank_sort_code STRING,
    --automated_billing_email BOOL OPTIONS(description="DEPRECATED"),
    city_name STRING,
    dashboard_price FLOAT64,
    invoicing_emails ARRAY<STRUCT<email_address STRING>> OPTIONS(description="List of emails to use during the automated invoice sendout."),
    data_processed BOOL OPTIONS(description="Whether the first audit has been run and data is available"),
    COC STRING,
    BIC STRING,
    bank_account_number STRING,
    siret STRING OPTIONS(description="SIRET of the company"),
    to_run BOOL OPTIONS(description="True: The scripts are running with the company's credentials. False: Nothing runs"),
    is_churned BOOL,
    order_number STRING(description="The customer's order number for Lox services."),
    insert_datetime DATETIME NOT NULL, --REQUIRED
    update_datetime DATETIME
)
