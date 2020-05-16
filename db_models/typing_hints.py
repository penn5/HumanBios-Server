from typing import TypedDict, Dict, Union, List, Optional, Any
from .enums import AccountType
from datetime import datetime


class User(TypedDict):
    identity: str
    user_id: str
    service: str
    via_instance: str
    first_name: str
    last_name: str
    username: str
    language: str
    conversation_id: Optional[str]
    created_at: str
    last_location: Optional[str]
    last_active: str
    answers: Dict[str, Any]
    files: Dict[str, Union[str, list]]
    states: List[str]
    type: AccountType
    context: Dict[str, Any]


class Conversation(TypedDict):
    id: str
    users: Dict[str, str]
    type: AccountType
    created_at: str


class ConversationRequest(TypedDict):
    identity: str
    type: AccountType
    created_at: str


class CheckBack(TypedDict):
    id: str
    server_mac: str
    identity: str
    context: str
    send_at: str
