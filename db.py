import os
import boto3
from boto3.dynamodb.conditions import Key, Attr
import OldTokenNotFoundException

FCM_TOKEN = 'fcm_token'
USERNAME = 'username'
GROUP_NAME = 'group_name'

boto3.setup_default_session(
    region_name='eu-central-1',
    aws_access_key_id="todo",
    aws_secret_access_key="todo"
)
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('cms_subscribers')


def save_registration(username, groups, fcm_token):
        table.put_item(
        Item={
            FCM_TOKEN: fcm_token,
            USERNAME: username,
            GROUP_NAME: groups
        }
    )


def update_registration(old_token, new_token):
    response = find_registration_by_id(old_token)
    if response['Count'] != 1:
        raise OldTokenNotFoundException
    record = response['Items'][0]
    delete_registration(old_token)
    save_registration(record[USERNAME], record[GROUP_NAME], new_token)


def find_registration_by_id(fcm_token):
    return table.query(
        KeyConditionExpression=Key(FCM_TOKEN).eq(fcm_token)
    )


def delete_registration(fcm_token):
    table.delete_item(
        Key={
            FCM_TOKEN: fcm_token,
        }
    )


def get_push_subscribers(event):
    users = list(map(lambda user: table.scan(
        FilterExpression=Attr(USERNAME).eq(user)
    )['Items'], event['users']))
    groups = list(map(lambda group: table.scan(
        FilterExpression=Attr(GROUP_NAME).eq(group)
    )['Items'], event['groups']))
    items = []
    for l in [i for i in users] + [i for i in groups]:
        for x in l:
            items.append(x)
    fcm_tokens = list(map(lambda x: x[FCM_TOKEN], items))
    fcm_tokens = list(set(fcm_tokens))
    print(fcm_tokens)
    return fcm_tokens
