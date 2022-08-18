InvoicesData.InvoiceFileName
(
    file_name STRING NOT NULL, --REQUIRED
    company STRING NOT NULL, --REQUIRED
    uploaded_date DATE NOT NULL, --REQUIRED
    url STRING NOT NULL OPTIONS(description="Authentication required to access this url (with @loxsolution account)."), --REQUIRED
    has_been_processed BOOL NOT NULL, --REQUIRED
    insert_datetime DATETIME NOT NULL, --REQUIRED
    update_datetime DATETIME
)