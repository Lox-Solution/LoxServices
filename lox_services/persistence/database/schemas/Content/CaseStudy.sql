Content.CaseStudy
(
    company_name STRING NOT NULL, --REQUIRED
    language STRING NOT NULL, --REQUIRED
    json_content STRING NOT NULL, --REQUIRED
    is_live BOOL NOT NULL, --REQUIRED
    insert_datetime DATETIME NOT NULL, --REQUIRED
    update_datetime DATETIME
)