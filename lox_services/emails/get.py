"""All functions related to email fetching."""

import email
from email.utils import parseaddr, getaddresses
import imaplib
import os
from datetime import datetime, timedelta
from email import policy
from email.message import Message
from typing import List, TypedDict, Tuple, Optional
from lox_services.config.env_variables import get_env_variable
from lox_services.emails.utils import generate_oauth2_string, refresh_authorization
from lox_services.utils.general_python import print_info, print_success, safe_mkdir


class GmailSearchOperators(TypedDict):
    """Some of Gmail operators to use in email searches.
    https://support.google.com/mail/answer/7190?hl=en
    """

    subject: str


def get_emails(
    mailbox: str, days: int = 1, *, search: GmailSearchOperators = {}, strict=False
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
    imap_ssl_client = imaplib.IMAP4_SSL("imap.gmail.com")
    imap_ssl_client.debug = 4

    access_token = refresh_authorization(get_env_variable("LOXTEAM_REFRESH_TOKEN"))
    auth_string = generate_oauth2_string(
        get_env_variable("LOX_TEAM_EMAIL"), access_token
    )

    imap_ssl_client.authenticate("XOAUTH2", lambda x: auth_string)
    labeled_status, labeled_emails = imap_ssl_client.select(mailbox)
    if labeled_status != "OK":
        raise ValueError("Invalid label value.")

    # Generating search criterias
    search_criterias = ""

    max_date = (datetime.today() - timedelta(days)).strftime("%d-%b-%Y")
    date_criteria = f"SENTSINCE {max_date} "
    search_criterias += date_criteria

    for key, value in search.items():
        string_value = f'"{value}"' if strict else value.replace(" ", "-")
        search_criterias += f"{str(key).upper()} {string_value} "

    print_info(f"Search criterias: {search_criterias}")
    status, emails_bytes = imap_ssl_client.search(None, f"({search_criterias.strip()})")
    if status != "OK":
        print("No emails found!")
        return

    emails_numbers_bytes = emails_bytes[0].split()

    emails: List[Message] = []
    for index_byte in emails_numbers_bytes:
        status, data_bytes = imap_ssl_client.fetch(index_byte, "(BODY.PEEK[])")
        if status != "OK":
            raise Exception(
                "An unknown error occured while trying to fetch email body."
            )

        email_content_bytes = data_bytes[0][1]
        email_content = email.message_from_bytes(
            email_content_bytes, policy=policy.default
        )  # policy.default is very important, it's decoding "encoded-word" subjects https://stackoverflow.com/questions/12903893/python-imap-utf-8q-in-subject-string
        subject = str(email_content["Subject"])
        date = datetime.strptime(email_content["Date"], "%a, %d %b %Y %X %z")
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
            part.get_content_maintype() == "multipart"
            or part.get("Content-Disposition") is None
        ):
            continue

        file_name = part.get_filename()
        if bool(file_name):
            print(f"Downloading {file_name} ...")
            file_path = os.path.join(download_folder, file_name)
            if os.path.isfile(file_path):
                print_success("File already downloaded.")
                continue
            fp = open(file_path, "wb")
            with fp:
                if file_path.endswith(".csv") or file_path.endswith(".txt"):
                    content = part.get_payload(decode=True)
                    content = content.decode("latin-1")
                    fp.write(str.encode(content))
                else:
                    fp.write(part.get_payload(decode=True))
            files_names.append(file_name)
            print_success(f"File downloaded successfully: {file_name}")

    return files_names


def get_email_with_datetime_and_subject(
    datetime_original_message: datetime,
    email_from: Optional[str] = None,
    subject: Optional[str] = None,
    label: Optional[str] = "INBOX",
    fallback: bool = False,
) -> Tuple[
    Optional[dict],
    Optional[str],
    Optional[str],
    Optional[List[str]],
    Optional[List[str]],
]:
    """
    Find an email by matching the date and subject.

    Args:
        datetime_original_message (datetime): The datetime of the original message.
        email_from (str): The email address of the sender.
        subject (Optional[str]): The subject of the email to search for. Defaults to None.

    Returns:
        Tuple: The email, message_id for threading, the sender's email address, the receiver's email address, and the list of Cc email addresses.
    """
    search_criteria = {}
    if email_from:
        search_criteria["from"] = email_from
    if subject:
        search_criteria["subject"] = subject

    emails = get_emails(
        label,
        60,
        search=search_criteria,
    )
    print(f"Found {len(emails)} emails.")

    closest_email = None
    closest_time_diff = None

    for email in emails:
        df_datetime = datetime_original_message
        email_datetime = datetime.strptime(email["Date"], "%a, %d %b %Y %H:%M:%S %z")

        # Remove the timezone information from the email datetime
        email_datetime_naive = email_datetime.replace(tzinfo=None)

        time_diff = abs((email_datetime_naive - df_datetime).total_seconds())

        if email_datetime_naive == df_datetime:
            message_id = email["Message-ID"]  # Get Message-ID for threading

            # Extract the sender's email address
            sender_email = email["From"]
            _, sender_email = parseaddr(sender_email)

            # Extract the email address from the "From" or "Reply-To" field
            full_address = email.get("Reply-To", email["To"])
            _, receiver_email = parseaddr(full_address)

            # Extract email addresses from the "Cc" field
            cc_addresses = email.get("Cc", "")
            cc_emails = [addr for _, addr in getaddresses([cc_addresses])]

            return email, message_id, [sender_email], [receiver_email], cc_emails
        else:
            if closest_time_diff is None or time_diff < closest_time_diff:
                closest_time_diff = time_diff
                closest_email = email

    if fallback and closest_email:
        print("Fallback to the closest email.")
        message_id = closest_email["Message-ID"]  # Get Message-ID for threading

        # Extract the sender's email address
        sender_email = closest_email["From"]
        _, sender_email = parseaddr(sender_email)

        # Extract the email address from the "From" or "Reply-To" field
        full_address = closest_email.get("Reply-To", closest_email["To"])
        _, receiver_email = parseaddr(full_address)

        # Extract email addresses from the "Cc" field
        cc_addresses = closest_email.get("Cc", "")
        cc_emails = [addr for _, addr in getaddresses([cc_addresses])]

        return closest_email, message_id, [sender_email], [receiver_email], cc_emails

    return None, None, None, None, []
