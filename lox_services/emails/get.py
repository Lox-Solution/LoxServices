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
    mailbox: str,
    days: int = 1,
    *,
    search: GmailSearchOperators = {},
    strict=False,
    search_from_current_date=True,
) -> List[Message]:
    """Gets the emails with the given label.
    ## Arguments
    - `mailbox`: The label to use to filter the emails.
    - `delta_days`: The number of days to look for in the past.
    - `filter`: The filter to use to filter the emails.
    - `strict`: If True, the filter will be strict, meaning that the filter will be used as is.
    - `search_from_current_date`: If True, the search will be done from the current date.

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

    if search_from_current_date:
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


def extract_email_details(
    email: dict,
) -> Tuple[dict, str, List[str], List[str], List[str]]:
    """
    Extracts relevant details from the email.

    Args:
        email (dict): The email dictionary.

    Returns:
        Tuple: The email, message_id, sender(s), receiver(s), and cc(s).
    """
    message_id = email.get("Message-ID", "")

    # Extract sender email
    sender_email = email.get("From", "")
    _, sender_email = parseaddr(sender_email)

    # Extract receiver email (preferring "Reply-To" if available)
    full_address = email.get("Reply-To", email.get("To", ""))
    _, receiver_email = parseaddr(full_address)

    # Extract CC emails
    cc_addresses = email.get("Cc", "")
    cc_emails = [addr for _, addr in getaddresses([cc_addresses])]

    return email, message_id, [sender_email], [receiver_email], cc_emails


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
    datetime_original_message: Optional[datetime] = None,
    email_from: Optional[str] = None,
    subject: Optional[str] = None,
    label: Optional[str] = "INBOX",
    fallback: bool = False,
) -> Tuple[
    Optional[dict],
    Optional[str],
    Optional[List[str]],
    Optional[List[str]],
    Optional[List[str]],
]:
    """
    Find an email by matching the date and subject.

    Args:
        datetime_original_message (Optional[datetime]): The datetime of the original message.
        email_from (str): The email address of the sender.
        subject (Optional[str]): The subject of the email to search for.
        label (Optional[str]): The mailbox label to search in. Defaults to "INBOX".
        fallback (bool): If True, finds the closest email if an exact match is not found.

    Returns:
        Tuple: The email, message_id for threading, sender's email(s), receiver's email(s), and CC email(s).
    """

    search_criteria = {}

    # If a specific date is provided, search for that exact day
    if datetime_original_message:
        search_criteria["ON"] = datetime_original_message.strftime("%d-%b-%Y")
        days_to_search = 1  # Search only that day
        search_from_current_date = False
    else:
        days_to_search = 15
        search_from_current_date = True

    # Add optional sender and subject filters
    if email_from:
        search_criteria["FROM"] = email_from
    if subject:
        search_criteria["SUBJECT"] = subject

    print(f"Search criteria: {search_criteria}")

    # Fetch emails based on the search criteria
    emails = get_emails(
        mailbox=label,
        days=days_to_search,
        search=search_criteria,
        search_from_current_date=search_from_current_date,
    )

    print(f"Found {len(emails)} emails.")

    closest_email = None
    closest_time_diff = None

    for email in emails:
        # Parse email date
        email_datetime = datetime.strptime(
            email["Date"], "%a, %d %b %Y %H:%M:%S %z"
        ).replace(tzinfo=None)

        # If an exact date was provided, check for exact match
        if datetime_original_message:
            time_diff = abs(
                (email_datetime - datetime_original_message).total_seconds()
            )
            if email_datetime == datetime_original_message:
                return extract_email_details(email)
        else:
            time_diff = 0  # Skip time comparison for the 15-day search

        # Track closest email if fallback is enabled
        if closest_time_diff is None or time_diff < closest_time_diff:
            closest_time_diff = time_diff
            closest_email = email

    # Return the closest email if fallback is enabled
    if fallback and closest_email:
        print("Fallback: Returning the closest matching email.")
        return extract_email_details(closest_email)

    return None, None, None, None, []
