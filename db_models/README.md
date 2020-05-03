### Database structure

## Message (?)
> probably worth saving all messages, if we ever plan to train rasa models

## User
* user_id: `str`
* service: `str`
* identity: `str`
* via_instance: `str`
* first_name: `str`
* last_name: `str`
* username: `str`
* language: `str`
* type: `str?` (MEDIC, SOCIAL, PATIENT)
* created_at: `datetime`
* last_location: `str` (coordinates)

## State
* name: `str`
* user: `User`

## Conversation
> I don't like the naming but, uh.. user-worker is worse, because potentially we may want user-user conversations
* user1: `User`
* user2: `User`
* type: `str?` (MEDICAL, SOCIAL, COMMON)
* created_at: `datetime`