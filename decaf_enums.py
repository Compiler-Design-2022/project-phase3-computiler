class Constants:
    function_decl = 'function_decl'
    bool_const = 'BOOLCONSTANT'
    int_const = 'INTCONSTANT'
    double_const = 'DOUBLECONSTANT'
    str_const = 'STRINGCONSTANT'
    null_const = 'NULL'
    field = 'field'

class DecafTypes:
    bool_type = 'bool'
    int_type = 'int'
    double_type = 'double'
    str_type = 'string'
    null_type = 'null'
    array_type = 'array'
    void_type = 'void'


class LoopLabels:
    while_start_label = "while_start_{version}"
    while_end_label = "end_while_{version}"
    for_break_label = "for_end_{version}"
    for_continue_label = "for_continue_label_{version}"
