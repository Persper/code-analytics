from os.path import isfile, join, isdir
from antlr4 import FileStream, CommonTokenStream, InputStream


class ASTCreater:
    def __init__(self, parser, lexer, filename, file_source):
        self.parser = parser
        self.lexer = lexer
        self.filename = filename
        self.file_source = file_source
        self.tree = None

    def __call__(self):
        input_stream = InputStream(self.file_source)
        lexer = self.lexer(input_stream)
        token_stream = CommonTokenStream(lexer)
        parser = self.parser(token_stream)
        self.tree = parser.compilationUnit()
