from server_logic.definitions import Context
from settings import ROOT_PATH, Config
from sanic.response import json
from fsm.handler import Handler
from settings import tokens
from sanic import Sanic
#import googlemaps
import asyncio
import secrets
import sanic
import os


app = Sanic(name="HumanBios-Server")
handler = Handler()
app.add_task(handler.reminder_loop())
#gclient = googlemaps.Client(key=LOAD_KEY)


@app.route('/api/process_message', methods=['POST'])
async def data_handler(request):
    # get data from request
    data = request.json
    if data is None:
        return json({"status": 403, "message": "expected json"})

    token = tokens.get(data.get('via_instance'), '')
    # `not token` to avoid `'' == ''`
    if not token or not (data.get("security_token", '') == token.token):
        # add custom 403 error code
        return json({"status": 403, "message": "token unauthorized"})

    # build into context
    result = Context.from_json(data)
    # verify context `required` attributes
    if not result.validated:
        # add custom 403 error code
        return json({"status": 403, "message": result.error})
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


@app.route('/api/setup', methods=['POST'])
async def worker_setup(request):
    # get data from request
    data = request.json
    # If not data -> return "expected json"
    if not data:
        return json({"status": 403, "message": "expected json"})
    # get security token from the data
    token = data.get("security_token", "")
    # Verify security token (of the server)
    if token != tokens['server']:
        return json({"status": 403, "message": "token unauthorized"})
    # Pull url from request
    url = data.get("url", "")
    # Generate new token and pull url
    if not url:
        return json({"status": 403, "message": "url invalid"})

    # Generate new token and name for the instance
    # @Important: 40 bytes token is > 50 characters long
    new_token = secrets.token_urlsafe(40)
    # @Important: Conveniently cut to length of 40
    new_token = new_token[:40]
    # @Important: Token hex returns n * 2 amount of symbols
    name = secrets.token_hex(10)
    # [DEBUG]: assert len(name) == 20

    # Save data on the server
    # TODO: @Important|@Priority: 1) Make registration consistent in db -> allow reloading
    #                                server (keeping front ends alive)
    #                                Good approach will be syncing from db every X minutes (and on-load)
    #                                Or some smarter trigger to keep db and this instance sync (e.g. trigger
    #                                all instances and sync from database when new front end inst was added)
    #                                Why this is important? Using database and load-balancer properly -> we
    #                                can get few instances of the server running (each user assigned to one
    #                                server in "session" manner so relevant cache works for each server inst)
    # TODO: @Important:            2) Make front ends consistent -> allow reloading them too
    config_obj = Config(new_token, url)
    tokens[name] = config_obj
    # Return useful data back to the caller
    return json({"status": 200, "name": name, "token": new_token})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8282, debug=False, access_log=False, log_config=None)
