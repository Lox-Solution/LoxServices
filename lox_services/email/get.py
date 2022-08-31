"""All functions related to email fetching."""
import email
import imaplib
import os
from datetime import datetime, timedelta
from email import policy
from email.message import Message
from typing import List, TypedDict
from lox_services.config.env_variables import get_env_variable
from lox_services.email.utils import (
    generate_oauth2_string,
    refresh_authorization)
from lox_services.utils.general_python import print_info, print_success, safe_mkdir

class GmailSearchOperators(TypedDict):
    """Some of Gmail operators to use in email searches.
        https://support.google.com/mail/answer/7190?hl=en
    """
    subject: str


def get_emails(
    mailbox: str,
    days: int = 1,
    *,
    search: GmailSearchOperators = {},
    strict = False
) -> List[Message]:
    """Gets the emails with the given label.
        ## Arguments
        - `mailbox`: The label to use to filter the emails.
        - `delta_days`: The number of days to look for in the past.
        - `filter`: The filter to use to filter the emails.
        
        ## Example
            >>> get_emails_with_label('Carriers/Chronopost', 30)
            #or
            >>> get_emails_with_label('Carriers/ColisPrive')
            
        ## Returns
        - A list of emails as `email.Message` class instances, refer to official doc to know what to do with it next.
    """
    imap_ssl_client = imaplib.IMAP4_SSL('imap.gmail.com')
    imap_ssl_client.debug = 4
    
    access_token = refresh_authorization(get_env_variable("LOXTEAM_REFRESH_TOKEN"))
    auth_string = generate_oauth2_string('loxteam@loxsolution.com', access_token)
    
    imap_ssl_client.authenticate('XOAUTH2', lambda x: auth_string)
    labeled_status, labeled_emails = imap_ssl_client.select(mailbox)
    if labeled_status != 'OK':
        raise ValueError("Invalid label value.")
    
    print_info(f"There are {int(labeled_emails[0])} emails matching this label.")
    
    # Generating search criterias
    search_criterias = ''
    
    max_date = (datetime.today() - timedelta(days)).strftime('%d-%b-%Y')
    date_criteria = f'SENTSINCE {max_date} '
    search_criterias += date_criteria
    
    for key, value in search.items():
        string_value = f'"{value}"' if strict else value.replace(' ', '-')
        search_criterias += f"{str(key).upper()} {string_value} "
    
    print_info(f"Search criterias: {search_criterias}")
    status, emails_bytes = imap_ssl_client.search(None, f'({search_criterias.strip()})')
    if status != 'OK':
        print('No emails found!')
        return
    
    emails_numbers_bytes = emails_bytes[0].split()
    print_info(f"There are {len(emails_numbers_bytes)} emails found for this label in the last {days} days.")
    
    emails: List[Message] = []
    for index_byte in emails_numbers_bytes:
        status, data_bytes = imap_ssl_client.fetch(index_byte, '(BODY.PEEK[])')
        if status != 'OK':
            raise Exception('An unknown error occured while trying to fetch email body.')
        
        email_content_bytes = data_bytes[0][1]
        email_content = email.message_from_bytes(email_content_bytes, policy=policy.default) #policy.default is very important, it's decoding "encoded-word" subjects https://stackoverflow.com/questions/12903893/python-imap-utf-8q-in-subject-string
        subject = str(email_content['Subject'])
        date = datetime.strptime(email_content['Date'], "%a, %d %b %Y %X %z")
        print_info(f"Email ({date.date()} {date.strftime('%X')}): {subject}\n")
        emails.append(email_content)
    
    return emails


def download_attachments(email_message: Message, download_folder: str) -> List[str]:
    """Gets the emails with the given label.
        ## Arguments
        - `email_message`: The email message (instance of Message class) used to download its attachments.
        - `download_folder`: The path to the folder where attachments will be downloaded.
        
        ## Example
            >>> email = email.message.Message() 
            >>> download_attachments(email, 'path_to_folder')
        
        ## Returns
        - A list of the downloaded file names.
    """
    safe_mkdir(download_folder)
    files_names: List[str] = []
    for part in email_message.walk():
        if (
            part.get_content_maintype() == 'multipart' or 
            part.get('Content-Disposition') is None        
        ):
            continue
        
        
        
        file_name = part.get_filename()
        if bool(file_name):
            print(f"Downloading {file_name} ...")
            file_path = os.path.join(download_folder, file_name)
            if os.path.isfile(file_path):
                print_success("File already downloaded.")
                continue
            fp = open(file_path, 'wb')
            with fp:
                if file_path.endswith('.csv') or file_path.endswith('.txt'):
                    content = part.get_payload(decode=True)
                    content = content.decode('latin-1')
                    fp.write(str.encode(content))                   
                else :
                    fp.write(part.get_payload(decode=True))
            files_names.append(file_name)
            print_success(f"File downloaded successfully: {file_name}")
        
    return files_names
