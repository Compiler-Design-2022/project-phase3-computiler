from lark import Tree, Token

tt = ('program', ('program_macro_expr', ('empty', None)), ('prgram_decl_expr', ('decl', ('function_decl', ('type', 'int'), 'main', '(', ('formals', ('empty', None)), ')', ('stmt_block', '{', ('variable_decl_expr', ('variable_decl_expr', ('variable_decl_expr', ('empty', None)), ('variable_decl', ('variable', ('type', 'int'), 'a'), ';')), ('variable_decl', ('variable', ('type', 'int'), 'b'), ';')), ('stmt_expr', ('stmt', ('expr', ('l_value', 'b'), ('expr_l_temp', '=', ('expr', ('constant', '2')))), ';'), ('stmt_expr', ('stmt', ('expr', ('l_value', 'a'), ('expr_l_temp', '=', ('expr', ('expr', ('constant', '1')), ('math_func', '+', ('expr', ('l_value', 'b'), ('expr_l_temp', ('empty', None))))))), ';'), ('stmt_expr', ('stmt', ('print_stmt', 'Print', '(', ('print_expr', ('expr', ('l_value', 'a'), ('expr_l_temp', ('empty', None)))), ')', ';')), ('stmt_expr', ('empty', None))))), '}')))))


def gen_lark_tree(input_code: tuple):
    if not input_code:
        return
    new_tree = Tree(data=input_code[0], children=[])
    for i in input_code[1:]:
        if not isinstance(i, tuple):
            new_tree.children.append(Token(input_code[0], i))
        else:
            new_tree.children.append(gen_lark_tree(i))
    return new_tree
