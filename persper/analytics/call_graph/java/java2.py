import os
import ast
from collections import defaultdict
from antlr4 import *
from persper.parser.java.JavaParserListener import JavaParserListener
from persper.parser.java.JavaParser import JavaParser
import logging

DEBUG = ast.literal_eval(os.environ.get('DEBUG_JAVA', "True"))
logging.basicConfig(filename='java.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')


class FunctionStatsListener(JavaParserListener):
    """
    This class is responsible to get name of the function and
    range of the function which is the start and end line of the function.
    """

    def __init__(self):
        self.function_names = list()
        self.function_ranges = list()
        self.current_function_name = None

    def enterMethodDeclaration(self, ctx=JavaParser.MethodDeclarationContext):
        try:
            name = ctx.IDENTIFIER().getText()
            self.current_function_name = name
            self.function_names.append(name)
            self.function_ranges.append([ctx.start.line, ctx.stop.line])
        except Exception as e:
            if DEBUG:
                raise
            else:
                logging.exception("[FunctionStatsListener][METHOD DECLARATION]")
                self.function_names = []
                self.function_ranges = []


class FunctionCallerListener(JavaParserListener):
    def __init__(self):
        self.function_names = list()

    def enterMethodDeclaration(self, ctx=JavaParser.MethodDeclarationContext):
        try:
            name = ctx.IDENTIFIER().getText()
            self.function_names.append(name)
        except Exception as e:
            if DEBUG:
                raise
            else:
                logging.exception("[FunctionCallerListener][METHOD DECLARATION]")
                self.function_names = []


class FunctionCalleeListener(JavaParserListener):
    def __init__(self):
        self.function_caller_callee_map = defaultdict(list)
        self.current_function_name = None

    def enterMethodDeclaration(self, ctx=JavaParser.MethodDeclarationContext):
        try:
            name = ctx.IDENTIFIER().getText()
            self.current_function_name = name
        except Exception as e:
            if DEBUG:
                raise
            else:
                logging.exception("[FunctionCalleeListener][METHOD DECLARATION]")
                self.current_function_name = None

    def enterMethodCall(self, ctx: JavaParser.MethodCallContext):
        try:
            # The condition is there to avoid functions like `this()` or `super()`
            if ctx.IDENTIFIER():
                name = ctx.IDENTIFIER().getText()
                if self.current_function_name:
                    self.function_caller_callee_map[self.current_function_name].append(
                        name)
        except Exception as e:
            if DEBUG:
                raise
            else:
                logging.exception("[FunctionCalleeListener][METHOD CALL]")


def get_function_range_java(tree):
    walker = ParseTreeWalker()
    collector = FunctionStatsListener()
    walker.walk(collector, tree)
    return collector.function_names, collector.function_ranges


def get_all_function_caller(tree):
    walker = ParseTreeWalker()
    collector = FunctionCallerListener()
    walker.walk(collector, tree)
    return collector.function_names


def get_caller_callee_map(tree):
    walker = ParseTreeWalker()
    collector = FunctionCalleeListener()
    walker.walk(collector, tree)
    return collector.function_caller_callee_map


def update_graph(ccgraph, ast_list, change_stats, new_fname_to_old_fname):
    for ast in ast_list:
        filename = ast.filename
        tree = ast.tree
        for function in get_all_function_caller(tree):

            if function not in ccgraph:
                ccgraph.add_node(function, [filename])
            else:
                files = ccgraph.files(function)
                old_filename = new_fname_to_old_fname.get(filename, None)
                # Case: Rename
                if old_filename:
                    files.add(filename)
                    if old_filename in files:
                        files.remove(old_filename)
                    ccgraph.update_node_files(function, files)
                # Case: New
                elif filename not in files:
                    files.add(filename)
                    ccgraph.update_node_files(function, files)

        for call, callee in get_caller_callee_map(tree).items():
            for callee_name in callee:
                if callee_name not in ccgraph:
                    # Pass [] to files argument since we don't know
                    # which file this node belongs to
                    ccgraph.add_node(callee_name, [])
                ccgraph.add_edge(call, callee_name)

    for func, fstat in change_stats.items():
        if func not in ccgraph:
            print("%s in change_stats but not in ccgraph" % func)
            continue
        ccgraph.update_node_history(func, fstat['adds'], fstat['dels'])
