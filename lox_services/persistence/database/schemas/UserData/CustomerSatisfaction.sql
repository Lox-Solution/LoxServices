UserData.CustomerSatisfaction
(
  email_address STRING NOT NULL, --REQUIRED
  satisfaction_score FLOAT64 NOT NULL, --REQUIRED
  last_updated TIMESTAMP NOT NULL, --REQUIRED
  insert_datetime DATETIME NOT NULL, --REQUIRED
  update_datetime DATETIME
)