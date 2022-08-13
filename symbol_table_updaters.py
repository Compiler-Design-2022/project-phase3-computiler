from lark.visitors import Interpreter
from lark import Tree, Visitor, Token

from decaf_enums import DecafTypes, Constants
from semantic_error import SemanticError
from symbol_table import SymbolTable, Variable, Type, Function, Class

stack = []
class_stack = []


def increment_data_pointer(size):
    cur = SymbolTableUpdater.data_pointer
    SymbolTableUpdater.data_pointer += size
    return cur


class SymbolTableUpdater(Interpreter):
    def __default__(self, tree):
        for child in tree.children:
            if isinstance(child, Tree):
                child.symbol_table = tree.symbol_table
        self.visit_children(tree)

    data_pointer = 0
    def type(self, tree):
        type_name = tree.children[0].value
        stack.append(Type(type_name))

    def function_decl(self, tree):
        function_class = None
        if len(class_stack) > 0:
            function_class = class_stack[-1]
        return_type = Type(DecafTypes.void_type)
        if isinstance(tree.children[0], Tree):
            tree.children[0].symbol_table = tree.symbol_table
            self.visit(tree.children[0])
            return_type = stack.pop()
        func_name = tree.children[1].value
        formals_symbol_table = SymbolTable(parent=tree.symbol_table)
        tree.children[2].symbol_table = formals_symbol_table
        sp_initial = len(stack)
        self.visit(tree.children[2])
        formals = []
        while len(stack) > sp_initial:
            f = stack.pop()
            formals.append(f)

        formals = formals[::-1]
        body_symbol_table = SymbolTable(parent=formals_symbol_table)
        tree.children[3].symbol_table = body_symbol_table
        self.visit(tree.children[3])
        prefix_label = ''
        if function_class:
            prefix_label = "class_"

        tree.symbol_table.add_func(Function(
            name=func_name,
            return_type=return_type,
            formals=formals,
            prefix_class=prefix_label
        ))

    def variable(self, tree):
        variable_class = None
        if len(class_stack) > 0:
            variable_class = class_stack[-1]
        tree.children[0].symbol_table = tree.symbol_table
        self.visit(tree.children[0])
        var_type = stack.pop()
        var_name = tree.children[1].value
        var = Variable(
            name=var_name,
            var_type=var_type,
            address=increment_data_pointer(4),
        )
        tree.symbol_table.add_var(var)
        stack.append(var)

    def array_type(self, tree):
        tree.children[0].symbol_table = tree.symbol_table
        self.visit(tree.children[0])
        mem_type = stack.pop()
        stack.append(Type("array", arr_type=mem_type))

    def access_mode(self, tree):
        if tree.children:
            return tree.children[0].value
        return 'public'

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
        tree.children[3].symbol_table = tree.symbol_table
        self.visit(tree.children[3])
        statement_block_table = SymbolTable(parent=tree.symbol_table)
        tree.children[6].symbol_table = statement_block_table
        self.visit(tree.children[6])

    def for_2(self, tree):
        tree.children[2].symbol_table = tree.symbol_table
        self.visit(tree.children[2])
        tree.children[4].symbol_table = tree.symbol_table
        self.visit(tree.children[4])
        statement_block_table = SymbolTable(parent=tree.symbol_table)
        tree.children[7].symbol_table = statement_block_table
        self.visit(tree.children[7])

    def for_3(self, tree):
        tree.children[3].symbol_table = tree.symbol_table
        self.visit(tree.children[3])
        tree.children[5].symbol_table = tree.symbol_table
        self.visit(tree.children[5])
        statement_block_table = SymbolTable(parent=tree.symbol_table)
        tree.children[7].symbol_table = statement_block_table
        self.visit(tree.children[7])

    def for_4(self, tree):
        tree.children[2].symbol_table = tree.symbol_table
        self.visit(tree.children[2])
        tree.children[4].symbol_table = tree.symbol_table
        self.visit(tree.children[4])
        tree.children[6].symbol_table = tree.symbol_table
        self.visit(tree.children[6])
        statement_block_table = SymbolTable(parent=tree.symbol_table)
        tree.children[8].symbol_table = statement_block_table
        self.visit(tree.children[8])

    def stmt_block(self, tree):
        new_block_table = SymbolTable(parent=tree.symbol_table)
        for child in tree.children:
            if isinstance(child, Tree):
                child.symbol_table = new_block_table
                self.visit(child)

    def class_declaration(self, tree):
        class_name = tree.children[1].value

        parent_name = None

        if len(tree.children) > 2 and isinstance(tree.children[2], Token) and tree.children[2].value == Constants.extends:
            parent_name = tree.children[3].value

        class_ = Class(name=class_name, address=increment_data_pointer(4), parent=parent_name)

        type_ = Type(name=class_name, class_obj=class_, size=4)

        tree.symbol_table.add_type(type_)

        class_symbol_table = SymbolTable(parent=tree.symbol_table)

        class_stack.append(class_)

        for subtree in tree.children:
            if isinstance(subtree, Tree) and subtree.data == 'field':
                subtree.symbol_table = class_symbol_table
                initial_stack_len = len(stack)
                self.visit(subtree)
                while initial_stack_len < len(stack):
                    stack.pop()

        class_stack.pop()

        class_.set_fields(
            member_data=class_symbol_table.variables,
            member_functions=class_symbol_table.functions
        )


class SymbolTableParentUpdater(Visitor):
    def __default__(self, tree):
        for child in tree.children:
            if isinstance(child, Tree):
                child.parent = tree


class TypeVisitor(Interpreter):

    def __default__(self, tree):
        self.visit_children(tree)

    def variable(self, tree):
        global variable_inits_code
        type_ = self.visit(tree.children[0])
        var_name = tree.children[1].value
        variable = tree.symbol_table.find_var(var_name, tree=tree)
        variable.type_ = type_

    def type(self, tree):
        type_name = tree.children[0].value
        type_ = tree.symbol_table.get_type(type_name)
        return type_

    def array_type(self, tree):
        arr_type = self.visit(tree.children[0])
        type_ = Type(name="array", arr_type=arr_type)

        return type_

    def class_declaration(self, tree):
        class_obj = tree.symbol_table.get_type(tree.children[1].value).class_obj
        if class_obj.parent:
            parent_class = tree.symbol_table.get_type(class_obj.parent).class_obj
            if not parent_class:
                raise SemanticError(37)
            class_obj.parent = parent_class
        for child in tree.children:
            if isinstance(child, Tree):
                self.visit(child)

    def function_decl(self, tree):
        return_type = Type(DecafTypes.void_type)
        if isinstance(tree.children[0], Tree):
            return_type = self.visit(tree.children[0])
        func_name = tree.children[1].value
        function = tree.symbol_table.get_function(func_name, tree=tree)
        function.return_type = return_type
        for child in tree.children:
            if isinstance(child, Tree):
                self.visit(child)
