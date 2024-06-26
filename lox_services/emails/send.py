"""
All send email functions
"""

import os
import smtplib
import lxml.html
import pandas as pd
from enum import Enum
from typing import Dict, List

from email import encoders
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from lox_services.config.env_variables import get_env_variable
from lox_services.emails.utils import (
    generate_oauth2_string,
    refresh_authorization,
    get_google_client_id,
)
from lox_services.utils.general_python import get_file_size, print_success

LOX_TEAM_EMAIL = get_env_variable("LOX_TEAM_EMAIL")
LOX_FINANCE_EMAIL = get_env_variable("LOX_FINANCE_EMAIL")

REFRESH_KEYS_LOX_ACCOUNTS = {
    LOX_TEAM_EMAIL: "LOXTEAM_REFRESH_TOKEN",
    LOX_FINANCE_EMAIL: "FINANCE_REFRESH_TOKEN",
}
LOX_ACCOUNTS = [LOX_TEAM_EMAIL, LOX_FINANCE_EMAIL]


class ContentTypes(Enum):
    """Enumeration of all email content types"""

    HTML = "html"
    STRING = "string"


def attach_images(msg: MIMEMultipart, images: Dict[str, str]) -> None:
    """
    Attaches images to an email message.

    Args:
        msg (MIMEMultipart): The email message to which images will be attached.
        images (Dict[str, str]): A dictionary where the key is the Content-ID of the image, and the value is the path to the image file.

    Example:
        >>> msg = MIMEMultipart()
        >>> images = {"image1": "/path/to/image1.png", "image2": "/path/to/image2.png"}
        >>> attach_images(msg, images)
    """
    for cid, path in images.items():
        with open(path, "rb") as img_file:
            msg_image = MIMEImage(img_file.read())
            msg_image.add_header("Content-ID", f"<{cid}>")
            msg.attach(msg_image)


def send_email(
    *,
    sender_email_address: str,
    sender_smtp_server: str = "smtp.gmail.com:587",  # Default is google
    sender_password: str,
    receiver_email_address: str,
    cc_email_addresses: List[str] = [],
    bcc_email_addresses: List[str] = [],
    subject: str,
    content: str,
    content_type: ContentTypes = ContentTypes.STRING,
    attachments: List[str] = [],
):
    """Send an email with subject, content, and attachments.
    ## Arguments
    - `sender_email_address`: Email address of the sender (used as login).
    - `sender_smtp_server`: The server of the email sender. Look on the internet to get it.
    - `sender_password`: The password of the email address.
    - `receiver_email_address`: Email address of the receiver.
    - `cc_email_addresses`: List of the emails added to copy of this email
    - `bcc_email_addresses`: List of the emails added to hidden copy of this email
    - `subject`: Subject of the email.
    - `content`: Message content of the email. Can be a string representing HTML.
    - `content_type`: Type of the content. Used to differ html from string email.
    - `attachments`: List of the locals absolutes paths of files to send to the receiver.

    ## Example
        >>> send_email(
            "loxteam@loxsolution.com",
            "dummy@gmail.com",
            "Dummy subject",
            "Dummy content",
            ["absolute_path/dummy.csv", "absolute_path/dummy.pdf"]
        )

    ## Returns
    - True if the email was sent successfully
    - False otherwise
    """
    email_object = MIMEMultipart()
    email_object["From"] = sender_email_address
    email_object["To"] = receiver_email_address
    email_object["Subject"] = subject
    # CC
    cc_email_addresses = list(
        filter(lambda element: element is not None, cc_email_addresses)
    )
    if len(cc_email_addresses) > 0:
        email_object["Cc"] = ", ".join(cc_email_addresses)
    # BCC
    bcc_email_addresses = list(
        filter(lambda element: element is not None, bcc_email_addresses)
    )
    if len(bcc_email_addresses) > 0:
        email_object["Bcc"] = ", ".join(bcc_email_addresses)

    if content_type == ContentTypes.HTML:
        part_html = MIMEText(content.encode("utf-8"), "html", _charset="utf-8")
        email_object.attach(part_html)
    else:
        email_object.attach(MIMEText(content, "plain"))

    if len(attachments) > 0:
        for attachment in attachments:
            filename = os.path.basename(attachment)
            attachment = open(attachment, "rb")
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f"attachment; filename= {filename}")
            email_object.attach(part)

    try:
        server = smtplib.SMTP(sender_smtp_server)
        server.ehlo()
        server.starttls()
        server.login(sender_email_address, sender_password)
        text = email_object.as_string()
        server.sendmail(sender_email_address, receiver_email_address, text)
        print(f"Email sent from {sender_email_address}, to {receiver_email_address}.")
        server.quit()
        return True
    except Exception:
        print(f"SMPT server connection error (sender: {sender_email_address}).")
        return False


