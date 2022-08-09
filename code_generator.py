from typing import List

from lark import Lark, ParseError
from lark.visitors import Interpreter

from decaf_enums import Constants, DecafTypes, LoopLabels
from globals import GlobalVariables
from mips_codes import MIPS, MIPSDouble, MIPSStr, MIPSConditionalStmt
from semantic_error import SemanticError
from symbol_table import Variable, SymbolTable, Type
from symbol_table_updaters import SymbolTableUpdater, SymbolTableParentUpdater


class CodeGenerator(Interpreter):
    VARIABLE_NAME_COUNT = 0

    @staticmethod
    def add_continue_and_break_target_labels(continue_label: str, break_label: str):
        GlobalVariables.CONTINUE_LOOP_STACK.append(continue_label)
        GlobalVariables.BREAK_LOOP_STACK.append(break_label)

    @staticmethod
    def pop_continue_and_break_target_labels():
        GlobalVariables.CONTINUE_LOOP_STACK.pop()
        GlobalVariables.BREAK_LOOP_STACK.pop()

    @staticmethod
    def get_version() -> int:
        CodeGenerator.change_var()
        return CodeGenerator.VARIABLE_NAME_COUNT

    def conditional_do_statement(self, tree, con_stmt, bre_stmt, stmt_children_number):
        CodeGenerator.add_continue_and_break_target_labels(
            continue_label=con_stmt,
            break_label=bre_stmt
        )
        statement_code = self.visit(tree.children[stmt_children_number])
        CodeGenerator.pop_continue_and_break_target_labels()
        return statement_code

    # TODO: how add break and continue?
    def while_stmt(self, tree):
        expression_code = self.visit(tree.children[1])
        GlobalVariables.STACK.pop()
        version = CodeGenerator.get_version()
        statement_code = self.conditional_do_statement(
            tree,
            LoopLabels.while_start_label.format(version=version),
            LoopLabels.while_end_label.format(version=version),
            2
        )
        output_code = MIPSConditionalStmt.while_stmt.format(
            expression_code=expression_code,
            version=version,
            while_statement=statement_code
        )
        return output_code

    def continue_stmt(self, tree):
        if not len(GlobalVariables.CONTINUE_LOOP_STACK):
            raise SemanticError()
        target_label = GlobalVariables.CONTINUE_LOOP_STACK[-1]
        output_code = MIPSConditionalStmt.continue_stmt.format(
            target_label=target_label
        )
        return output_code

    def break_stmt(self, tree):
        if not len(GlobalVariables.BREAK_LOOP_STACK):
            raise SemanticError()
        target_label = GlobalVariables.BREAK_LOOP_STACK[-1]
        output_code = MIPSConditionalStmt.break_stmt.format(
            target_label=target_label
        )
        return output_code

    def for_stmt(self, tree):
        pass

    def if_stmt(self, tree):
        expression_code = self.visit(tree.children[1])
        else_statement_code = ''
        statement_code = self.visit(tree.children[2])
        if len(tree.children) > 3:
            else_statement_code = self.visit(tree.children[4])
        output_code = MIPSConditionalStmt.if_stmt.format(
            expression_code=expression_code,
            version=CodeGenerator.get_version(),
            else_statement_code=else_statement_code,
            statement_code=statement_code
        )
        return output_code

    def stmt_block(self, tree):
        children_codes = self.visit_children(tree)
        codes = []
        for child_code in children_codes:
            if child_code:
                codes.append(child_code)
        return '\n'.join(codes)

    def declare_program(self, tree):
        variables = [item for item in tree.children if item.data == 'variable']
        functions = [item for item in tree.children if item.data == 'function_decl']
        classes = [item for item in tree.children if item.data == 'class_decl']

        result = "\n.text"

        for item in list(*variables, *functions, *classes):
            result += self.visit(item)

        result += MIPS.main.format(GlobalVariables.CLASS_INIT, GlobalVariables.VAR_INIT)
        result += MIPS.side_functions
        segment_code = MIPS.data_segment

        for index, item in GlobalVariables.CONSTANTS:
            segment_code += MIPS.constant_str.format(index, item)
        segment_code += '\n'
        for index, item in GlobalVariables.ARRAYS:
            segment_code += MIPS.array_base.format(index, item)
        segment_code += '\n'

        result = segment_code + result

        return result

    @staticmethod
    def are_types_invalid(var1: Variable, var2: Variable):
        return var1.var_type.name != var2.var_type.name

    @classmethod
    def are_boolean(cls, *variables: List[Variable]):
        non_booleans = [i for i in variables if i.var_type.name != DecafTypes.bool_type]
        return bool(len(non_booleans))

    @classmethod
    def change_var(cls):
        cls.VARIABLE_NAME_COUNT += 1

    def unary_neg(self, tree):
        output_code = self.visit(tree.children[0])
        var = GlobalVariables.STACK.pop()
        if var.var_type.name == DecafTypes.int_type:
            output_code += MIPS.unary_neg_int
        elif var.var_type.name == DecafTypes.double_type:
            output_code += MIPSDouble.unary_neg_double
        else:
            raise SemanticError()
        GlobalVariables.STACK.append(var)
        return output_code

    # module, unary negative
    def module(self, tree):
        var1, var2, expr1, expr2, output_code = self.prepare_calculations(tree)
        if var1.var_type.name != DecafTypes.int_type or var2.var_type.name != DecafTypes.int_type:
            raise SemanticError()
        output_code += MIPS.module_int
        var_type = tree.symbol_table.get_type('int')
        GlobalVariables.STACK.append(Variable(var_type=var_type))

    def assign(self, tree):
        l_var, r_var, expr1_code, expr2_code, output_code = self.prepare_calculations(tree)
        if CodeGenerator.are_types_invalid(l_var, r_var):
            raise SemanticError()
        if l_var.var_type.name == DecafTypes.int_type:
            output_code += MIPS.assignment_int
        GlobalVariables.STACK.append(l_var)
        return output_code

    def div(self, tree):
        var1, var2, expr1_code, expr2_code, output_code = self.prepare_calculations(tree)
        if CodeGenerator.are_types_invalid(var1, var2) and not CodeGenerator.is_var_int_or_double(var1):
            raise SemanticError()
        if var1.var_type.name == DecafTypes.int_type:
            output_code += MIPS.div_int
        elif var1.var_type.name == DecafTypes.double_type:
            output_code += MIPSDouble.div
        GlobalVariables.STACK.append(Variable(var_type=var1.var_type))
        return output_code

    def prepare_calculations(self, tree):
        var1_expr = tree.children[0]
        var2_expr = tree.children[1]
        expr1_code = self.visit(var1_expr)
        expr2_code = self.visit(var2_expr)
        var1 = GlobalVariables.STACK.pop()
        var2 = GlobalVariables.STACK.pop()
        output_code = expr1_code
        output_code += expr2_code
        return var1, var2, expr1_code, expr2_code, output_code

    @staticmethod
    def is_var_int_or_double(var: Variable):
        return var.var_type.name in (DecafTypes.double_type, DecafTypes.int_type)

    def mul(self, tree):
        var1, var2, expr1_code, expr2_code, output_code = self.prepare_calculations(tree)
        if CodeGenerator.are_types_invalid(var1, var2) and not CodeGenerator.is_var_int_or_double(var1):
            raise SemanticError()
        if var1.var_type.name == DecafTypes.int_type:
            output_code += MIPS.mul_int
        elif var1.var_type.name == DecafTypes.double_type:
            output_code += MIPSDouble.mul
        GlobalVariables.STACK.append(Variable(var_type=var1.var_type))
        return output_code

    def sub(self, tree):
        var1, var2, expr1_code, expr2_code, output_code = self.prepare_calculations(tree)
        if CodeGenerator.are_types_invalid(var1, var2) and not CodeGenerator.is_var_int_or_double(var1):
            raise SemanticError()
        if var1.var_type.name == DecafTypes.int_type:
            output_code += MIPS.sub_int
        elif var1.var_type.name == DecafTypes.double_type:
            output_code += MIPSDouble.sub
        GlobalVariables.STACK.append(Variable(var_type=var1.var_type))
        return output_code

    def add(self, tree):
        var1, var2, expr1_code, expr2_code, output_code = self.prepare_calculations(tree)
        if CodeGenerator.are_types_invalid(var1, var2):
            raise SemanticError()
        if var1.var_type.name == DecafTypes.int_type:
            output_code += MIPS.add_int
        elif var1.var_type.name == DecafTypes.double_type:
            output_code += MIPSDouble.add
        elif var1.var_type.name == DecafTypes.str_type:
            CodeGenerator.change_var()
            output_code += MIPSStr.concat.format(version=CodeGenerator.VARIABLE_NAME_COUNT)
        GlobalVariables.STACK.append(Variable(var_type=var1.var_type))
        return output_code

    def read_line(self, tree):
        CodeGenerator.change_var()
        output_code = MIPSStr.read_line.format(version=CodeGenerator.VARIABLE_NAME_COUNT)
        GlobalVariables.STACK.append(
            Variable(
                var_type=tree.symbol_table.get_type(DecafTypes.str_type)
            )
        )
        return output_code

    def read_int(self, tree):
        output_code = MIPS.read
        var_type = tree.symbol_table.get_type(DecafTypes.int_type)
        GlobalVariables.STACK.append(Variable(var_type=var_type))
        return output_code

    def constant(self, tree):
        const_token_type = tree.children[0].type
        output_code = ''
        var_type = None
        if const_token_type == Constants.bool_const:
            value = int(tree.children[0].value)
            var_type = tree.symbol_table.get_type(DecafTypes.bool_type)
            output_code += MIPS.bool_const.format(value=value)
        elif const_token_type == Constants.int_const:
            value = int(tree.children[0].value)
            var_type = tree.symbol_table.get_type(DecafTypes.int_type)
            output_code += MIPS.int_const.format(value=value)
        elif const_token_type == Constants.double_const:
            pass
        elif const_token_type == Constants.str_const:
            pass
        elif const_token_type == Constants.null_const:
            var_type = tree.symbol_table.get_type(DecafTypes.null_type)
            output_code += MIPS.null_const
        GlobalVariables.STACK.append(Variable(var_type=var_type))
        return output_code

    # logical functions or, and, equal, not_equal, less than, equal_or_less_than, greater_than, equal_or_greater_than,
    def logical_or(self, tree):
        var1, var2, expr1_code, expr2_code, output_code = self.prepare_calculations(tree)

        if CodeGenerator.are_boolean(var1, var2):
            raise SemanticError()

        output_code += MIPS.logical_or

        GlobalVariables.STACK.append(Variable(var_type=var1.var_type))
        return output_code

    def logical_and(self, tree):
        var1, var2, expr1_code, expr2_code, output_code = self.prepare_calculations(tree)

        if CodeGenerator.are_boolean(var1, var2):
            raise SemanticError()

        output_code += MIPS.logical_and

        GlobalVariables.STACK.append(Variable(var_type=var1.var_type))
        return output_code

    def logical_equal(self, tree):
        var1, var2, expr1_code, expr2_code, output_code = self.prepare_calculations(tree)

        # if CodeGenerator.are_types_invalid(var1, var2):
        #     raise SemanticError()

        if var1.var_type == DecafTypes.double_type:
            CodeGenerator.change_var()
            output_code += MIPS.set_multiple_var(
                MIPS.logical_double_equal,
                str(CodeGenerator.VARIABLE_NAME_COUNT),
                2
            )

        elif var1.var_type == DecafTypes.str_type:
            CodeGenerator.change_var()
            output_code += MIPS.set_multiple_var(
                MIPS.logical_string_equal,
                str(CodeGenerator.VARIABLE_NAME_COUNT),
                10
            )

        unknown_equal = bool((not (var1.type_.name == 'null' and var2.type_.name == 'null')) and \
                             (var1.type_.name == var2.type_.name or \
                              (var1.type_.name == 'null' and var2.type_.name not in ['double', 'int', 'bool', 'string',
                                                                                     'array']) or \
                              (var2.type_.name == 'null' and var1.type_.name not in ['double', 'int', 'bool', 'string',
                                                                                     'array'])))

        if unknown_equal:
            output_code += MIPS.logical_unknown_equal

        else:
            raise SemanticError()

        GlobalVariables.STACK.append(Variable(var_type=var1.var_type))
        return output_code

    def logical_not_equal(self, tree):
        var1, var2, expr1_code, expr2_code, output_code = self.prepare_calculations(tree)

        if var1.var_type == DecafTypes.double_type:
            CodeGenerator.change_var()
            output_code += MIPS.set_multiple_var(
                MIPS.logical_double_not_equal,
                str(CodeGenerator.VARIABLE_NAME_COUNT),
                2
            )

        elif var1.var_type == DecafTypes.str_type:
            CodeGenerator.change_var()
            output_code += MIPS.set_multiple_var(
                MIPS.logical_sring_not_equal,
                str(CodeGenerator.VARIABLE_NAME_COUNT),
                10
            )

        unknown_equal = bool((not (var1.type_.name == 'null' and var2.type_.name == 'null')) and \
                             (var1.type_.name == var2.type_.name or \
                              (var1.type_.name == 'null' and var2.type_.name not in ['double', 'int', 'bool', 'string',
                                                                                     'array']) or \
                              (var2.type_.name == 'null' and var1.type_.name not in ['double', 'int', 'bool', 'string',
                                                                                     'array'])))

        if unknown_equal:
            output_code += MIPS.logical_unknown_not_equal

        else:
            raise SemanticError()

        GlobalVariables.STACK.append(Variable(var_type=var1.var_type))
        return output_code

    def logical_less_than(self, tree):
        var1, var2, expr1_code, expr2_code, output_code = self.prepare_calculations(tree)

        if CodeGenerator.are_types_invalid(var1, var2):
            raise SemanticError()

        if var1.var_type.name == DecafTypes.int_type:
            output_code += MIPS.logical_less_than_int

        elif var1.var_type.name == DecafTypes.double_type:
            CodeGenerator.change_var()
            output_code += MIPS.set_multiple_var(
                MIPS.logical_less_than_double,
                str(CodeGenerator.VARIABLE_NAME_COUNT),
                2
            )

        else:
            raise SemanticError()

        GlobalVariables.STACK.append(Variable(var_type=var1.var_type))
        return output_code

    def logical_less_than_or_equal(self, tree):
        var1, var2, expr1_code, expr2_code, output_code = self.prepare_calculations(tree)

        if CodeGenerator.are_types_invalid(var1, var2):
            raise SemanticError()

        if var1.var_type.name == DecafTypes.int_type:
            output_code += MIPS.logical_less_than_or_equal_int

        elif var1.var_type.name == DecafTypes.double_type:
            CodeGenerator.change_var()
            output_code += MIPS.set_multiple_var(
                MIPS.logical_less_than_or_equal_double,
                str(CodeGenerator.VARIABLE_NAME_COUNT),
                2
            )

        else:
            raise SemanticError()

        GlobalVariables.STACK.append(Variable(var_type=var1.var_type))
        return output_code

    def logical_greater_than(self, tree):
        var1, var2, expr1_code, expr2_code, output_code = self.prepare_calculations(tree)

        if CodeGenerator.are_types_invalid(var1, var2):
            raise SemanticError()

        if var1.var_type.name == DecafTypes.int_type:
            output_code += MIPS.logical_greater_than_int

        elif var1.var_type.name == DecafTypes.double_type:
            CodeGenerator.change_var()
            output_code += MIPS.set_multiple_var(
                MIPS.logical_greater_than_double,
                str(CodeGenerator.VARIABLE_NAME_COUNT),
                2
            )

        else:
            raise SemanticError()

        GlobalVariables.STACK.append(Variable(var_type=var1.var_type))
        return output_code

    def logical_greater_than_or_equal(self, tree):
        var1, var2, expr1_code, expr2_code, output_code = self.prepare_calculations(tree)

        if CodeGenerator.are_types_invalid(var1, var2):
            raise SemanticError()

        if var1.var_type.name == DecafTypes.int_type:
            output_code += MIPS.logical_greater_than_or_equal_int

        elif var1.var_type.name == DecafTypes.double_type:
            CodeGenerator.change_var()
            output_code += MIPS.set_multiple_var(
                MIPS.logical_greater_than_or_equal_double,
                str(CodeGenerator.VARIABLE_NAME_COUNT),
                2
            )

        else:
            raise SemanticError()

        GlobalVariables.STACK.append(Variable(var_type=var1.var_type))
        return output_code

    def declare_function(self, tree):
        _, var_1, var_2, var_3 = tree.children[:4]
        # new_type = self.visit(var_0) if isinstance(var_0, Tree) else Type('void')
        function_name = var_1.value
        function = tree.symbol_table.get_function(function_name, tree=tree)
        self.visit(var_2)

        formal = ''
        for index, val in enumerate(function.formals[::-1]):
            formal += MIPS.function_formal.format(4 * (index + 1), val.address)

        GlobalVariables.FUNCTION_STACK.append(function)

        stmt_block = self.visit(var_3)

        GlobalVariables.FUNCTION_STACK.pop()

        return MIPS.function.format(
            function.label,
            formal,
            stmt_block,
            function.label
        )

    def return_stmt(self, tree):
        if len(GlobalVariables.FUNCTION_STACK) == 0:
            raise SemanticError()

        function = GlobalVariables.FUNCTION_STACK[-1]

        code = MIPS.return_stmt

        variable = tree.symbol_table.get_type('void')

        if len(tree.children) > 1:
            code += self.visit(tree.children[1])
            variable = GlobalVariables.STACK.pop()

            # store value
            code += MIPS.return_main.replace("\t\t\t", "\t")

        if variable.var_type.name != function.return_type.name:
            raise SemanticError()

        # jump to continue
        code += f"""
    	j {function.label}_end
    	""".replace("\t\t", "")

        return code

    def field(self, tree):
        access_modifier = self.visit(tree.children[0])

        return self.visit(tree.children[1])

    def access_modifier(self, tree):
        if tree.children:
            return tree.children[0].value
        return ''

    def new_identifier(self, tree):
        ident_name = tree.children[1].value
        type_ = tree.symbol_table.get_type(ident_name)

        class_ = type_.class_ref
        if not class_:
            raise SemanticError()

        object_size = class_.get_object_size() + 1

        code = MIPS.new_identifier.Format(object_size * 4, class_.address).replace("\t\t", "\t")

        GlobalVariables.STACK.append(Variable(var_type=type_))
        return code

    def variable(self, tree):
        output_code = ''
        type_ = self.visit(tree.children[0])
        var_name = tree.children[1].value
        variable = tree.symbol_table.find_var(var_name, tree=tree)
        output_code += MIPS.variable_init.Format(variable.address).replace("\t\t", "\t")
        return output_code


def prepare_main_tree(tree):
    SymbolTableParentUpdater().visit_topdown(tree)
    tree.symbol_table = SymbolTable()
    tree.symbol_table.add_type(Type('int', 4))
    tree.symbol_table.add_type(Type('double', 8))
    tree.symbol_table.add_type(Type('bool', 4))
    tree.symbol_table.add_type(Type('void', 0))
    tree.symbol_table.add_type(Type('string', 8))
    tree.symbol_table.add_type(Type('array', 4))
    SymbolTableUpdater().visit_topdown(tree)


def generate(input_code):
    parser = Lark.open('./grammar.lark', parser="lalr", propagate_positions=True)
    try:
        tree = parser.parse(input_code)
        prepare_main_tree(tree)
        mips_code = CodeGenerator().visit(tree)
    except ParseError as e:
        return e
    except SemanticError:
        mips_code = MIPS.semantic_error
    return mips_code


if __name__ == "__main__":
    inputfile = 'example.d'
    with open(inputfile, "r") as input_file:
        code = input_file.read()
    code = generate(code)
    print("#### code ")
    print(code)

    output_file = open("../tmp/res.mips", "w")
    output_file.write(code)
