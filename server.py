from server_logic.definitions import Context
from settings import ROOT_PATH, logger
from sanic.response import json
from fsm.handler import Handler
from settings import tokens
from sanic import Sanic
#import googlemaps
import asyncio
import os


app = Sanic(name="HumanBios-Server")
handler = Handler()
#gclient = googlemaps.Client(key=LOAD_KEY)


@app.route('/api/process_message', methods=['POST'])
async def data_handler(request):
    # get data from request
    data = request.json
    if data is None:
        return json({"status": 403, "message": "token unauthorized"})

    token = tokens.get(data.get('via_bot'), '')
    # `not token` to avoid `'' == ''`
    if not token or not (data.get("security_token", '') == token.token):
        # add custom 403 error code
        return json({"status": 403, "message": "token unauthorized"})

    # build into context
    result = Context.from_json(data)
    # verify context `required` attributes
    if not result.validated:
        # add custom 403 error code
        # TODO: Describe which fields were unvalidated
        return json({"status": 403, "message": "invalid"})
    # Validated object
    ctx = result.object
    # Replace security token to the server's after validation
    ctx.replace_security_token()
    # process message
    asyncio.create_task(handler.process(ctx))
    # return context
    return json(ctx.ok)


@app.route('/webhooks/rasa/webhook/get_facility', methods=['POST'])
async def rasa_get_facility(request):
    # @Important: rasa sends location and facility type
    # @Important: we search in database -> Found: return relevant facility address.
    # @Important:                       -> Not Found: request facility from google places -> \
    # @Important:                                respond with address <- save to database <- /
    # TODO: Introduce database.
    # TODO: Introduce google places api
    data = request.json
    location: str = data.get('location')
    facility_type: str = data.get('facility_type')
    facility_id: str = data.get('facility_id')
    amount: int = data.get('amount')
    # Facility type is one of the values
    if facility_id:
        address = "<this is a dummy server response of the cached facility>"
        resp = {"facility_address_0": address}
    elif amount:
        resp = {}
        for i in range(amount):
            resp[f"facility_address_{i}"] = "<this is a dummy server response address>"
    else:
        resp = {"facility_address_0": "<this is a dummy server response address>"}
    return json(resp)
   

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8282, log_config=None)