def send_emails_from_loxsolution_account(
    *,
    sender_email_address: str = LOX_TEAM_EMAIL,
    receiver_email_addresses: List[str],
    reply_to_email_address: str = None,
    cc_email_addresses: List[str] = [],
    bcc_email_addresses: List[str] = [],
    subject: str,
    content: str,
    attachments: List[str] = [],
    images: Dict[str, str] = {},
):
    """Uses Oauth2 tokens to send the email from Loxteam account.
    ## Arguments
    - `sender_email_adress`: The email of the sender. We must have the refresh token stored in the env variables.
    - `receiver_email_addresses`: Email address of the receiver.
    - `reply_to_email_address`: Email address to reply to.
    - `subject`: Subject of the email.
    - `content`: Message content of the email. Can be a string representing HTML.
    - `attachments`: List of the locals absolutes paths of files to send to the receiver.
    - `cc_email_addresses`: List of the emails added to copy of this email
    - `bcc_email_addresses`: List of the emails added to hidden copy of this email
    - `images`: Dictionary of the images to attach to the email. The key is the cid and the value is the path of the image.

    ## Example
        >>> send_email_from_loxsolution_account(
            ["alexandre.girbal@loxsolution.com"],
            "Dummy subject",
            "Dummy content",
            ["/home/alexandre/Downloads/vue.JPG", "absolute_path/dummy.pdf"]
        )

    ## Returns
    - Nothing if no exception is raised.
    - Raises an exception otherwise.
    """
    if sender_email_address not in LOX_ACCOUNTS:
        raise ValueError(
            "Sender's email address is invalid. Valid emails at the moment are team and finance emails."
        )
    print(
        f"{sender_email_address} is sending an email to {receiver_email_addresses} ..."
    )
    print(
        f"Subject: {subject}\nccs: {cc_email_addresses}\nbccs: {bcc_email_addresses} ..."
    )
    refresh_key = REFRESH_KEYS_LOX_ACCOUNTS[sender_email_address]
    access_token = refresh_authorization(get_env_variable(refresh_key))
    auth_string = generate_oauth2_string(
        sender_email_address, access_token, as_base64=True
    )

    msg = MIMEMultipart("related")
    msg["Subject"] = subject
    msg["From"] = sender_email_address
    msg["To"] = ", ".join(receiver_email_addresses)
    if reply_to_email_address:
        msg["Reply-To"] = reply_to_email_address

    # CC
    cc_email_addresses = list(
        filter(lambda element: element is not None, cc_email_addresses)
    )
    if len(cc_email_addresses) > 0:
        msg["Cc"] = ", ".join(cc_email_addresses)
    # BCC
    bcc_email_addresses = list(
        filter(lambda element: element is not None, bcc_email_addresses)
    )
    if len(bcc_email_addresses) > 0:
        msg["Bcc"] = ", ".join(bcc_email_addresses)

    msg.preamble = "This is a multi-part message in MIME format."
    msg_alternative = MIMEMultipart("alternative")
    msg.attach(msg_alternative)
    part_text = MIMEText(
        lxml.html.fromstring(content).text_content().encode("utf-8"),
        "plain",
        _charset="utf-8",
    )
    part_html = MIMEText(content.encode("utf-8"), "html", _charset="utf-8")
    msg_alternative.attach(part_text)
    msg_alternative.attach(part_html)

    # Attach images
    for cid, path in images.items():
        with open(path, "rb") as img_file:
            msg_image = MIMEImage(img_file.read())
            msg_image.add_header("Content-ID", f"<{cid}>")
            msg.attach(msg_image)

    # Attach other attachments
    for attachment_path in attachments:
        if pd.isna(attachment_path):
            continue
        filename = os.path.basename(attachment_path)
        file_size, unit = get_file_size(attachment_path)
        print(f"Attaching '{filename}' ({file_size} {unit}) ...")
        attachment = open(attachment_path, "rb")
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename= {filename}")
        msg_alternative.attach(part)

    server = smtplib.SMTP("smtp.gmail.com:587")
    server.ehlo(get_google_client_id())
    server.starttls()
    server.docmd("AUTH", "XOAUTH2 " + auth_string)
    server.send_message(msg)
    print_success("Email sent successfully.")
    server.quit()
