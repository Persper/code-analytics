from antlr4 import CommonTokenStream, InputStream


class ASTCreater:
    def __init__(self, parser, lexer, filename, file_source):
        """

        :param parser: Parser object from antlr4
        :param lexer: Lexer object from antlr4
        :param filename: Name of the file which has to be parsed
        :param file_source: Stream of strings, content of the file
        """
        self.parser = parser
        self.lexer = lexer
        # ASTCreater helps to have a filename attach to every AST objects
        self.filename = filename
        self.file_source = file_source
        self.tree = None

    def __call__(self):
        input_stream = InputStream(self.file_source)
        lexer = self.lexer(input_stream)
        token_stream = CommonTokenStream(lexer)
        parser = self.parser(token_stream)
        self.tree = parser.compilationUnit()
