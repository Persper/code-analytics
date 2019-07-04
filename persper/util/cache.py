import json
import rocksdb

class Cache():
    def __init__(self, path='', serializer='json'):
        self._serializer = serializer

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

        self._db = rocksdb.DB(path, opts)

    def put(self, key, val):
        if self._serializer == 'json':
            val = self.json_encode(val)
        if type(key) is str:
            key = self.str2bytes(key)
        if type(val) is str:
            val = self.str2bytes(val)
        self._db.put(key, val)

    def get(self, key):
        if type(key) is str:
            key = self.str2bytes(key)
        val = self._db.get(key)
        if self._serializer == 'json':
            val = self.json_decode(val)
        return val

    def delete(self, key):
        if type(key) is str:
            key = self.str2bytes(key)
        self._db.delete(key)

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
    obj = { "a": 1, "b": "hello" }
    key = 'test_obj1'
    cache.put(key, obj)

    obj_get = cache.get(key)
    print(obj_get['a'])
    print(obj_get['b'])
