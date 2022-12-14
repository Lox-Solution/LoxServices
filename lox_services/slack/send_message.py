import json
import sys
import requests

from lox_services.config.env_variables import get_env_variable

def send_messages(message: str , title : str):
    "Send a slack message to run-report channel  "
    if get_env_variable("ENVIRONMENT") == 'production':
        url = f'https://hooks.slack.com/services/{get_env_variable("RUNS_REPORTS")}'
    else:
        url = f'https://hooks.slack.com/services/{get_env_variable("RUNS_REPORTS_DEV")}'    

    slack_data = {
        "username": "NotificationBot",
        "text": f"{title} {message}"
    }
    byte_length = str(sys.getsizeof(slack_data))
    headers = {'Content-Type': "application/json", 'Content-Length': byte_length}
    response = requests.post(url, data=json.dumps(slack_data), headers=headers)
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)

