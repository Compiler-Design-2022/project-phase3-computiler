class SemanticError(Exception):
    def __init__(self, message='', line=None, col=None):
        self.message = message
        self.line = 0
        self.col = 0
        if line:
            self.line = line
        if col:
            self.col = col
        

    def __str__(self) -> str:
        return f"line : {self.line} /// column : {self.col} /// message : {self.message}"
