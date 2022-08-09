import logging
import ply.yacc as yacc
from compiler.lexer import tokens


def p_program(p):
    """Program : ProgramMacroExpr ProgramDeclExpr"""


def p_macro(p):
    """Macro : IMPORT T_STRINGLITERAL"""


def p_program_macro_expr(p):
    """ProgramMacroExpr : Macro ProgramMacroExpr
    | empty
    """


def p_program_decl_expr(p):
    """ProgramDeclExpr : Decl ProgramDeclExpr
    | Decl
    """


def p_variable_decl(p):
    """VariableDecl : Variable SEMICOLON"""
    print(p[1])


def p_variable(p):
    """Variable : Type T_ID"""
    pass


def p_function_decl(p):
    """FunctionDecl : Type T_ID LPAREN Formals RPAREN StmtBlock
    | VOID T_ID LPAREN Formals RPAREN StmtBlock
    """
    pass


def p_decl(p):
    """Decl : VariableDecl
    | FunctionDecl
    | ClassDecl
    | InterfaceDecl
    """


def p_variable_decl_expr(p):
    """VariableDeclExpr : empty
    | VariableDeclExpr VariableDecl
    """


def p_formals(p):
    """Formals : VariableExpr
    | empty
    """


def p_class_decl(p):
    """ClassDecl : CLASS T_ID EXTENDS T_ID IMPLEMENTS TIDEXPR LBRACE FieldExpr RBRACE
    | CLASS T_ID IMPLEMENTS TIDEXPR LBRACE FieldExpr RBRACE
    | CLASS T_ID EXTENDS T_ID LBRACE FieldExpr RBRACE
    | CLASS T_ID LBRACE FieldExpr RBRACE
    """


def p_tid_expr(p):
    """TIDEXPR : T_ID
    | T_ID COMMA TIDEXPR
    """


def p_field_expr(p):
    """FieldExpr : Field FieldExpr
    | empty
    """


def p_variable_expr(p):
    """VariableExpr : Variable
    | Variable COMMA VariableExpr
    """


def p_field(p):
    """Field : AccessMode  VariableDecl
    | AccessMode  FunctionDecl
    """


def p_access_modifier(p):
    """AccessMode : PRIVATE
    | PROTECTED
    | PUBLIC
    | empty
    """


def p_interface_decl(p):
    'InterfaceDecl : INTERFACE T_ID LBRACE PrototypeExpr RBRACE'


def p_prototype(p):
    """ProtoType : Type T_ID LPAREN Formals RPAREN SEMICOLON
    | VOID T_ID LPAREN Formals RPAREN SEMICOLON
    """


def p_prototype_expr(p):
    """PrototypeExpr :  ProtoType PrototypeExpr
    | empty
    """


def p_stmt_block(p):
    """StmtBlock : LBRACE VariableDeclExpr StmtExpr RBRACE"""


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
    pass


def p_stmt_expr(p):
    """StmtExpr : empty
    | Stmt StmtExpr
    """


def p_if_stmt(p):
    """IfStmt : IF LPAREN Expr RPAREN Stmt
    | IF LPAREN Expr RPAREN Stmt ELSE Stmt
    """
    pass


def p_while_stmt(p):
    """WhileStmt : WHILE LPAREN Expr RPAREN Stmt"""
    pass


def p_for_stmt(p):
    """ForStmt : FOR LPAREN Expr SEMICOLON Expr SEMICOLON Expr RPAREN Stmt
    | FOR LPAREN SEMICOLON Expr SEMICOLON Expr RPAREN Stmt
    | FOR LPAREN Expr SEMICOLON Expr SEMICOLON RPAREN Stmt
    | FOR LPAREN SEMICOLON Expr SEMICOLON RPAREN Stmt
    """
    pass


def p_return_stmt(p):
    """ReturnStmt : RETURN SEMICOLON
    | RETURN Expr SEMICOLON
    """
    pass


def p_break_stmt(p):
    """BreakStmt : BREAK SEMICOLON"""
    pass


def p_continue_stmt(p):
    """ContinueStmt : CONTINUE SEMICOLON"""
    pass


def p_print_expr(p):
    """PrintExpr : Expr
    | Expr COMMA PrintExpr
    """
    pass


def p_print_stmt(p):
    """PrintStmt : PRINT LPAREN PrintExpr RPAREN SEMICOLON"""
    pass


def p_expr_l_temp(p):
    """ExprLValueTemp : EQUAL Expr
    | empty
    """
    pass


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
    pass


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


def p_expr_temp(p):
    """ExprTemp : COMMA ExprExpr
    | empty
    """


def p_expr_expr(p):
    """ExprExpr : Expr ExprTemp"""


def p_l_value(p):
    """LValue : T_ID
    | Expr LBRACKET Expr RBRACKET
    | Expr POINT T_ID
    """
    pass


def p_call_temp(p):
    """CallTemp : T_ID LPAREN Actuals RPAREN"""
    pass


def p_call(p):
    """Call : CallTemp
    | Expr POINT CallTemp
    """
    pass


def p_actual_temp(p):
    """ActualTemp : empty
    | COMMA ActualExpr
    """
    pass


def p_actual_expr(p):
    """ActualExpr : Expr ActualTemp"""
    pass


def p_actuals(p):
    """Actuals : ActualExpr
    | empty
    """
    pass


def p_constant(p):
    """Constant : T_INTLITERAL
     | T_DOUBLELITERAL
     | T_BOOLEANLITERAL
     | T_STRINGLITERAL
     | NULL
    """
    pass


def p_empty(p):
    """empty :"""
    pass


def p_type(p):
    """Type : INT
    | DOUBLE
    | BOOL
    | STRING
    | T_ID
    | Type LBRACKET RBRACKET
    """
    pass


def p_error(p):
    raise SyntaxError


logging.basicConfig(
    level=logging.CRITICAL,
)
log = logging.getLogger()
parser = yacc.yacc(debug=True, debuglog=log)
