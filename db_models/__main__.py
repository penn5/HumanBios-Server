# This module creates database (DynamoDB)
from settings.settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
import boto3

dynamodb = boto3.resource('dynamodb', region_name='eu-center-1',
                          endpoint_url="http://dynamodb-local:8000",
                          aws_access_key_id=AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

try:
    table1 = dynamodb.create_table(
        TableName='Users',
        KeySchema=[
            {
                'AttributeName': 'identity',
                'KeyType': 'HASH'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'identity',
                'AttributeType': 'S'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 1,
            'WriteCapacityUnits': 1
        }
    )
except Exception as e:
    print(e)
    table1 = None

try:
    table2 = dynamodb.create_table(
        TableName='Conversations',
        KeySchema=[
            {
                'AttributeName': 'id',
                'KeyType': 'HASH'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'id',
                'AttributeType': 'S'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 1,
            'WriteCapacityUnits': 1
        }
    )
except Exception as e:
    print(e)
    table2 = None

try:
    table3 = dynamodb.create_table(
        TableName='ConversationRequests',
        KeySchema=[
            {
                'AttributeName': 'identity',
                'KeyType': 'HASH'
            },
            {
                "AttributeName": "created_at",
                "KeyType": "RANGE"
            }
        ],
        AttributeDefinitions=[
            {
                'Attribute'
                'Name': 'identity',
                'AttributeType': 'S'
            },
            {
                "AttributeName": "created_at",
                "AttributeType": "S"
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 1,
            'WriteCapacityUnits': 1
        }
    )
except Exception as e:
    print(e)
    table3 = None

try:
    table4 = dynamodb.create_table(
        TableName='CheckBacks',
        KeySchema=[
            {
                'AttributeName': 'identity',
                'KeyType': 'HASH'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'identity',
                'AttributeType': 'S'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 1,
            'WriteCapacityUnits': 1
        }
    )
except Exception as e:
    print(e)
    table4 = None

print("Table statuses:", ', '.join([x.table_status for x in (table1, table2, table3, table4) if x]))