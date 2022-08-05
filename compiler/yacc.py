import logging
import ply.yacc as yacc
from compiler.lexer import tokens


def p_program(p):
    """Program : ProgramMacroExpr ProgramDeclExpr"""
    p[0] = ('program', p[1], p[2])


def p_macro(p):
    """Macro : IMPORT T_STRINGLITERAL"""
    p[0] = ('macro', p[1], p[2])


def p_program_macro_expr(p):
    """ProgramMacroExpr : Macro ProgramMacroExpr
    | empty
    """
    if len(p) == 3:
        p[0] = ('program_macro_expr', p[1], p[2])
    else:
        p[0] = ('program_macro_expr', p[1])


def p_program_decl_expr(p):
    """ProgramDeclExpr : Decl ProgramDeclExpr
    | Decl
    """
    if len(p) == 3:
        p[0] = ('program_decl_expr', p[1], p[2])
    else:
        p[0] = ('prgram_decl_expr', p[1])


def p_variable_decl(p):
    """VariableDecl : Variable SEMICOLON"""
    print(p[1])
    p[0] = ('variable_decl', p[1], p[2])


def p_variable(p):
    """Variable : Type T_ID"""
    p[0] = ('variable', p[1], p[2])


def p_function_decl(p):
    """FunctionDecl : Type T_ID LPAREN Formals RPAREN StmtBlock
    | VOID T_ID LPAREN Formals RPAREN StmtBlock
    """
    p[0] = ('function_decl', p[1], p[2], p[3], p[4], p[5], p[6])


def p_decl(p):
    """Decl : VariableDecl
    | FunctionDecl
    | ClassDecl
    | InterfaceDecl
    """
    p[0] = ('decl', p[1])


def p_variable_decl_expr(p):
    """VariableDeclExpr : empty
    | VariableDeclExpr VariableDecl
    """
    if len(p) == 3:
        p[0] = ('variable_decl_expr', p[1], p[2])
    else:
        p[0] = ('variable_decl_expr', p[1])


def p_formals(p):
    """Formals : VariableExpr
    | empty
    """
    p[0] = ('formals', p[1])


def p_class_decl(p):
    """ClassDecl : CLASS T_ID EXTENDS T_ID IMPLEMENTS TIDEXPR LBRACE FieldExpr RBRACE
    | CLASS T_ID IMPLEMENTS TIDEXPR LBRACE FieldExpr RBRACE
    | CLASS T_ID EXTENDS T_ID LBRACE FieldExpr RBRACE
    | CLASS T_ID LBRACE FieldExpr RBRACE
    """
    if len(p) == 10:
        p[0] = ('class_decl', p[1], p[2], p[3], p[4], p[5], p[6], p[7], p[8], p[9])
    elif len(p) == 8:
        p[0] = ('class_decl', p[1], p[2], p[3], p[4], p[5], p[6], p[7])
    else:
        p[0] = ('class_decl', p[1], p[2], p[3], p[4], p[5])


def p_tid_expr(p):
    """TIDEXPR : T_ID
    | T_ID COMMA TIDEXPR
    """
    if len(p) == 2:
        p[0] = ('tide_expr', p[1])
    else:
        p[0] = ('tide_expr', p[1], p[2], p[3])


def p_field_expr(p):
    """FieldExpr : Field FieldExpr
    | empty
    """
    if len(p) == 3:
        p[0] = ('field_expr', p[1], p[2])
    else:
        p[0] = ('field_expr', p[1])


def p_variable_expr(p):
    """VariableExpr : Variable
    | Variable COMMA VariableExpr
    """
    if len(p) == 2:
        p[0] = ('variable_expr', p[1])
    else:
        p[0] = ('variable_expr', p[1], p[2], p[3])


def p_field(p):
    """Field : AccessMode  VariableDecl
    | AccessMode  FunctionDecl
    """
    p[0] = ('field', p[1], p[2])


def p_access_mode(p):
    """AccessMode : PRIVATE
    | PROTECTED
    | PUBLIC
    | empty
    """
    p[0] = ('access_mode', p[1])


def p_interface_decl(p):
    """InterfaceDecl : INTERFACE T_ID LBRACE PrototypeExpr RBRACE"""
    p[0] = ('interface_decl', p[1], p[2], p[3], p[4], p[5])


