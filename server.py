from server_logic.definitions import Context
from sanic.response import json, text
from fsm.handler import Handler
from sanic import Sanic
import settings
import aiohttp

app = Sanic(name="HumanBios-Server")
handler = Handler()


@app.route('/api/process_message', methods=['POST'])
async def data_handler(request):
    # get data from request
    data = request.json
    # TODO: ADD SAFETY TOKEN-CHECK

    # build into context
    ctx = Context.from_json(data)
    # verify context `required` attributes
    if not ctx.validate():
        # TODO: Add information that will explain what was missing/wrong
        # add custom 403 error code
        resp = ctx.to_dict()
        resp['response']['status'] = 403
        return json(resp)
    # process message
    await handler.process(ctx)
    # return context
    return json(ctx.to_dict())


@app.route('/webhooks/botsociety/webhook', methods=['GET'])
async def botsociety_webhook(request):
    conversations_ids = request.args['conversation_id']
    #user_id = request.args['user_id']
    async with aiohttp.ClientSession() as session:
        # Both conv and user ids are lists, so relaying that they are the same length
        #for index, each_id in enumerate(conversations_ids):
        for each_id in enumerate(conversations_ids):
            url_ = f"{settings.B_URL}/{settings.B_VERSION}/conversations/{each_id}"
            headers = {
                'user_id': settings.B_ID,  # user_id[index],
                'api_key_public': settings.B_KEY,
                'Content-Type': 'application/json'
            }
            async with session.get(url_, headers=headers) as response:
                # WORK IN PROGRESS !!! DONT LOOK :P
                print(await response.json())
    return text('ok')

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, log_config=None)