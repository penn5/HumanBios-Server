from .typing_hints import User, ConversationRequest, Conversation, CheckBack, Optional
from settings.settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
from boto3.dynamodb.conditions import Key, Attr
from server_logic.definitions import Context
from botocore.exceptions import ClientError
from .create_db import create_db
from .enums import AccountType
import datetime
import boto3
import pytz
import uuid


# TODO: Probably worth it to switch to async solution eventually but
# TODO: right now, it's just PoC solution
class DataBase:
    types = AccountType
    _initialized = False
    __instance = None
    LIMIT_CONCURRENT_CHATS = 100
    TZ = pytz.utc

    def __init__(self, database_url="http://localhost:8000", region_name='eu-center-1'):
        self.dynamodb = boto3.resource(
            'dynamodb',
            region_name=region_name,
            endpoint_url=database_url,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY
        )
        # Create db tables
        create_db(self.dynamodb)
        self.Users = self.dynamodb.Table('Users')
        self.Conversations = self.dynamodb.Table('Conversations')
        self.ConversationRequests = self.dynamodb.Table('ConversationRequests')
        self.CheckBacks = self.dynamodb.Table('CheckBacks')
        # Cache
        self.active_conversations = 0
        self.requested_users = set()

        DataBase._initialized = True

    # High level methods

    # User methods
    async def create_user(self, item: User):
        """Creates User item in the according table"""
        self.Users.put_item(
            Item=item
        )

    async def get_user(self, identity: str) -> Optional[User]:
        """Returns User item by the user identity"""
        try:
            response = self.Users.get_item(
                Key={
                    'identity': identity
                }
            )
        except ClientError as e:
            # TODO: @Important: Change all prints to logger.info or .error
            # Print Error Message and return None
            print(e.response['Error']['Message'])
        else:
            # If not exist -> return None
            if not response.get('Item'):
                return
            # Return just item
            return response['Item']

    async def update_user(self, identity: str, expression: str, values: Optional[dict], user: User = None) -> Optional[User]:
        response = self.Users.update_item(
            Key={
                'identity': identity
            },
            UpdateExpression=expression,
            ExpressionAttributeValues=values,
            ReturnValues="UPDATED_NEW"
        )
        if user is not None:
            # This is.. uh (since database returns only new value, not full object)
            for key, new_value in response['Attributes'].items():
                user[key] = new_value  # ignore warning
            return user

    async def commit_user(self, user: User):
        self.Users.put_item(Item=user)

    # Conversation Requests

    # TODO: @Important: Still make methods async for now, because we don't
    # TODO: @Important: want to rewrite the code in all states etc.
    async def create_request(self, identity: str, type_: types):
        """Creates ConversationRequest item in the according table"""
        if identity in self.requested_users:
            raise ValueError("Identity is already in the conversation!")
        self.requested_users.add(identity)
        self.ConversationRequests.put_item(
            Item={
                "identity": identity,
                "type": type_,
                # @Important: 1) DynamoDB do not support `datetime` type
                # @Important: 2) We can use `>` operator on iso-formatted string, because
                # @Important:    structure of it is correct for left-to-right char comparison
                "created_at": datetime.datetime.now(self.TZ).isoformat()
            }
        )

    async def get_request_by_user(self, identity: str):
        """Returns ConversationRequest item by the user identity"""
        try:
            response = self.ConversationRequests.get_item(
                Key={
                    'identity': identity
                }
            )
        except ClientError as e:
            # TODO: @Important: Change all prints to logger.info or .error
            # Print Error Message and return None
            print(e.response['Error']['Message'])
        else:
            # Return just item
            return response['Item']

    async def del_request_by_user(self, identity: str):
        """Remove ConversationRequest item by the user identity"""
        self.requested_users.remove(identity)
        try:
            response = self.ConversationRequests.delete_item(
                Key={
                    'identity': identity
                }
            )
        except ClientError as e:
            # @Important: This exception is not really an error, just says that if we entered
            # @Important: some condition to check, before deleting item - the condition failed
            if e.response['Error']['Code'] == "ConditionalCheckFailedException":
                print(e.response['Error']['Message'])
            else:
                raise
        else:
            #print("Delete ConversationRequest succeeded: ")
            pass

    async def get_waiting_requests(self, waiting: datetime.timedelta):
        now = self.now()
        condition = now - waiting
        response = self.ConversationRequests.query(
            FilterExpression="created_at > :c_at",
            ExpressionAttributeNames={
                ":c_at": {"S": condition.isoformat()}
            }
        )
        # TODO: FINISH (add return with unpacked results and update `.requested_users` set with latest data)

    def has_user_request(self, identity: str):
        return identity in self.requested_users

    def conversations_limit_reached(self):
        """Returns True if the number of current active conversations exceed the defined limit"""
        return self.active_conversations >= self.LIMIT_CONCURRENT_CHATS

    def now(self) -> datetime.datetime:
        return datetime.datetime.now(self.TZ)

    async def create_checkback(self, user: User, context: Context, send_in: datetime.timedelta):
        """Creates Checkback item in the according table"""
        self.CheckBacks.put_item(
            Item={
                "identity": context['request']['user']['identity'],
                "context": (context.deepcopy()).to_dict(),
                "send_at": (self.now() + send_in).isoformat()
            }
        )

    async def all_in_range(self, now: datetime.datetime, until: datetime.datetime):
        response = self.CheckBacks.query(
            FilterExpression="send_at >= :now and send_at <= :until",
            ExpressionAttributeNames={
                ":now": {"S": now.isoformat()},
                ":until": {"S": until.isoformat()}
            }
        )
        return response['Items']