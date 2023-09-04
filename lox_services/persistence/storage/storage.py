"""All functions related to Google Cloud Storage"""
import os
import shutil
import urllib
from typing import Union, List

from google.api_core.page_iterator import HTTPIterator
from google.api_core import exceptions
from google.cloud.storage import Client, Blob


from lox_services.persistence.config import SERVICE_ACCOUNT_PATH
from lox_services.persistence.storage.constants import OUTPUT_FOLDER_BUCKET
from lox_services.persistence.storage.utils import use_environment_bucket
from lox_services.utils.general_python import print_info, print_success, safe_mkdir

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(SERVICE_ACCOUNT_PATH)


def process_gcloud_url(url: str) -> str:
    """
    Process a Google Cloud Storage URL to extract the blob url.

    Args:
        url (str): The URL to be processed.

    Returns:
        str: The extracted portion of the URL.
    """

    url = urllib.parse.unquote(url)

    # Extract the path
    path = url.split("cloud.google.com/")[1].rsplit("?authuser", 1)[0]

    blob = path.split("/", 1)[1]
    return blob


def get_bucket_content(bucket_name: str, prefix: str) -> HTTPIterator:
    """Gets all file names in the given bucket.
    ## Arguments
    - `bucket_name`: The name of the bucket.
    - `prefix`: The prefix path of the files to retrieve.

    ## Example
        >>> get_content("invoices_email", "/Chronopost")

    ## Returns
    An iterator of the retrieved files.
    """
    bucket_name = use_environment_bucket(bucket_name)
    storage_client = Client()
    blobs = storage_client.list_blobs(bucket_name, prefix=prefix)
    return blobs


def get_all_blobs_from_bucket(bucket_name: str) -> List[str]:
    """
    Retrieve all client invoices from a Google Cloud Storage bucket.

    Returns:
        list[str]: A list of all blob names in the bucket.
    """
    blobs = []

    blobs: list[Blob] = storage.get_bucket_content(bucket_name, "")

    # Extract the names of the blobs and store them in a separate list

    return [blob.name for blob in blobs]


def blob_exists_in_bucket(bucket_name: str, blob_name: str):
    """Tells if a blob (file) exists in a bucket.
    ## Arguments
    - `bucket_name`: The bucket to check.
    - `blob_name`: The blob to check.

    ## Example
        >>> blob_exists_in_bucket("invoices_clients","Bergamotte/Invoices/XP000752345FR.pdf")
    """
    bucket_name = use_environment_bucket(bucket_name)
    storage_client = Client()
    bucket = storage_client.bucket(bucket_name)
    stats = Blob(bucket=bucket, name=blob_name).exists(storage_client)
    # print(stats)
    return stats


def download_file(bucket_name: str, blob_name: str, target_file_path: str):
    """Downloads a blob (file) from a bucket.
    ## Arguments
    - `bucket_name`: The bucket containing the file to download.
    - `blob_name`: The blob to download.
    - `target_file_path`: The absolute path where the file will be downloaded.

    ## Example
        >>> download_file("invoices_clients","Bergamotte/Invoices/XP000752345FR.pdf", os.path.join(ROOT_PATH, "output_folder", "invoices_clients","Bergamotte","Chronopost","XP000752345FR.pdf"))
    """
    bucket_name = use_environment_bucket(bucket_name)
    print_info(
        f"Downloading from Lox Google Cloud Storage: {bucket_name}/{blob_name} ..."
    )
    safe_mkdir(target_file_path)
    storage_client = Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    try:
        blob.download_to_filename(target_file_path)
    except exceptions.NotFound as e:
        print(f"file {blob_name} not found")
        os.remove(target_file_path)
        raise e

    print_success(f"Successfuly downloaded at {target_file_path}")


