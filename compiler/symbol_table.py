from compiler.semantic_error import SemanticError


class Type:
    def __init__(self, name, size=None):
        self.name = name
        self.size = size

    def is_same(self, target):
        if target.name == self.name and target.size == self.size:
            return True
        return False


class Variable:
    def __init__(self, var_type: Type, address=None, name=None):
        self.name = name
        self.var_type = var_type
        self.address = address


class Function:
    def __init__(self, name, formals, return_type, address, size):
        self.name = name
        self.formals = formals
        self.return_type = return_type
        self.address = address
        self.size = size


class SymbolTable:
    def __init__(self):
        self.types = dict()
        self.parent = None
        self.functions = {}

    def get_type(self, var_type, rise_error=True, is_arr_type=False):
        if var_type in self.types.keys():
            return self.types[var_type]
        if self.parent:
            return self.parent.get_type(var_type=var_type, rise_error=rise_error, is_arr_type=is_arr_type)
        if rise_error:
            raise SemanticError()

    def add_type(self, var_type: Type):
        if self.get_type(var_type=var_type.name, rise_error=False, is_arr_type=True):
            raise SemanticError()
        else:
            self.types[var_type.name] = var_type

    def get_function(self, func_name, tree=None, rise_error=True, depth=1):
        if self.parent and depth == 1:
            return self.parent.find_func(func_name, tree, rise_error)
        if func_name in self.functions:
            return self.functions.get(func_name, SemanticError())

        if rise_error:
            raise SemanticError()
        return None

    def find_type(self, name, tree=None, error=True, depth_one=False):
        if name in self.types:
            return self.types[name]
        if self.parent and not depth_one:
            return self.parent.find_type(name, tree, error)

        if error:
            raise SemanticError(tree=tree)
        return None
