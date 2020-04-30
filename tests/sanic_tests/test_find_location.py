from pytest import fixture
from server import app
import ujson


def test_post_request_location_id():
    data = {'facility_id': 'Pdj2f1Nfm23'}
    request, response = app.test_client.post('/webhooks/rasa/webhook/get_facility', data=ujson.dumps(data))

    assert response.json.get("facility_address_0") != ""
    assert response.json.get("facility_address_0") is not None


@fixture
def location_data():
    data = {
        'facility_type': 'hospital',
        'location': 'Peremohy Ave, 54/1, к. 345, Kyiv, 03680',
        'amount': 1,
    }
    return data


def test_post_request_location_single_data(location_data):
    request, response = app.test_client.post('/webhooks/rasa/webhook/get_facility', data=ujson.dumps(location_data))

    assert response.json.get("facility_address_0") != ""
    assert response.json.get("facility_address_0") is not None
    # Single amount
    assert len(response.json) == 1


def test_post_request_location_many_data(location_data):
    AMOUNT = 5

    location_data['amount'] = AMOUNT
    request, response = app.test_client.post('/webhooks/rasa/webhook/get_facility', data=ujson.dumps(location_data))

    for i in range(AMOUNT):
        assert response.json.get(f"facility_address_{i}") != ""
        assert response.json.get(f"facility_address_{i}") is not None
    # Many results
    assert len(response.json) == AMOUNT
