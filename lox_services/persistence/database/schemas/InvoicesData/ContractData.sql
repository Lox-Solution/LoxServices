InvoicesData.ContractData
(
    carrier STRING NOT NULL, --REQUIRED
    company STRING NOT NULL, --REQUIRED
    country STRING,
    service_level STRING,
    zone STRING,
    weight_from FLOAT64,
    weight_to FLOAT64,
    trade STRING,
    type_packaging STRING,
    period INT64,
    price_per STRING,
    start_date DATE,
    end_date DATE,
    type_charges STRING,
    description STRING,
    countries STRING,
    price FLOAT64,
    insert_datetime DATETIME NOT NULL, --REQUIRED
    update_datetime DATETIME
)
