LoxData.Blacklist
(
    ip_address STRING NOT NULL, --REQUIRED
    banned_at DATETIME NOT NULL, --REQUIRED
    insert_datetime DATETIME NOT NULL, --REQUIRED
    update_datetime DATETIME
)