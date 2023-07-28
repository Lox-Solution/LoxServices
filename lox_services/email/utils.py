"""
Adapted from:
https://github.com/google/gmail-oauth2-tools/blob/master/python/oauth2.py
https://developers.google.com/identity/protocols/OAuth2

1. Generate and authorize an OAuth2 (generate_oauth2_token)
2. Generate a new access tokens using a refresh token(refresh_token)
3. Generate an OAuth2 string to use for login (access_token)

This setup is for *LOX_TEAM_EMAIL*
"""

import re
from typing import List
import base64
import json
from urllib import request
from urllib import parse

from lox_services.config.env_variables import get_env_variable

GOOGLE_ACCOUNTS_BASE_URL = "https://accounts.google.com"
REDIRECT_URI = "http://localhost"


def get_google_client_id():
    return get_env_variable("EMAILSENDER_GOOGLE_CLIENT_ID")


def get_google_client_secret():
    return get_env_variable("EMAILSENDER_GOOGLE_CLIENT_SECRET")


def _command_to_url(command):
    return "%s/%s" % (GOOGLE_ACCOUNTS_BASE_URL, command)


def url_escape(text):
    return parse.quote(text, safe="~-._")


def url_format_params(params):
    param_fragments = []
    for param in sorted(params.items(), key=lambda x: x[0]):
        param_fragments.append("%s=%s" % (param[0], url_escape(param[1])))
    return "&".join(param_fragments)


def call_refresh_token(client_id, client_secret, refresh_token):
    params = {}
    params["client_id"] = client_id
    params["client_secret"] = client_secret
    params["refresh_token"] = refresh_token
    params["grant_type"] = "refresh_token"
    request_url = _command_to_url("o/oauth2/token")
    response = (
        request.urlopen(request_url, parse.urlencode(params).encode("UTF-8"))
        .read()
        .decode("UTF-8")
    )
    return json.loads(response)


def generate_oauth2_string(username, access_token, as_base64=False):
    auth_string = "user=%s\1auth=Bearer %s\1\1" % (username, access_token)
    if as_base64:
        auth_string = base64.b64encode(auth_string.encode("ascii")).decode("ascii")
    return auth_string


def refresh_authorization(refresh_token: str) -> str:
    response = call_refresh_token(
        get_google_client_id(), get_google_client_secret(), refresh_token
    )
    return response["access_token"]


def extract_emails_from_string(string: str) -> List[str]:
    """Extracts all emails from a string.
    ## Arguments
    - `string`: The string to extract emails from.

    ## Returns
    - A list of emails if any were found.
    - An empty list if no emails were found.

    ## Examples
    ```
        emails = extract_emails_from_string("My email is alexandre@domain.com")
        print(emails) # ["alexandre@domain.com"]

        no_emails = extract_emails_from_string("This is a string without emails")
        print(no_emails) # []
    ```
    ## Exceptions
    ```
        emails = extract_emails_from_string("email@domain.com--")   # double special character after email
        print(emails) # []
    ```


    """

    return re.findall(
        r"[a-z0-9](?!.*[!#$%&*+-/=?^_`}{|]{2})[a-z0-9!#$%&*+-/=?^_`}{|]{0,62}[a-z0-9]+@[a-z0-9.-]+\.[a-z0-9]+",
        string.lower(),
    )
