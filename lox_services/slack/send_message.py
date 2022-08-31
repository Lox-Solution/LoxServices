import json
import sys
import requests

from lox_services.config.env_variables import get_env_variable

RUNS_REPORTS=get_env_variable('RUNS_REPORTS')
RUNS_REPORTS_DEV=get_env_variable('RUNS_REPORTS_DEV')

def send_messages(message: str , title : str):
    "Send a slack message to run-report channel  "
    if get_env_variable("ENVIRONMENT") == 'development':
        url = f"https://hooks.slack.com/services/{RUNS_REPORTS_DEV}"
    else:
        url = f"https://hooks.slack.com/services/{RUNS_REPORTS}"
    
    slack_data = {
        "username": "NotificationBot",
        "icon_emoji": ":satellite:",
        #"channel" : "#somerandomcahnnel",
        "attachments": [{
            "color": "#F3421C",
            "fields": [{
                "title": title,
                "value": message,
                "short": "false",
            }]
        }]
    }
    
    byte_length = str(sys.getsizeof(slack_data))
    headers = {'Content-Type': "application/json", 'Content-Length': byte_length}
    response = requests.post(url, data=json.dumps(slack_data), headers=headers)

    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
