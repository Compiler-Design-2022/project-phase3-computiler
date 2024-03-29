from semantic_error import SemanticError


class Class:
    def __init__(self, name, parent=None, interfaces=None, address=None):
        self.parent = parent
        self.interfaces = interfaces
        self.name = name
        self.address = address
        self.member_data = None
        self.member_functions = None
        self.accesses = {}

    def set_fields(self, member_data, member_functions):
        self.member_data = member_data
        self.member_functions = member_functions

    def get_function_index(self):
        if not self.parent:
            return 0
        return self.parent.get_function_index() + len(self.parent.member_functions)

    def get_function(self, name, raise_error=True):
        if self.parent:
            function, index = self.parent.get_function(name, raise_error=False)
            if function is not None:
                return function, index

        if name in self.member_functions:
            return self.member_functions[name], self.get_function_index() + list(self.member_functions.keys()).index(name)

        if raise_error:
            raise SemanticError()
        return None, None

    def get_access(self, name):
        if name in self.accesses:
            return self.accesses[name]

        elif self.parent:
            return self.parent.get_access(name)

    def can_upcast(self, class_obj):
        if self.name == class_obj.name:
            return True
        if not self.parent:
            return False
        return self.parent.can_upcast(class_obj)


class Type:
    def __init__(self, name, size=None, arr_type=None, class_obj=None):
        self.name = name
        self.size = size
        self.arr_type = arr_type
        self.class_obj = class_obj

    def is_same(self, target):
        if self.name != target.name and self.arr_type:
            return self.arr_type.is_same(target)
        if self.name != target.name:
            return False

        if (self.arr_type and not target.arr_type) or (not self.arr_type and target.arr_type):
            return False

        if self.class_obj and not target.class_obj:
            return False
        if self.class_obj:
            return self.class_obj == target.class_obj
        if self.arr_type:
            return self.arr_type.is_same(target.arr_type)
        return True

    def same_or_can_upcast(self, type_name):
        if self.arr_type:
            return self.is_same(type_name)

        if self.class_obj and self.class_obj.can_upcast(type_name.class_obj):
            return True

        return self.name == type_name.name


class Variable:
    def __init__(self, var_type: Type, address=None, name=None):
        self.name = name
        self.var_type = var_type
        self.address = address


class Function:
    def __init__(self, name, formals, return_type, address=0, size=0, prefix_class=''):
        self.name = prefix_class + name
        self.formals = formals
        self.return_type = return_type
        self.address = address
        self.size = size


class SymbolTable:
    symbol_tables = []

    def __init__(self, parent=None):
        self.types = dict()
        self.parent = parent
        self.functions = {}
        self.variables = {}
        SymbolTable.symbol_tables.append(self)

    def get_type(self, var_type, rise_error=True, is_arr_type=False):
        if var_type in self.types.keys():
            return self.types[var_type]
        if self.parent:
            return self.parent.get_type(var_type=var_type, rise_error=rise_error, is_arr_type=is_arr_type)
        if rise_error:
            raise SemanticError(32)

    def add_type(self, var_type: Type):
        if self.get_type(var_type=var_type.name, rise_error=False, is_arr_type=True):
            raise SemanticError(31)
        else:
            self.types[var_type.name] = var_type

    def add_var(self, var: Variable):
        if self.find_var(var.name, error=False, depth_one=True):
            raise SemanticError(33)

        self.variables[var.name] = var

    def add_func(self, func: Function, tree=None):
        if self.get_function(func.name, rise_error=False, depth=1):
            raise SemanticError(30)

        self.functions[func.name] = func

    def get_function(self, func_name, tree=None, rise_error=True, depth=1):
        if self.parent and depth == 1:
            return self.parent.get_function(func_name, tree, rise_error)
        if func_name in self.functions:
            return self.functions.get(func_name, SemanticError(36))

        if rise_error:
            raise SemanticError(35)
        return None

    def find_var(self, name, tree=None, error=True, depth_one=False):
        if name in self.variables:
            return self.variables[name]
        if self.parent and not depth_one:
            return self.parent.find_var(name, tree, error)

        if error:
            raise SemanticError(34)
        return None
