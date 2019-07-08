import json
import pickle
import rocksdb


class Cache:
    def __init__(self, rocksdb_path, serializer='pickle'):
        """
        :params serializers: available are 'pickle', 'json'.
        """
        self._serializer = serializer
        opts = self._config_rocksdb()

        self._db = rocksdb.DB(rocksdb_path, opts)

    def _config_rocksdb(self):
        """options used to create a rocksdb instance.
        more about options: https://python-rocksdb.readthedocs.io/en/latest/api/options.html
        """
        opts = rocksdb.Options()
        opts.create_if_missing = True
        opts.max_open_files = 300000
        opts.write_buffer_size = 67108864
        opts.max_write_buffer_number = 3
        opts.target_file_size_base = 67108864

        opts.table_factory = rocksdb.BlockBasedTableFactory(
            filter_policy=rocksdb.BloomFilterPolicy(10),
            block_cache=rocksdb.LRUCache(2 * (1024 ** 3)),
            block_cache_compressed=rocksdb.LRUCache(500 * (1024 ** 2)))
        return opts

    def put(self, key, val):
        val = self._encode(val)

        """prevent storing a key or value as a string"""
        if type(key) is str:
            key = self.str2bytes(key)
        if type(val) is str:
            val = self.str2bytes(val)
        self._db.put(key, val)

    def get(self, key):
        if type(key) is str:
            key = self.str2bytes(key)
        val = self._db.get(key)
        val = self._decode(val)
        return val

    def delete(self, key):
        if type(key) is str:
            key = self.str2bytes(key)
        self._db.delete(key)

    def _encode(self, val):
        if self._serializer == 'json':
            val = self.json_encode(val)
        elif self._serializer == 'pickle':
            val = pickle.dumps(val)
        return val

    def _decode(self, val):
        if self._serializer == 'json':
            val = self.json_decode(val)
        elif self._serializer == 'pickle':
            val = pickle.loads(val)
        return val

    @staticmethod
    def str2bytes(val):
        return bytes(val, encoding='utf-8')

    @staticmethod
    def json_encode(val):
        try:
            return json.dumps(val)
        except:
            return ''

    @staticmethod
    def json_decode(val):
        try:
            return json.loads(val)
        except:
            return None


if __name__ == "__main__":
    cache = Cache('./test_rock')
    obj = {"a": 1, "b": "hello", "c": [1, 3, 5]}
    key = 'test_obj1'
    cache.put(key, obj)

    obj_get = cache.get(key)
    print(obj_get['a'])
    print(obj_get['b'])
    print(obj_get['c'])
