UserData.UsersActivity
(
  email STRING NOT NULL, --REQUIRED
  url STRING NOT NULL, --REQUIRED
  date DATETIME NOT NULL, --REQUIRED
  parameters STRING NOT NULL, --REQUIRED
  browserInfo STRING NOT NULL, --REQUIRED
  insert_datetime DATETIME NOT NULL, --REQUIRED
  update_datetime DATETIME
)
