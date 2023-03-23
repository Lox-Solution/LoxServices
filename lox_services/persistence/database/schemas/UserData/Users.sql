UserData.Users
(
  email_address STRING NOT NULL, --REQUIRED
  admin BOOL NOT NULL, --REQUIRED
  first_name STRING NOT NULL, --REQUIRED
  last_name STRING NOT NULL, --REQUIRED
  company_name STRING NOT NULL, --REQUIRED
  password STRING,
  allowed BOOL,
  phone_number STRING,
  job_title STRING,
  processed BOOL,
  temporary_password STRING,
  dashboard_access BOOL,
  insert_datetime DATETIME NOT NULL, --REQUIRED
  update_datetime DATETIME
)