def p_prototype(p):
    """ProtoType : Type T_ID LPAREN Formals RPAREN SEMICOLON
    | VOID T_ID LPAREN Formals RPAREN SEMICOLON
    """
    p[0] = ('prototype', p[1], p[2], p[3], p[4], p[5], p[6])


def p_prototype_expr(p):
    """PrototypeExpr :  ProtoType PrototypeExpr
    | empty
    """
    if len(p) == 3:
        p[0] = ('prototype_expr', p[1], p[2])
    else:
        p[0] = ('prototype_expr', p[1])


def p_stmt_block(p):
    """StmtBlock : LBRACE VariableDeclExpr StmtExpr RBRACE"""
    p[0] = ('stmt_block', p[1], p[2], p[3], p[4])


def p_stmt(p):
    """Stmt : Expr SEMICOLON
    | SEMICOLON
    | IfStmt
    | WhileStmt
    | ForStmt
    | BreakStmt
    | ContinueStmt
    | ReturnStmt
    | PrintStmt
    | StmtBlock
    """
    if len(p) == 3:
        p[0] = ('stmt', p[1], p[2])
    else:
        p[0] = ('stmt', p[1])


def p_stmt_expr(p):
    """StmtExpr : empty
    | Stmt StmtExpr
    """
    if len(p) == 3:
        p[0] = ('stmt_expr', p[1], p[2])
    else:
        p[0] = ('stmt_expr', p[1])


def p_if_stmt(p):
    """IfStmt : IF LPAREN Expr RPAREN Stmt
    | IF LPAREN Expr RPAREN Stmt ELSE Stmt
    """
    if len(p) == 6:
        p[0] = ('if_stmt', p[1], p[2], p[3], p[4], p[5])
    else:
        p[0] = ('if_stmt', p[1], p[2], p[3], p[4], p[5], p[6], p[7])


def p_while_stmt(p):
    """WhileStmt : WHILE LPAREN Expr RPAREN Stmt"""
    p[0] = ('while_stmt', p[1], p[2], p[3], p[4], p[5])


def p_for_stmt(p):
    """ForStmt : FOR LPAREN Expr SEMICOLON Expr SEMICOLON Expr RPAREN Stmt
    | FOR LPAREN SEMICOLON Expr SEMICOLON Expr RPAREN Stmt
    | FOR LPAREN Expr SEMICOLON Expr SEMICOLON RPAREN Stmt
    | FOR LPAREN SEMICOLON Expr SEMICOLON RPAREN Stmt
    """
    if len(p) == 10:
        p[0] = ('for_stmt', p[1], p[2], p[3], p[4], p[5], p[6], p[7], p[8], p[9])
    elif len(p) == 9:
        p[0] = ('for_stmt', p[1], p[2], p[3], p[4], p[5], p[6], p[7], p[8])
    elif len(p) == 8:
        p[0] = ('for_stmt', p[1], p[2], p[3], p[4], p[5], p[6], p[7])


def p_return_stmt(p):
    """ReturnStmt : RETURN SEMICOLON
    | RETURN Expr SEMICOLON
    """
    if len(p) == 3:
        p[0] = ('return_stmt', p[1], p[2])
    else:
        p[0] = ('return_stmt', p[1], p[2], p[3])


def p_break_stmt(p):
    """BreakStmt : BREAK SEMICOLON"""
    p[0] = ('break_stmt', p[1], p[2])


def p_continue_stmt(p):
    """ContinueStmt : CONTINUE SEMICOLON"""
    p[0] = ('continue_stmt', p[1], p[2])


def p_print_expr(p):
    """PrintExpr : Expr
    | Expr COMMA PrintExpr
    """
    if len(p) == 2:
        p[0] = ('print_expr', p[1])
    else:
        p[0] = ('print_expr', p[1], p[2], p[3])


def p_print_stmt(p):
    """PrintStmt : PRINT LPAREN PrintExpr RPAREN SEMICOLON"""
    p[0] = ('print_stmt', p[1], p[2], p[3], p[4], p[5])


def p_expr_l_temp(p):
    """ExprLValueTemp : EQUAL Expr
    | empty
    """
    if len(p) == 3:
        p[0] = ('expr_l_temp', p[1], p[2])
    else:
        p[0] = ('expr_l_temp', p[1])


