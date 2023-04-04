import os
from lox_services.persistence.config import ENVIRONMENT
from lox_services.persistence.storage.constants import INVOICE_BASE_URL


def generate_invoice_storage_url(
    company: str, carrier: str, tracking_number: str
) -> str:
    """generate the storage url for client invoices
    ## Arguments
    - `company`: The name of the company being ran.
    - `carrier`: The name of the carrier being ran.
    - `tracking_number`: tracking_number linked to invoice.

    ## Example
        >>> generate_invoice_storage_url(
            "test",
            "UPPS",
            "XX00000XX"
            ) # https://storage.cloud.google.com/invoices_clients/test/Invoices/UPS/XX00000XX.pdf
    ## Returns
        str
    """
    return os.path.join(
        INVOICE_BASE_URL, company, "Invoices", carrier, f"{tracking_number}.pdf"
    )


def extract_tracking_number_from_file_storage_name(file_storage_name: str) -> str:
    "Get tracking_number from google storage path"
    return file_storage_name.rsplit("/", maxsplit=1)[-1].rsplit(".", 1)[0]


def use_environment_bucket(bucket_name: str):
    """Modifies the bucket_name if using development mode."""
    if not bucket_name:
        print("bucket_name:", type(bucket_name))
        raise ValueError("Bucket name must be provided.")

    if ENVIRONMENT == "development":
        bucket_name += "_development"

    return bucket_name
