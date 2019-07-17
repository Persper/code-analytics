import tempfile
from persper.util.cache import Cache


def test_cache():
    with tempfile.TemporaryDirectory() as tmpdirname:
        cache = Cache(tmpdirname, serializer='pickle')

        obj = {"a": 1, "b": "hello", "c": [1, 3, 5]}
        key = 'test_obj1'
        cache.put(key, obj)

        obj_get = cache.get(key)
        assert obj_get['a'] == 1
        assert obj_get['b'] == "hello"
        assert obj_get['c'] == [1, 3, 5]
