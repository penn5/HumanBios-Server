from settings import tokens
from server import app
import ujson


def test_index_returns_403_unauthorized():
    request, response = app.test_client.post('/api/process_message')

    assert response.json == {"status": 403, "description": "token unauthorized"}


def test_post_request_data_sent():
    data = {'via_bot': 'tests_dummy_bot', 'security_token': tokens['tests_dummy_bot'].token}
    request, response = app.test_client.post('/api/process_message', data=ujson.dumps(data))

    assert request.json.get('security_token') == tokens['tests_dummy_bot'].token
    assert request.json.get('via_bot') == 'tests_dummy_bot'


def test_post_json_request_403_invalid():
    data = {'via_bot': 'tests_dummy_bot', 'security_token': tokens['tests_dummy_bot'].token}
    request, response = app.test_client.post('/api/process_message', data=ujson.dumps(data))

    assert response.json == {"status": 403, "description": "invalid"}