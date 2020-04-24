# Context schema
Context schema to refer to while developing or extending front end and back end APIs  
  
**'!' before argument means it's required**  
**'~' before the argument means it contains required argument**  
**'\*' before the argument means it might contain any arguments**  
***all others:* `Union[None, $(type)]`**

If **any** of the required arguments is not specified, server will return **403**.  

Surely, might be changed at any point during production stage, so before writing responses look here to see relevant info.

```
{
  'request': {
    !  'service_in': str,
    !  'service_out': str,
    ~  'user': {
    !           'user_id': int,
                'first_name': str,
                'last_name': str,
                'username': str,
       },
    ~  'chat': {
    !           'chat_id': int,
                'name': str,
                "type": str,
                "first_name": str,
                "username": str,
        }, 
    !  'is_forward': bool,
       'forward': {
           'user_id': int,
           'is_bot': bool,
           'first_name': str,
           'username': str,
       },
    !  'is_message": bool,
       'message': {     
           'text': str,
           'message_id': int,
           'update_id': int,
       },
    !  'is_file': bool,
    !  'is_audio': bool,
    !  'is_video': bool,
    !  'is_document': bool,
    !  'is_image': bool,
    !  'is_location': bool,
       'file' {
           'payload': str,
           'extention': str,
           'thumbnail': str, 
       },
    *   'service_context': {},
    *   'cache': {},
  },
  'response': {
    !  'status': int,
    !  'service_in': str,
    !  'service_out': str,
    !  'body': [
             {
                !  'method': str,
                ~  'target': {
                !             'user_id': int,
                              'name': str,
                              'username': str,
                   },
                !  'has_text': bool,
                   'text': str,
                !  'has_file': bool,
                   'file': {
                           'payload': str,
                    },
                *   'service_context': {},
             },
             ...
       ],
    *  'cache': {},
    }
```