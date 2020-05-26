# Database structure

## Tables
#### Users
* identity: `str`- primary key
* user_id: `str`
* service: `str`
* via_instance: `str`
* first_name: `str`
* last_name: `str`
* username: `str`
* language: `str`
* type: `int` (AccountType)
* created_at: `str`
* last_location: `str` (coordinates)
* last_active: `str`
* conversation_id: `str`
* answers: `dict`
* states: `list`
* context: `dict`


#### Conversations
* id: `str`- primary key
* users: `dict` ({'$identity1': '$identity2', '$identity2': '$identity1'})
* type: `int` (AccountType)
* created_at: `str`


#### ConversationRequests
* identity: `str`- primary key
* type: `int` (AccountType)
* created_at: `str`


#### CheckBacks
* id: `str`
* server_mac: `str`
* identity: `str`
* context: `dict`
* send_at: `str`


#### Session
* name: `str` - primary key
* token: `str`
* url: `str`
* broadcast: `Optional[int]`
* psychological_room: `Optional[int]`
* doctor_room: `Optional[int]`


#### BroadcastMessage
* id: `str` - primary key
* context: `str`


#### TranslationItem
* text: `str`
* language: `str`
* result_text: `str`
* result_language: `str`


#### Message
> probably worth saving all messages, if we ever plan to train rasa models
* identity: `str` - primary key
* text: `str`
