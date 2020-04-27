from server_logic.definitions.context import Context, ContextItem
import pytest


@pytest.fixture
def ctx_data():
    return {'foo': {'nya': 1, 'mew': "mau", 'hello': {"henlo": 'yo', 'hallo': 'de'}}, 'weird': ('flex', 'but okay')}


def test_context_from_json_properties_success(ctx_data):
    ctx = Context.from_json(ctx_data)

    assert type(ctx.foo) == ContextItem
    assert type(ctx.foo.hello) == ContextItem
    assert ctx.foo.nya == 1
    assert ctx.foo.hello.hallo == 'de'
    assert ctx.weird == ('flex', 'but okay')


def test_context_from_json_dictionary_access_success(ctx_data):
    ctx = Context.from_json(ctx_data)

    assert type(ctx.foo) == ContextItem
    assert type(ctx.foo.hello) == ContextItem
    assert ctx['foo']['mew'] == "mau"
    assert ctx['foo']['hello']['henlo'] == 'yo'


def test_context_from_json_elements_access_must_fail(ctx_data):
    ctx = Context.from_json(ctx_data)

    with pytest.raises(KeyError):
        ctx['nya']
    with pytest.raises(KeyError):
        ctx['foo']['hello']['yo']
    with pytest.raises(KeyError):
        ctx['foo']['mau']
    with pytest.raises(KeyError):
        ctx['fo']['aaa']


def test_context_from_json_tricky_case():
    ctx_data = {('weird flex', "buy ice"): 'life', lambda a: a * 100: 1}

    ctx = Context.from_json(ctx_data)

    assert ctx[('weird flex', "buy ice")] == 'life'
    with pytest.raises(KeyError):
        assert ctx[lambda a: a * 100] == 1

    assert str(ctx) == str(ctx_data)