class SymbolTable:
    pass


class Type:
    def __init__(self, name, size):
        self.name = name
        self.size = size

    def is_same(self, target):
        if target.name == self.name and target.size == self.size:
            return True
        return False


class Variable:
    def __init__(self, name, var_type, size, address):
        self.name = name
        self.var_type = var_type
        self.size = size
        self.address = address


class Function:
    def __init__(self, name, formals, return_type, address, size):
        self.name = name
        self.formals = formals
        self.return_type = return_type
        self.address = address
        self.size = size
