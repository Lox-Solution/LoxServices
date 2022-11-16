"""Sending static emails via Postmark"""
import base64
import json
import os
from typing import List

import requests

from lox_services.config.env_variables import get_env_variable


def send_email_via_postmark(
    *_,
    sender: str,
    receivers: List[str],
    template_alias: str,
    ccs: List[str] = [],
    bccs: List[str] = [],
    template_model: dict = {},
    attachments: List[str] = [],
    tag: str = None,
    track_opens: bool = True,
    track_links: str = None,
    api_token: str = None,
):
    """Sends an email via Postmark. POSTMARK_API_TOKEN environment variable can be set or passed as parameter.
        Cf documentation: https://postmarkapp.com/developer/api/templates-api#email-with-template
        
        ## Arguments
        - `sender`: Email address of the sender (used as login).
        - `receivers`: List of the emails of the receivers.
        - `ccs`: List of the emails added to copy of this email.
        - `bccs`: List of the emails added to hidden copy of this email.
        - `template_alias`: Alias of the template to use (not the id!).
        - `template_model`: Dictionary of the template model to use.
        - `attachments`: List of the locals absolutes paths of files to send in the email.
        - `tag`: Tag to add to the email.
        - `track_opens`: Boolean to track the opens of the email.
        - `track_links`: String to track the links of the email.
        - `api_token`: Postmark API token. If not passed, will look for POSTMARK_API_TOKEN environment variable.
        
        ## Returns
        - The response of the request.
        
        ## Example
        >>> send_email_via_postmark(
            sender="sender@email.com",
            receivers=["receiver@email.com"],
            template_alias="template-alias-en",
            template_model={
                "firstname": "John",
                "lastname": "Doe",
            },
        )
    """
    
    attachments_objects = []
    for attachment in attachments:
        with open(attachment, 'rb') as file:
            attachments_objects.append({
                'Name': os.path.basename(attachment),
                'Content': base64.b64encode(file.read()).decode('utf-8'),
                'ContentType': 'application/text',
            })
    
    body=json.dumps({
        "From": sender,
        "To": ",".join(receivers),
        "TemplateAlias": template_alias,
        "TemplateModel": template_model,
        "Cc": ",".join(ccs) if ccs else None,
        "Bcc": ",".join(bccs) if bccs else None,
        "Tag": tag,
        "TrackOpens": track_opens,
        "TrackLinks": track_links,
        "Attachments": attachments_objects
    })
    
    postmark_api_token = api_token if api_token else get_env_variable('POSTMARK_API_TOKEN')
    result = requests.post(
        url="https://api.postmarkapp.com/email/withTemplate",
        headers={
            "Accept": "application/json",
            "X-Postmark-Server-Token": postmark_api_token,
        },
        data=body,
    )
    
    return result
