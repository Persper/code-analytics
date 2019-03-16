from collections import defaultdict
from antlr4 import *
from persper.analytics.call_graph.java.Java8Listener import Java8Listener
from persper.analytics.call_graph.java.Java8Parser import Java8Parser


class FunctionStatsListener(Java8Listener):
    """
    This class is responsible to get name of the function and
    range of the function which is the start and end line of the function.
    """

    def __init__(self):
        self.function_names = list()
        self.function_ranges = list()

    def enterMethodDeclaration(self, ctx=Java8Parser.MethodDeclarationContext):
        header = ctx.methodHeader()
        declator = header.methodDeclarator()
        name = declator.Identifier().getText()
        self.current_function_name = name
        self.function_names.append(name)
        self.function_ranges.append([ctx.start.line, ctx.stop.line])


class FunctionCallerListener(Java8Listener):
    def __init__(self):
        self.function_names = list()

    def enterMethodDeclaration(self, ctx=Java8Parser.MethodDeclarationContext):
        header = ctx.methodHeader()
        declator = header.methodDeclarator()
        name = declator.Identifier().getText()
        self.function_names.append(name)


class FunctionCalleeListener(Java8Listener):
    def __init__(self):
        self.function_caller_callee_map = defaultdict(list)
        self.current_function_name = None

    def enterMethodDeclaration(self, ctx=Java8Parser.MethodDeclarationContext):
        header = ctx.methodHeader()
        declator = header.methodDeclarator()
        name = declator.Identifier().getText()
        self.current_function_name = name

    def enterMethodInvocation(self, ctx=Java8Parser.MethodInvocationContext):
        if ctx.methodName():
            name = ctx.methodName().getText()
        else:
            name = ctx.getText()
        if self.current_function_name:
            self.function_caller_callee_map[self.current_function_name].append(
                name)

    def enterPrimary(self, ctx: Java8Parser.PrimaryContext):
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
        is_method = ctx.primaryNoNewArray_lfno_primary().methodInvocation_lfno_primary()
        if is_method:
            name = is_method.methodName().getText()

            if self.current_function_name:
                self.function_caller_callee_map[self.current_function_name].append(
                    name)


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


def update_graph(ccgraph, ast_list, change_stats):
    for ast in ast_list:
        filename = ast.filename
        tree = ast.tree
        for function in get_all_function_caller(tree):

            if function not in ccgraph:
                ccgraph.add_node(function, [filename])
            else:
                files = ccgraph.nodes()[function]['files']
                if filename not in files:
                    ccgraph.update_node_files(function, files.union(set([filename])))

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