def p_math_func(p):
    """MathFunc : PLUS Expr
    | MINUS Expr
    | DIVIDE Expr
    | TIMES Expr
    | MODULE Expr
    | BIGGER_THAN Expr
    | BIGGER_THAN_OR_EQUAL Expr
    | SMALLER_THAN Expr
    | SMALLER_THAN_OR_EQUAL Expr
    | LOGICAL_EQUAL Expr
    | LOGICAL_NON_EQUAL Expr
    | LOGICAL_AND Expr
    | LOGICAL_OR Expr
    """
    p[0] = ('math_func', p[1], p[2])


def p_expr(p):
    """Expr : LValue ExprLValueTemp
    | Constant
    | THIS
    | Call
    | LPAREN Expr RPAREN
    | Expr MathFunc
    | MINUS Expr
    | EXCLAMATION Expr
    | READINTEGER LPAREN RPAREN
    | READLINE LPAREN RPAREN
    | NEW T_ID
    | NEWARRAY LPAREN Expr COMMA Type RPAREN
    | ITOD LPAREN Expr RPAREN
    | DTOI LPAREN Expr RPAREN
    | ITOB LPAREN Expr RPAREN
    | BTOI LPAREN Expr RPAREN
    """
    if len(p) == 3:
        p[0] = ('expr', p[1], p[2])
    elif len(p) == 2:
        p[0] = ('expr', p[1])
    elif len(p) == 4:
        p[0] = ('expr', p[1], p[2], p[3])
    elif len(p) == 7:
        p[0] = ('expr', p[1], p[2], p[3], p[4], p[5], p[6])
    else:
        p[0] = ('expr', p[1], p[2], p[3], p[4])


def p_expr_temp(p):
    """ExprTemp : COMMA ExprExpr
    | empty
    """
    if len(p) == 3:
        p[0] = ('expr_temp', p[1], p[2])
    else:
        p[0] = ('expr_temp', p[1])


def p_expr_expr(p):
    """ExprExpr : Expr ExprTemp"""
    p[0] = ('expr_expr', p[1], p[2])


def p_l_value(p):
    """LValue : T_ID
    | Expr LBRACKET Expr RBRACKET
    | Expr POINT T_ID
    """
    if len(p) == 5:
        p[0] = ('l_value', p[1], p[2], p[3], p[4])
    elif len(p) == 4:
        p[0] = ('l_value', p[1], p[2], p[3])
    else:
        p[0] = ('l_value', p[1])


def p_call_temp(p):
    """CallTemp : T_ID LPAREN Actuals RPAREN"""
    p[0] = ('call_temp', p[1], p[2], p[3], p[4])


def p_call(p):
    """Call : CallTemp
    | Expr POINT CallTemp
    """
    if len(p) == 4:
        p[0] = ('call', p[1], p[2], p[3])
    else:
        p[0] = ('call', p[1])


def p_actual_temp(p):
    """ActualTemp : empty
    | COMMA ActualExpr
    """
    if len(p) == 3:
        p[0] = ('actual_temp', p[1], p[2])
    else:
        p[0] = ('actual_temp', p[1])


def p_actual_expr(p):
    """ActualExpr : Expr ActualTemp"""
    p[0] = ('actual_expr', p[1], p[2])


def p_actuals(p):
    """Actuals : ActualExpr
    | empty
    """
    p[0] = ('actuals', p[1])


def p_constant(p):
    """Constant : T_INTLITERAL
     | T_DOUBLELITERAL
     | T_BOOLEANLITERAL
     | T_STRINGLITERAL
     | NULL
    """
    p[0] = ('constant', p[1])


def p_empty(p):
    """empty :"""
    p[0] = ('empty', None)


def p_type(p):
    """Type : INT
    | DOUBLE
    | BOOL
    | STRING
    | T_ID
    | Type LBRACKET RBRACKET
    """
    if len(p) == 4:
        p[0] = ('type', p[1], p[2], p[3])
    else:
        p[0] = ('type', p[1])


def p_error(p):
    raise SyntaxError


logging.basicConfig(
    level=logging.CRITICAL,
)
log = logging.getLogger()
parser = yacc.yacc(debug=True, debuglog=log)
