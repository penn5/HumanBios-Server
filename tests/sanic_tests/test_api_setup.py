from settings import tokens
from server import app
import ujson


def test_api_setup_returns_403_expected_json():
    request, response = app.test_client.post('/api/setup')

    assert response.json.get("status") == 403
    assert response.json.get("message") == "expected json"


def test_api_setup_returns_403_unauthorized():
    data = {'odd': 'ting'}
    request, response = app.test_client.post('/api/setup', data=ujson.dumps(data))

    assert response.json.get("status") == 403
    assert response.json.get("message") == "token unauthorized"


# Returns 403 url invalid, but authorization passed
def test_api_setup_returns_authorized():
    data = {'security_token': tokens['server']}
    request, response = app.test_client.post('/api/setup', data=ujson.dumps(data))

    assert response.json.get("status") == 403
    assert response.json.get("message") == "url invalid"


def test_api_setup_request_data_sent_with_403_url_invalid():
    data1 = {'dummy_data': 'dummy', 'security_token': tokens['server']}
    request, response = app.test_client.post('/api/setup', data=ujson.dumps(data1))

    assert response.json.get("status") == 403
    assert response.json.get("message") == "url invalid"

    data2 = {"url": '', 'security_token': tokens['server']}
    request, response = app.test_client.post('/api/setup', data=ujson.dumps(data2))

    assert response.json.get("status") == 403
    assert response.json.get("message") == "url invalid"


def test_api_setup_success():
    data = {"url": 'https://example.com', 'security_token': tokens['server']}
    request, response = app.test_client.post('/api/setup', data=ujson.dumps(data))

    assert response.json.get("status") == 200

    assert type(response.json.get("name"))
    assert response.json.get('name') != ""
    assert len(response.json.get('name')) == 20

    assert type(response.json.get("token"))
    assert response.json.get('token') != ""
    assert len(response.json.get('token')) == 40