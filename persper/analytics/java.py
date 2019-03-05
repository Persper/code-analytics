import re
from persper.analytics.call_commit_graph import CallCommitGraph
from persper.analytics.graph_server import GraphServer
from persper.analytics.patch_parser import PatchParser
from persper.analytics.c import function_change_stats
from persper.analytics.call_graph.java.ast_creater import ASTCreater
from persper.analytics.call_graph.java.Java8Lexer import Java8Lexer
from persper.analytics.call_graph.java.Java8Parser import Java8Parser
from persper.analytics.call_graph.java.java import get_function_range_java, update_graph


class JavaGraphServer(GraphServer):
    def __init__(self, filename_regex_strs):
        self._ccgraph = CallCommitGraph()
        self._filename_regexes = [re.compile(
            regex_str) for regex_str in filename_regex_strs]
        # TODO: The right implementation of patch parser for java
        self._pparser = PatchParser()

    def register_commit(self, hexsha, author_name, author_email,
                        commit_message):
        self._ccgraph.add_commit(hexsha, author_name, author_email,
                                 commit_message)

    def update_graph(self, old_filename, old_src, new_filename, new_src, patch):
        ast_list = []
        ast_obj_list = list()
        old_ast = None
        new_ast = None

        # Parse source codes into ASTs
        # TODO: Should we use filepath or file source
        if old_src:
            ast_obj = ASTCreater(Java8Parser, Java8Lexer, old_filename)
            ast_obj()
            old_ast = ast_obj.tree

        if new_src:
            ast_obj = ASTCreater(Java8Parser, Java8Lexer, new_filename)
            ast_obj()
            new_ast = ast_obj.tree
            if new_ast is None:
                return -1
            ast_list = [new_ast]
            ast_obj_list = [ast_obj]

        # TODO: Why is this and what is this?
        # Compute function change stats
        change_stats = function_change_stats(old_ast, new_ast, patch,
                                             self._parse_patch,
                                             get_function_range_java)

        # Update call-commit graph
        # TODO: How is filename passed?
        update_graph(self._ccgraph, ast_obj_list, change_stats)
        return 0

    def get_graph(self):
        return self._ccgraph

    def reset_graph(self):
        self._ccgraph.reset()

    def filter_file(self, filename):
        for regex in self._filename_regexes:
            if not regex.match(filename):
                return False
        return True

    def config(self, param):
        pass

    def _parse_patch(self, patch):
        adds, dels = None, None
        try:
            adds, dels = self._pparser.parse(patch.decode('utf-8', 'replace'))
        except UnicodeDecodeError:
            print("UnicodeDecodeError when parsing patch!")
        except:
            print("Unknown error when parsing patch!")
        return adds, dels
