UserData.CustomerData
(
  company STRING NOT NULL, --REQUIRED
  segment STRING,
  first_contact_date DATE,
  starting_date DATE,
  cohort STRING,
  sales_cycle STRING,
  first_invoice_date DATE,
  onboarding_time INT64,
  insert_datetime DATETIME NOT NULL, --REQUIRED
  update_datetime DATETIME
)