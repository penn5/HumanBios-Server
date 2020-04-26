from server_logic.definitions import Context
from sanic.response import json, text
from fsm.handler import Handler
from sanic import Sanic
#import googlemaps 
import aiohttp
import ujson

app = Sanic(name="HumanBios-Server")
handler = Handler()
#gclient = googlemaps.Client(key=LOAD_KEY)


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


@app.route('/webhooks/rasa/webhook/get_facility', methods=['POST'])
async def rasa_get_facility(request):
    # @Important: rasa sends location and facility type
    # @Important: we search in database -> Found: return relevant facility address.
    # @Important:                       -> Not Found: request facility from google places ->
    # @Important: -> save to database, respond with facility address
    # TODO: Introduce database.
    # TODO: Introduce google places api
    data = request.json
    data = ujson.loads(data)
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
