from db import ServiceTypes


def test_service_types_literals():
    assert ServiceTypes.TELEGRAM == "telegram"
    assert ServiceTypes.FACEBOOK == "facebook"
    assert ServiceTypes.WEBSITE == "website"
