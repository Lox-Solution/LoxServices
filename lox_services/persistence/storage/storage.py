"""All functions related to Google Cloud Storage"""
import datetime
import os
import re
import urllib
from typing import List

import pandas as pd
from google.api_core.page_iterator import HTTPIterator
from google.api_core import exceptions
from google.cloud.storage import Client, Blob

from lox_services.persistence.database.queries.user_data import select_all_carrier_invoices_information
from lox_services.persistence.config import SERVICE_ACCOUNT_PATH
from lox_services.persistence.storage.utils import use_environment_bucket
from lox_services.persistence.database.update import update_from_dataframe
from lox_services.utils.general_python import print_info, print_success, safe_mkdir

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.path.join(SERVICE_ACCOUNT_PATH)

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


def get_folders_names(bucket_name: str, prefix: str) -> List[str]:
    """Gets all direct folders with given arguments.
        ## Arguments
        - `bucket_name`: The name of the bucket.
        - `prefix`: The prefix path of the files to retrieve.
        
        ## Example
            >>> get_content("invoices_clients", "YellowKorner")
        
        ## Returns
        A list of all folders found in the given bucket and prefixes.
    """
    if not prefix:
        raise ValueError("Prefix name must be provided.")
    bucket_name = use_environment_bucket(bucket_name)
    delimiter = '/'
    if not prefix.endswith(delimiter):
        prefix += delimiter
    storage_client = Client()
    blobs = storage_client.list_blobs(bucket_name, prefix=prefix, delimiter=delimiter)
    [b for b in blobs] #iterate through all blobs to get folders in .prefixes entity
    return [folder.replace(prefix,"").rsplit("/", 1)[0] for folder in blobs.prefixes]


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
    print_info(f"Downloading from Lox Google Cloud Storage: {bucket_name}/{blob_name} ...")
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


def upload_file(bucket_name: str, source_file_path: str, destination_file_path: str):
    """Uploads a local file to the path specified in the given bucket in Google Cloud Storage.
        ## Arguments
        - `bucket_name`: The name of the bucket to upload the file to.
        - `source_file_path`: The absolute path of the file to upload.
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
    blob.upload_from_filename(source_file_path)
    
    print_success(f"File {source_file_path.split('/')[-1]} uploaded to bucket '{bucket_name}': {destination_file_path}.")


def generate_download_signed_url_v4(bucket_name: str, blob_name: str):
    """Generates a v4 signed URL for downloading a blob.
        Note that this method requires a service account key file. You can not use
        this if you are using Application Default Credentials from Google Compute
        Engine or from the Google Cloud SDK.
    """
    # bucket_name = 'your-bucket-name'
    # blob_name = 'your-object-name'
    bucket_name = use_environment_bucket(bucket_name)
    print(f"Generated GET signed URL for {bucket_name} {blob_name}")
    storage_client = Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    
    url = blob.generate_signed_url(
        version="v4",
        # This URL is valid for 15 minutes
        expiration=datetime.timedelta(minutes=15),
        # Allow GET requests using this URL.
        method="GET",
    )
    
    print(url)
    return url


def download_invoices_not_processed(company: str, carrier: str, invoices_folder: str) -> List[str]:
    """Downloads all invoices that were dropped by clients and are not processed
        ## Arguments
        - `company`: The name of the company being ran.
        - `carrier`: The name of the carrier being ran.
        - `invoices_folder`: The full path where the files will be downloaded.
        
        ## Example
            >>> download_file("invoices_clients","Cultura/2021-11-29/17%3A00%3A22.839Z-facture_chronopost_40476401_202011-1.xls", os.path.join('/',"XP000752345FR.pdf"))
        
        ## Returns
        Nothing
    """
    all_files = select_all_carrier_invoices_information(company, carrier)
    print(all_files)
    downloaded_file_paths = []
    # all_files['carrier'] = 'Chronopost'
    for _, row in all_files.iterrows():
        if row['has_been_processed']:
            continue
        
        print('url', row['url'])
        # Get the bucket name from the URL
        bucket_name = row['url'].split('/')[3]
        #https://cloud.google.com/invoices_clients/24S/2021-07-06/2021-07-06T07%3A50%3A37.316Z%20Facture%20Chronopost%20Janvier%202021.xls?authuser=0
        
        # Remove the website and bucket name from the url
        blob_name = '/'.join(row['url'].split('?')[0].split('/')[4:])
        
        # print("bucket_name", bucket_name)
        # print("blob name",blob_name)
        
        # Replace url character by normal ones
        blob_name = urllib.parse.unquote(blob_name)
        # blob_name = blob_name.replace('%2F', '/').replace('%3A',':').replace()
        
        print("bucket_name", bucket_name)
        print("blob name",blob_name)
        output_path = os.path.join(invoices_folder, row['file_name'])
        
        print(output_path)
        download_file(bucket_name, blob_name, output_path)
        downloaded_file_paths.append(output_path)
    return downloaded_file_paths


def set_invoices_not_processed_to_processed(company: str, carrier:str) -> None:
    """Updates as processed all the company for a specific carrier
        ## Arguments
        - `company`: The name of the company being ran.
        - `carrier`: The name of the carrier being ran.
        
        ## Example
            >>> set_invoices_not_processed_to_processed("Cultura", "Chronopost")
        
        ## Returns
        Nothing
    """
    update_from_dataframe(
        dataset='UserData',
        table='DroppedFiles',
        dataframe= pd.DataFrame([[company, carrier, True]], columns = ['company', 'carrier', 'has_been_processed']),
        where=[{
            "field":"carrier",
            "operator": "="
        },{
            "field":"company",
            "operator": "="
        }]
    )

def download_file_from_url(url: str, output_folder: str):
    url = urllib.parse.unquote(url)
    path = url.split("cloud.google.com/")[1].rsplit("?authuser", 1)[0]
    print(path)
    
    bucket = path.split("/")[0]
    blob = path.split("/", 1)[1]
    file_name = blob.rsplit("/", 1)[1]
    
    download_file(bucket, blob, os.path.join(output_folder, file_name))



def download_file_by_url(url: str, download_path: str):
    "Download file from storage by the storage url associated"
    decode_url = urllib.parse.unquote(url)
    if not re.match(r"(https://storage.cloud.google.com/).*(\?authuser=0)", decode_url):
        raise Exception("URL path need to match '(https://storage.cloud.google.com/).*(\?authuser=0)'")
    file_path = decode_url.split("https://storage.cloud.google.com/")[-1].rsplit("?authuser=0")[0]
    bucket, blob_name = file_path.split("/", 1)
    safe_mkdir(download_path)
    download_file(bucket, blob_name, download_path)
