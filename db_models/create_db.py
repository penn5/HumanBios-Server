from botocore.exceptions import ClientError


class TableStatus:
    def __init__(self, name: str, status: str = None):
        self.status = status
        self.name = name

    def __repr__(self):
        return f"{self.name}: {self.status}"


def create_db(dynamodb):
    statuses = list()

    status = TableStatus('Users')
    try:
        table = dynamodb.create_table(
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
        status.status = table.table_status
    except ClientError as e:
        if e.response['Error']['Code'] == "ResourceInUseException":
            status.status = "ALREADY EXISTS"
        else:
            raise e
    statuses.append(status)

    status = TableStatus('Conversations')
    try:
        table = dynamodb.create_table(
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
        status.status = table.table_status
    except ClientError as e:
        if e.response['Error']['Code'] == "ResourceInUseException":
            status.status = "ALREADY EXISTS"
        else:
            raise e
    statuses.append(status)

    status = TableStatus('ConversationRequests')
    try:
        table = dynamodb.create_table(
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
        status.status = table.table_status
    except ClientError as e:
        if e.response['Error']['Code'] == "ResourceInUseException":
            status.status = "ALREADY EXISTS"
        else:
            raise e
    statuses.append(status)

    status = TableStatus('CheckBacks')
    try:
        table = dynamodb.create_table(
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
        status.status = table.table_status
    except ClientError as e:
        if e.response['Error']['Code'] == "ResourceInUseException":
            status.status = "ALREADY EXISTS"
        else:
            raise e
    statuses.append(status)

    print("Table statuses:", ', '.join(str(x) for x in statuses))