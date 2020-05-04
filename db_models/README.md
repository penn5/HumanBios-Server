# Database structure

## Message
> probably worth saving all messages, if we ever plan to train rasa models
* text: `str`
* user: `User`

## User
* user_id: `str`
* service: `str`
* identity: `str`
* via_instance: `str`
* first_name: `str`
* last_name: `str`
* username: `str`
* language: `str`
* type: `int` (MEDIC, SOCIAL, PATIENT)
* created_at: `datetime`
* last_location: `str` (coordinates)

## Resume
* answers: `Answer`
* user: `User`

## Answer
* text: `str`
* file: `str` (file id, file path, etc)

## State
* name: `str`
* user: `User`

## Conversation
> I don't like the naming but, uh.. user-worker is worse, because potentially we may want user-user conversations
* user1: `User`
* user2: `User`
* type: `int` (MEDICAL, SOCIAL, COMMON)
* created_at: `datetime`
* status: `int` (FINISHED, ON-GOING)

## ConversationRequest
* user: `User`
* type: `int` (MEDICAL, SOCIAL, COMMON)
* created_at: `datetime`
* resolved_at: `datetime`