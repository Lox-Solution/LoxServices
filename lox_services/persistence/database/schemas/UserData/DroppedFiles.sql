UserData.DroppedFiles
(
  company STRING NOT NULL, --REQUIRED
  file_name STRING NOT NULL, --REQUIRED
  uploaded_date DATE NOT NULL, --REQUIRED
  url STRING NOT NULL, --REQUIRED
  has_been_processed BOOL NOT NULL, --REQUIRED
  is_carrier_invoice BOOL NOT NULL, --REQUIRED
  carrier STRING,
  document_type STRING,
  insert_datetime DATETIME NOT NULL, --REQUIRED
  update_datetime DATETIME
)
