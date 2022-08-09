from lark import Tree


class SemanticError(Exception):
    def __init__(self, tree: Tree = None):
        super(SemanticError, self).__init__()
