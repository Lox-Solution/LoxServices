Content.MyClaims
(
    carrier STRING NOT NULL, --REQUIRED
    reason_refund STRING NOT NULL, --REQUIRED
    form_field STRING,
    insert_datetime DATETIME NOT NULL, --REQUIRED
    update_datetime DATETIME
)
