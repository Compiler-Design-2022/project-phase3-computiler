class SemanticError(Exception):
    def __init__(self, token=100):
        super(SemanticError, self).__init__()
        self.token = token
