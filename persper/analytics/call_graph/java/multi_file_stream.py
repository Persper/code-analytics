from antlr4 import InputStream
from os import listdir
from os.path import isfile, join, isdir
import codecs


class MultiFileStream(InputStream):

    def __init__(self, path: str, encoding: str = 'ascii', errors: str = 'strict'):
        super().__init__(self.readDataFrom(path, encoding, errors))
        self.dir_name = path

    def get_list_of_file(self, path):
        file_paths = [join(path, f) for f in listdir(
            path) if isfile(join(path, f)) and f.endswith(".java")]
        return file_paths

    def get_file_data(self, path):
        bytes = b''
        for path in self.get_list_of_file(path):
            with open(path, 'rb') as file:
                bytes += file.read()
        return bytes

    def readDataFrom(self, path: str, encoding: str, errors: str = 'strict'):
        # read binary to avoid line ending conversion
        bytes = self.get_file_data(path)
        return codecs.decode(bytes, encoding, errors)
