LoxData.Targets
(
    metric STRING NOT NULL, --REQUIRED
    month DATE NOT NULL, --REQUIRED
    target INT64 NOT NULL, --REQUIRED
    insert_datetime DATETIME NOT NULL, --REQUIRED
    update_datetime DATETIME
)
