from compiler.semantic_error import SemanticError


class Type:
    def __init__(self, name, size):
        self.name = name
        self.size = size

    def is_same(self, target):
        if target.name == self.name and target.size == self.size:
            return True
        return False


class Variable:
    def __init__(self, name, var_type: Type, address=None):
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
