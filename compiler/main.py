import logging
from compiler.ply_2_lark_converter import gen_lark_tree
from compiler.preprocessor import run_preprocess
from compiler.yacc import parser
from compiler.gen_code import generate_code

def run(input_file_address: str) -> str:
    result = ''
    with open(input_file_address) as input_file:
        data = input_file.read()
    data = run_preprocess(input_data=data)
    logging.basicConfig(
        level=logging.CRITICAL,
    )
    log = logging.getLogger()
    try:
        tree_data = parser.parse(input=data, debug=True)
        tree = gen_lark_tree(tree_data)
        result = generate_code(tree)
        output_file = open("../tmp/res.mips", "w")
        output_file.write(result)
        return "Successful"
    except SyntaxError as e:
        return "Syntax Error"
        #return False
