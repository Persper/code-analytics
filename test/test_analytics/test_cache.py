import tempfile
from persper.util.cache import Cache


def test_cache_pickle_serializer():
    with tempfile.TemporaryDirectory() as tmpdirname:
        cache = Cache(tmpdirname, serializer='pickle')

        obj = {"a": 1, "b": "hello", "c": [1, 3, 5]}
        key = 'test_obj1'
        cache.put(key, obj)

        obj_get = cache.get(key)
        assert obj_get['a'] == 1
        assert obj_get['b'] == 'hello'
        assert obj_get['c'] == [1, 3, 5]

def test_cache_json_serializer():
    with tempfile.TemporaryDirectory() as tmpdirname:
        cache = Cache(tmpdirname, serializer='json')

        obj = {"a": 1, "b": "hello", "c": [1, 3, 5]}
        key = 'test_obj1'
        cache.put(key, obj)

        obj_get = cache.get(key)
        assert obj_get['a'] == 1
        assert obj_get['b'] == 'hello'
        assert obj_get['c'] == [1, 3, 5]

def test_cache_raw_key_value():
    with tempfile.TemporaryDirectory() as tmpdirname:
        cache = Cache(tmpdirname)

        key = 'raw_key'
        val = 'i am raw'
        cache.put_raw(key, val)

        val_get = cache.get_raw(key)
        assert val_get == bytes(val, encoding='utf-8')
