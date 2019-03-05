from os.path import isfile, join, isdir
from antlr4 import FileStream, CommonTokenStream
from multi_file_stream import MultiFileStream


class ASTCreater:
    def __init__(self, parser, lexer, path):
        self.parser = parser
        self.lexer = lexer
        self.path = path
        self.tree = None

    def __call__(self):
        if isfile(self.path):
            input_stream = FileStream(self.path)
        elif isdir(self.path):
            input_stream = MultiFileStream(self.path)
        lexer = self.lexer(input_stream)
        token_stream = CommonTokenStream(lexer)
        parser = self.parser(token_stream)
        self.tree = parser.compilationUnit()
