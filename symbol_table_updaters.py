from lark.visitors import Interpreter
from lark import Tree, Visitor

from semantic_error import SemanticError
from symbol_table import SymbolTable, Variable, Type, Function

stack = []
class_stack = []


def IncDataPointer(size):
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
    """
    Each Node set it's children SymbolTables. 
    If defining a method make sure to set all children symbol tables
    and visit children. default gives every child (non token) parent
    symbol table
    """

    def type(self, tree):
        type_ = tree.children[0].value
        stack.append(Type(type_))

    def function_decl(self, tree):
        # stack frame
        #			-------------------
        # 			| 	argument n    |			\
        # 			| 		...		  |				=> caller
        # 			| 	argument 1    |			/
        #			-------------------
        #  $fp -> 	| saved registers |			\
        #  $fp - 4	| 		...		  |			 \
        #			-------------------				=> callee
        # 			| 	local vars	  |			 /
        # 			| 		...		  |			/
        #  $sp ->	| 		...		  |
        #  $sp - 4	-------------------

        # access arguments with $fp + 4, $fp + 8, ...

        # check if function is a member function
        function_class = None
        if len(class_stack) > 0:
            function_class = class_stack[-1]

        # type
        type_ = Type("void")  # void

        if isinstance(tree.children[0], Tree):
            tree.children[0].symbol_table = tree.symbol_table
            self.visit(tree.children[0])
            type_ = stack.pop()

        func_name = tree.children[1].value

        # set formal scope and visit formals
        formals_symbol_table = SymbolTable(parent=tree.symbol_table)
        tree.children[2].symbol_table = formals_symbol_table

        # TODO
        # not sure what to do here and what types do formals need to be
        # now they are list of types:Type (but without size)
        sp_initial = len(stack)
        self.visit(tree.children[2])
        formals = []

        while len(stack) > sp_initial:
            f = stack.pop()
            formals.append(f)

        formals = formals[::-1]

        # Add this to formals and symbol table

        # set body scope
        body_symbol_table = SymbolTable(parent=formals_symbol_table)
        tree.children[3].symbol_table = body_symbol_table
        self.visit(tree.children[3])

        # change function label in mips code to not get confused with other functions with same name
        prefix_label = ''
        if function_class:
            prefix_label = "class_" + function_class.name + "_"

        tree.symbol_table.add_func(Function(
            name=func_name,
            return_type=type_,
            formals=formals,
        ), tree)

    def variable(self, tree):

        # check if variable is a member data
        variable_class = None
        if len(class_stack) > 0:
            variable_class = class_stack[-1]

        tree.children[0].symbol_table = tree.symbol_table
        self.visit(tree.children[0])
        type_ = stack.pop()

        var_name = tree.children[1].value

        var = Variable(
            name=var_name,
            var_type=type_,
            address=IncDataPointer(4),
        )

        tree.symbol_table.add_var(var, tree)

        # We need var later (e.g. in formals of funtions)
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


def stmt_block(self, tree):
    new_block_table = SymbolTable(parent=tree.symbol_table)
    for child in tree.children:
        if isinstance(child, Tree):
            child.symbol_table = new_block_table
            self.visit(child)


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

    def class_decl(self, tree):

        class_name = tree.children[1].value

        class_ = tree.symbol_table.get_type(class_name).class_ref

        if class_.parent:
            parent_class = tree.symbol_table.get_type(class_.parent).class_ref
            if not parent_class:
                raise SemanticError(37)

            class_.parent = parent_class

        for child in tree.children:
            if isinstance(child, Tree):
                self.visit(child)

    def function_decl(self, tree):

        # type
        type_ = Type("void")
        if isinstance(tree.children[0], Tree):
            type_ = self.visit(tree.children[0])

        # name
        func_name = tree.children[1].value
        function = tree.symbol_table.get_function(func_name, tree=tree)

        function.return_type = type_

        for child in tree.children:
            if isinstance(child, Tree):
                self.visit(child)
