from sanic import Sanic
from sanic.response import json
from fsm.handler import Handler

app = Sanic(name="HumanBios-Server")
handler = Handler()


@app.route('/api/process_message', methods=['POST'])
async def data_handler(request):
    data = request.json
    # TODO: ADD SAFETY TOKEN-CHECK
    # process message
    await handler.process(data)
    # return context
    return json(data)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, log_config=None)