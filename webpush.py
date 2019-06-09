import requests
import json

import config
from db import get_push_subscribers

send_url = "https://fcm.googleapis.com/fcm/send"


def send_web_push(payload):
    headers = {'Authorization': 'key={}'.format(config.fcm_key),
               'Content-Type': 'application/json'}
    body = {
        "notification": {
            "title": 'New event created: ' + payload['title']
        }
    }
    tokens = get_push_subscribers(payload)
    for token in tokens:
        body["to"] = token
        requests.post(send_url, data=json.dumps(body), headers=headers)
        print(token)


if __name__ == '__main__':
    send_web_push()

