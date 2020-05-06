from settings import tokens
from server import app
import ujson


def test_index_returns_403_unauthorized():
    request, response = app.test_client.post('/api/process_message')

    assert response.json.get("status") == 403
    assert response.json.get("message") == "expected json"


def test_post_request_data_sent_with_403_invalid():
    data = {'via_instance': 'tests_dummy_bot', 'security_token': tokens['tests_dummy_bot'].token}
    request, response = app.test_client.post('/api/process_message', data=ujson.dumps(data))

    assert request.json.get('security_token') == tokens['tests_dummy_bot'].token
    assert request.json.get('via_instance') == 'tests_dummy_bot'

    assert response.json.get("status") == 403
    assert response.json.get("message") == "'service_in' is a required property"


def test_post_json_request_403_invalid():
    data1 = {'security_token': tokens['tests_dummy_bot'].token, 'via_instance': 'tests_dummy_bot',
             "user": {"user_id": 1232131}, "chat": {"chat_id": 2131321}}
    data2 = {"security_token": tokens['tests_dummy_bot'].token, "service_in": "WhatsApp",
             'via_instance': 'tests_dummy_bot', "chat": {"chat_id": 2131321}}
    data3 = {'security_token': tokens['tests_dummy_bot'].token, 'via_instance': 'tests_dummy_bot',
             "service_in": "WhatsApp", "user": {"user_id": 1232131}, "chat": {}}

    request1, response1 = app.test_client.post('/api/process_message', data=ujson.dumps(data1))

    # Data source 1 test
    assert response1.json.get("status") == 403
    assert response1.json.get("message") == "'service_in' is a required property"

    request2, response2 = app.test_client.post('/api/process_message', data=ujson.dumps(data2))

    # Data source 2 test
    assert response2.json.get("status") == 403
    assert response2.json.get("message") == "'user' is a required property"

    request3, response3 = app.test_client.post('/api/process_message', data=ujson.dumps(data3))

    # Data source 3 test
    assert response3.json.get("status") == 403
    assert response3.json.get("message") == "'chat_id' is a required property"