from lark.visitors import Interpreter
from lark import Tree, Visitor


class SymbolTableUpdater(Interpreter):
    def __default__(self, tree):
        for child in tree.children:
            if isinstance(child, Tree):
                child.symbol_table = tree.symbol_table
        self.visit_children(tree)


class SymbolTableParentUpdater(Visitor):
    def __default__(self, tree):
        for child in tree.children:
            if isinstance(child, Tree):
                child.parent = tree
