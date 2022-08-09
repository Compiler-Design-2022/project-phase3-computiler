from lark.visitors import Interpreter
from lark import Tree, Visitor
from symbol_table import SymbolTable


class SymbolTableUpdater(Interpreter):
    def __default__(self, tree):
        for child in tree.children:
            if isinstance(child, Tree):
                child.symbol_table = tree.symbol_table
        self.visit_children(tree)

    def if_stmt(self, tree):
        tree.children[1].symbol_table = tree.symbol_table
        self.visit(tree.children[1])
        statement_block_table = SymbolTable(parent=tree.symbol_table)
        tree.children[2].symbol_table = statement_block_table
        self.visit(tree.children[2])
        if len(tree.children) > 3:
            else_statement_block_table = SymbolTable(parent=tree.symbol_table)
            tree.children[4].symbol_table = else_statement_block_table
            self.visit(tree.children[4])

    def while_stmt(self, tree):
        tree.children[1].symbol_table = tree.symbol_table
        self.visit(tree.children[1])
        statement_block_table = SymbolTable(parent=tree.symbol_table)
        tree.children[2].symbol_table = statement_block_table
        self.visit(tree.children[2])

    def for_1(self, tree):
        tree.children[1].symbol_table = tree.symbol_table
        self.visit(tree.children[1])
        statement_block_table = SymbolTable(parent=tree.symbol_table)
        tree.children[2].symbol_table = statement_block_table
        self.visit(tree.children[2])

    def for_2(self, tree):
        tree.children[1].symbol_table = tree.symbol_table
        self.visit(tree.children[1])
        tree.children[2].symbol_table = tree.symbol_table
        self.visit(tree.children[2])
        statement_block_table = SymbolTable(parent=tree.symbol_table)
        tree.children[3].symbol_table = statement_block_table
        self.visit(tree.children[3])

    def for_3(self, tree):
        tree.children[1].symbol_table = tree.symbol_table
        self.visit(tree.children[1])
        tree.children[2].symbol_table = tree.symbol_table
        self.visit(tree.children[2])
        statement_block_table = SymbolTable(parent=tree.symbol_table)
        tree.children[3].symbol_table = statement_block_table
        self.visit(tree.children[3])

    def for_4(self, tree):
        tree.children[1].symbol_table = tree.symbol_table
        self.visit(tree.children[1])
        tree.children[2].symbol_table = tree.symbol_table
        self.visit(tree.children[2])
        tree.children[3].symbol_table = tree.symbol_table
        self.visit(tree.children[3])
        statement_block_table = SymbolTable(parent=tree.symbol_table)
        tree.children[4].symbol_table = statement_block_table
        self.visit(tree.children[4])

    # TODO: i don't know how is this symbol table
    def stmt_block(self, tree):
        pass


class SymbolTableParentUpdater(Visitor):
    def __default__(self, tree):
        for child in tree.children:
            if isinstance(child, Tree):
                child.parent = tree
