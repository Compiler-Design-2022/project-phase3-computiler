import ply.lex as lex

reserved = {
    '__func__',
    '__line__',
    'bool',
    'break',
    'btoi',
    'class',
    'extends',
    'implements',
    'continue',
    'define',
    'double',
    'dtoi',
    'else',
    'for',
    'if',
    'import',
    'int',
    'itob',
    'itod',
    'new',
    'NewArray',
    'null',
    'Print',
    'private',
    'public',
    'protected',
    'ReadInteger',
    'ReadLine',
    'return',
    'string',
    'this',
    'void',
    'interface',
    'while',
}
tokens = [
    ('PLUS_EQUAL', r'\+\='),
    ('MINUS_EQUAL', r'-\='),
    ('MULTIPLY_EQUAL', r'\*\='),
    ('DIVIDE_EQUAL', r'/\='),
    ('T_DOUBLELITERAL', r'([0-9]+(\.[0-9]*)((e|E)(\+|-)?[0-9]+)?|([0-9]+(\.[0-9]+)((e|E)(\+|-)?[0-9]+)?))'),
    ('T_INTLITERAL', r'(0(x|X)[0-9a-fA-F]+|([0-9]+))'),
    ('T_COMMENT', r'(/\*([^*]|[\r\n]|(\*+([^*/]|[\r\n])))*\*+/)'),
    ('T_SINGLE_COMMENT', r'//.*'),
    ('T_STRINGLITERAL', r'\"(\\\"|[^\"])*\"'),
    ('T_BOOLEANLITERAL', r'(?<![a-zA-Z0-9_])(true|false)(?![a-zA-Z0-9_])'),
    ('T_ID', r'[a-zA-Z_][a-zA-Z_0-9]*'),
    ('PLUS', r'\+'),
    ('POINT', r'\.'),
    ('MINUS', r'\-'),
    ('TIMES', r'\*'),
    ('DIVIDE', r'/'),
    ('LPAREN', r'\('),
    ('RPAREN', r'\)'),
    ('LBRACE', r'\{'),
    ('RBRACE', r'\}'),
    ('LBRACKET', r'\['),
    ('RBRACKET', r'\]'),
    ('SEMICOLON', r';'),
    ('BAR', r'\|'),
    ('EQUAL', r'\='),
    ('MODULE', r'%'),
    ('LOGICAL_OR', r'\|\|'),
    ('LOGICAL_AND', r'\&\&'),
    ('LOGICAL_EQUAL', r'\=\='),
    ('LOGICAL_NON_EQUAL', r'\!\='),
    ('BIGGER_THAN', r'\>'),
    ('BIGGER_THAN_OR_EQUAL', r'\>\='),
    ('SMALLER_THAN', r'\<'),
    ('SMALLER_THAN_OR_EQUAL', r'\<\='),
    ('COMMA', r'\,'),
    ('EXCLAMATION', r'!'),
    ('ignore', '\t'),
    ('newline', r'\n+'),
    ('SKIP', r'[ \t\v\f]+'),      												# Skip over spaces and tabs
	('MISMATCH', r'.')
         ] + list(reserved.values())

# t_POINT =
# t_PLUS =
# t_MINUS =
# t_TIMES =
# t_DIVIDE =
# t_LPAREN =
# t_RPAREN =
# t_LBRACE =
# t_RBRACE =
# t_LBRACKET =
# t_RBRACKET =
# t_SEMICOLON =
# t_BAR =
# t_EQUAL =
# t_LOGICAL_OR =
# t_MODULE =
# t_LOGICAL_AND =
# t_LOGICAL_EQUAL =
# t_PLUS_EQUAL =
# t_MINUS_EQUAL =
# t_MULTIPLY_EQUAL =
# t_DIVIDE_EQUAL =
# t_LOGICAL_NON_EQUAL =
# t_BIGGER_THAN =
# t_BIGGER_THAN_OR_EQUAL =
# t_SMALLER_THAN =
# t_SMALLER_THAN_OR_EQUAL =
# t_COMMA =
# t_EXCLAMATION =
# t_ignore = ' '

# reserved Regular Expressions
# t_FUNC = r'__func__'
# t_LINE = r'__line__'
# t_BOOL = r'bool'
# t_BREAK = r'break'
# t_BTOI = r'btoi'
# t_CLASS = r'class'
# t_EXTENDS = r'extends'
# t_IMPLEMENTS = r'implements'
# t_INTERFACE = r'interface'
# t_CONTINUE = r'continue'
# t_DEFINE = r'define'
# t_DOUBLE = r'double'
# t_DTOI = r'dtoi'
# t_ELSE = r'else'
# t_FOR = r'for'
# t_IF = r'if'
# t_IMPORT = r'import'
# t_INT = r'int'
# t_ITOB = r'itob'
# t_ITOD = r'itod'
# t_NEW = r'new'
# t_NEWARRAY = r'NewArray'
# t_NULL = r'null'
# t_PRINT = r'Print'
# t_PRIVATE = r'private'
# t_PUBLIC = r'public'
# t_PROTECTED = r'protected'
# t_READINTEGER = r'ReadInteger'
# t_READLINE = r'ReadLine'
# t_RETURN = r'return'
# t_STRING = r'string'
# t_THIS = r'this'
# t_VOID = r'void'
# t_WHILE = r'while'

# t_T_ID =
# t_T_INTLITERAL =


def t_T_STRINGLITERAL(t):

    return t


def t_T_DOUBLELITERAL(t):

    return t


def t_newline(t):

    t.lexer.lineno += len(t.value)


def t_T_COMMENT(t):

    pass


def t_T_SINGLE_COMMENT(t):

    pass


def t_T_BOOLEANLITERAL(t):

    t.type = reserved.get(t.value, 'T_BOOLEANLITERAL')
    return t


def t_error(t):
    print("UNDEFINED_TOKEN")
    t.lexer.skip(1)


def t_ID(t):
    r"""[a-zA-Z_][a-zA-Z_0-9]*"""
    t.type = reserved.get(t.value, 'T_ID')  # Check for reserved words
    return t


lexer = lex.lex()
