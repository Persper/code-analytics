import json
import pickle
import rocksdb
from lxml import etree


class Cache:
    def __init__(self, rocksdb_path: str, cache_size: int = 1, serializer: str = None):
        """
        :params serializers: available are 'pickle', 'json', 'xml'.
        The default serializer is None.
        """
        self._serializer = serializer
        self._cache_size = cache_size
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
            block_cache=rocksdb.LRUCache(self._cache_size * (1024 ** 3)))
        return opts

    def put(self, key, val, serializer=None):
        """use instance scoped serializer if param serializer is None"""
        if serializer is None:
            serializer = self._serializer
        val = self._encode(val, serializer)

        """prevent storing a key or value as a string"""
        if type(key) is str:
            key = self.str2bytes(key)
        if type(val) is str:
            val = self.str2bytes(val)
        self._db.put(key, val)

    def get(self, key, serializer=None):
        if serializer is None:
            serializer = self._serializer
        if type(key) is str:
            key = self.str2bytes(key)
        val = self._db.get(key)
        if val != b'' and val is not None and type(val) is bytes:
            val = self._decode(val, serializer)
        return val

    def delete(self, key):
        if type(key) is str:
            key = self.str2bytes(key)
        self._db.delete(key)

    def put_raw(self, key, val):
        self.put(key, val, serializer='raw')

    def get_raw(self, key):
        return self.get(key, serializer='raw')

    def _encode(self, val, serializer=None):
        if serializer == 'json':
            val = self.json_encode(val)
        elif serializer == 'pickle':
            val = self.pickle_encode(val)
        elif serializer == 'xml':
            val = self.xml_encode(val)
        return val

    def _decode(self, val, serializer=None):
        if serializer == 'json':
            val = self.json_decode(val)
        elif serializer == 'pickle':
            val = self.pickle_decode(val)
        elif serializer == 'xml':
            val = self.xml_decode(val)
        return val

    @staticmethod
    def str2bytes(val):
        return bytes(val, encoding='utf-8')

    @staticmethod
    def json_encode(val):
        try:
            return json.dumps(val)
        except BaseException:
            return ''

    @staticmethod
    def json_decode(val):
        try:
            return json.loads(val)
        except BaseException:
            return None

    @staticmethod
    def xml_encode(val):
        try:
            return etree.tostring(val)
        except BaseException:
            return ''

    @staticmethod
    def xml_decode(val):
        try:
            return etree.fromstring(val)
        except BaseException:
            return None

    @staticmethod
    def pickle_encode(val):
        try:
            return pickle.dumps(val)
        except BaseException:
            return ''

    @staticmethod
    def pickle_decode(val):
        try:
            return pickle.loads(val)
        except BaseException:
            return None