def upload_file(
    bucket_name: str, source_file: Union[str, bytes], destination_file_path: str
):
    """Uploads a local file to the path specified in the given bucket in Google Cloud Storage.
    ## Arguments
    - `bucket_name`: The name of the bucket to upload the file to.
    - `source_file`: The absolute path of the file or bytes composing the file to upload.
    - `destination_file_path`: The full path where the file will be uploaded (after bucket name).

    ## Example
        >>> upload_file("invoices_email", "/home/whatever/example.pdf", "/Chronopost/40322379.pdf")

    ## Returns
    Nothing
    """
    bucket_name = use_environment_bucket(bucket_name)
    storage_client = Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_file_path)

    if isinstance(source_file, bytes):
        blob.upload_from_file(source_file)
        print_success(
            f"File uploaded to bucket '{bucket_name}': {destination_file_path}."
        )
    else:
        blob.upload_from_filename(source_file)
        print_success(
            f"File {source_file.split('/')[-1]} uploaded to bucket '{bucket_name}': {destination_file_path}."
        )


def download_file_from_url(
    url: str, output_folder: str, skip_if_existing: bool = False
):
    "Download file from storage by the storage url associated"
    url = urllib.parse.unquote(url)
    path = url.split("cloud.google.com/")[1].rsplit("?authuser", 1)[0]
    print(path)

    bucket = path.split("/")[0]
    blob = path.split("/", 1)[1]
    file_name = blob.rsplit("/", 1)[1]
    output_path = os.path.join(output_folder, file_name)

    if os.path.exists(output_path) and skip_if_existing:
        return

    download_file(bucket, blob, output_path)


def push_and_delete_run_output_folder(run_folder: str, destination_folder: str):
    "Zip run output folder, upload it to google cloud and delete both the archive and the folder from local storage."

    # make few checks before processing
    if not os.path.exists(run_folder):
        print(f"{run_folder} does not exist.")
        return
    if not os.path.isdir(run_folder):
        raise ValueError(f"{run_folder} needs to be a directory.")

    if "/output_folder/" not in run_folder:
        raise Exception(
            "Function use is limited to only output folder, since it uploads to output bucket!"
        )

    if not os.listdir(run_folder):
        print("Not any file to push to storage.")
        return

    archives_path = shutil.make_archive(os.path.basename(run_folder), "zip", run_folder)
    destination_path = os.path.join(destination_folder, os.path.basename(archives_path))
    upload_file(OUTPUT_FOLDER_BUCKET, archives_path, destination_path)

    os.remove(archives_path)
    shutil.rmtree(run_folder)


def delete_file_from_storage(
    bucket_name: str,
    blob_name: str,
):
    """Removes file specified from the given bucket in Google Cloud Storage.
    ## Arguments
    - `bucket_name`: The name of the bucket where file is.
    - `source_file`: The path to the file to remove.

    ## Example
        >>> delete_file_from_storage("invoices_clients", "Helloprint/Invoices/UPS/1Z1234567890.pdf")

    ## Returns
    Nothing
    """
    bucket_name = use_environment_bucket(bucket_name)
    storage_client = Client()

    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    if blob.exists():
        print(f"Removing {blob_name} from storage.")
        blob.delete()


def delete_file_from_url(url: str):
    """
    Deletes a file from storage based on the provided URL.

    Args:
        url (str): The URL of the file to be deleted from storage.

    ## Example
        >>> delete_file_from_url("https://storage.cloud.google.com/invoices_clients/Helloprint/Invoices/UPS/1Z1234567890.pdf")

    Returns:
        None
    """

    url = urllib.parse.unquote(url)
    path = url.split("cloud.google.com/")[1].rsplit("?authuser", 1)[0]

    bucket = path.split("/")[0]
    blob = path.split("/", 1)[1]

    delete_file_from_storage(bucket_name=bucket, blob_name=blob)


def delete_multiple_files_from_storage(
    bucket_name: str,
    blob_names: List[str],
):
    """Removes existing files specified from the given bucket in Google Cloud Storage.
    ## Arguments
    - `bucket_name`: The bucket's name where the files are stored.
    - `blob_names`: List of files to be deleted.

    ## Example
        >>> delete_multiple_files_from_storage("invoices_clients", ["Helloprint/Invoices/UPS/1Z1234567890.pdf"])

    """
    bucket_name = use_environment_bucket(bucket_name)
    storage_client = Client()

    bucket = storage_client.bucket(bucket_name)

    # Make sure that the blobs exist before deleting them
    to_delete = [x for x in blob_names if x in get_all_blobs_from_bucket(bucket_name)]

    bucket.delete_blobs(to_delete)
