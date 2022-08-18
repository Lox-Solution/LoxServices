InvoicesData.ClientInvoicesData
(
    company STRING NOT NULL, --REQUIRED
    carrier STRING NOT NULL, --REQUIRED
    tracking_number STRING,
    reference STRING,
    postal_code STRING,
    city STRING,
    country STRING,
    product_description_detailled STRING,
    product_category STRING,
    customer_id STRING,
    sales_channel STRING,
    sales_date DATE,
    currency_code STRING,
    net_amount FLOAT64,
    quantity INT64,
    amount FLOAT64,
    incentive_amount FLOAT64,
    tax_amount FLOAT64,
    tax_percentage FLOAT64,
    invoice_url STRING,
    design_url STRING,
    picture_url STRING,
    phone_number STRING,
    is_normalized_data BOOL OPTIONS(description="Was the data given by the customer or generated thanks to a set of possible data"),
    insert_datetime DATETIME NOT NULL, --REQUIRED
    update_datetime DATETIME
)