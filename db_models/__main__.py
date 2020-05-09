# This module creates database (DynamoDB)
import boto3

dynamodb = boto3.resource('dynamodb', region_name='eu-center-1', endpoint_url="http://localhost:8000")


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

print("Table statuses:", ', '.join([x.table_status for x in (table1, table2, table3, table4)]))