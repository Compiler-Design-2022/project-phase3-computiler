from lark import Lark, ParseError
from lark.visitors import Interpreter
from compiler.mips_codes import MIPS
from compiler.decaf_enums import Constants
from compiler.semantic_error import SemanticError
from compiler.symbol_table import Variable, SymbolTable, Type

stack = []


class CodeGenerator(Interpreter):
    def constant(self, tree):
        const_token_type = tree.children[0].type
        output_code = ''
        var_type = None
        if const_token_type == Constants.bool_const:
            value = int(tree.children[0].value)
            var_type = tree.symbol_table.get_type('bool')
            output_code = MIPS.bool_const.format(value)
        elif const_token_type == Constants.int_const:
            value = int(tree.children[0].value)
            var_type = tree.symbol_table.get_type('int')
            output_code = MIPS.int_const.format(value)
        elif const_token_type == Constants.double_const:
            pass
        elif const_token_type == Constants.str_const:
            pass
        elif const_token_type == Constants.null_const:
            var_type = tree.symbol_table.get_type('null')
            output_code = MIPS.null_const
        stack.append(Variable(name=None, var_type=var_type))
        return output_code


def prepare_main_tree(tree):
    tree.symbol_table = SymbolTable()
    tree.symbol_table.add_type(Type('int', 4))
    tree.symbol_table.add_type(Type('double', 8))
    tree.symbol_table.add_type(Type('bool', 4))
    tree.symbol_table.add_type(Type('void', 0))
    tree.symbol_table.add_type(Type('string', 8))
    tree.symbol_table.add_type(Type('array', 4))


def generate(input_code):
    parser = Lark.open('./grammar.lark', parser="lalr", propagate_positions=True)
    try:
        tree = parser.parse(input_code)
        prepare_main_tree(tree)
        mips_code = CodeGenerator.visit(tree)
    except ParseError as e:
        return e
    except SemanticError:
        mips_code = MIPS.semantic_error
    return mips_code


if __name__ == "__main__":
    inputfile = 'example.d'

    # inputfile = '../tmp/in.d'
    code = ""
    with open(inputfile, "r") as input_file:
        code = input_file.read()
    code = generate(code)
    print("#### code ")
    print(code)

    output_file = open("../tmp/res.mips", "w")
    output_file.write(code)
