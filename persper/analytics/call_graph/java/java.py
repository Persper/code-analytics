import os
from collections import defaultdict
from antlr4 import *
from persper.analytics.call_graph.java.Java8Listener import Java8Listener
from persper.analytics.call_graph.java.Java8Parser import Java8Parser
import logging

DEBUG = os.environ.get('DEBUG_JAVA', True)
logging.basicConfig(filename='java.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')


class FunctionStatsListener(Java8Listener):
    """
    This class is responsible to get name of the function and
    range of the function which is the start and end line of the function.
    """

    def __init__(self):
        self.function_names = list()
        self.function_ranges = list()
        self.current_function_name = None

    def enterMethodDeclaration(self, ctx=Java8Parser.MethodDeclarationContext):
        try:
            header = ctx.methodHeader()
            declator = header.methodDeclarator()
            name = declator.Identifier().getText()
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


class FunctionCallerListener(Java8Listener):
    def __init__(self):
        self.function_names = list()

    def enterMethodDeclaration(self, ctx=Java8Parser.MethodDeclarationContext):
        try:
            header = ctx.methodHeader()
            declator = header.methodDeclarator()
            name = declator.Identifier().getText()
            self.function_names.append(name)
        except Exception as e:
            if DEBUG:
                raise
            else:
                logging.exception("[FunctionCallerListener][METHOD DECLARATION]")
                self.function_names = []


class FunctionCalleeListener(Java8Listener):
    def __init__(self):
        self.function_caller_callee_map = defaultdict(list)
        self.current_function_name = None

    def enterMethodDeclaration(self, ctx=Java8Parser.MethodDeclarationContext):
        try:
            header = ctx.methodHeader()
            declator = header.methodDeclarator()
            name = declator.Identifier().getText()
            self.current_function_name = name
        except Exception as e:
            if DEBUG:
                raise
            else:
                logging.exception("[FunctionCalleeListener][METHOD DECLARATION]")
                self.current_function_name = None

    def enterMethodInvocation(self, ctx=Java8Parser.MethodInvocationContext):
        try:
            if ctx.methodName():
                name = ctx.methodName().getText()
            else:
                name = ctx.getText()
            if self.current_function_name:
                self.function_caller_callee_map[self.current_function_name].append(
                    name)
        except Exception as e:
            if DEBUG:
                raise
            else:
                logging.exception("[FunctionCalleeListener][METHOD INVOCATION]")

    def enterMethodInvocation_lfno_primary(self, ctx: Java8Parser.MethodInvocation_lfno_primaryContext):
        """
        This function is responsible to handle all the expressions,
        For example:
            int a = 1 + add(3);
            add(someStuff(), moreStuff());
            if(someStuff()){
                int a = 30;
            }

        :param ctx: context for parser
        :return:
        """
        try:
            if ctx.methodName():
                name = ctx.methodName().getText()
            else:
                name = ctx.getText()
            if self.current_function_name:
                self.function_caller_callee_map[self.current_function_name].append(
                    name)
        except Exception as e:
            if DEBUG:
                raise
            else:
                logging.exception("[FunctionCalleeListener][METHOD INVOCATION]")


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
