from operator import le
from typing import List

from lark import Lark, ParseError, Tree
from lark.visitors import Interpreter

from decaf_enums import Constants, DecafTypes, LoopLabels
from globals import GlobalVariables
from mips_codes import MIPS, MIPSArray, MIPSDouble, MIPSStr, MIPSConditionalStmt, MIPSPrintStmt, MIPSSpecials
from semantic_error import SemanticError
from symbol_table import Variable, SymbolTable, Type
from symbol_table_updaters import SymbolTableUpdater, SymbolTableParentUpdater, TypeVisitor


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

    @staticmethod
    def decrease_stack_ptr_pos(stack_ptr: int) -> int:
        return stack_ptr - 4

    def conditional_do_statement(self, tree, con_stmt, bre_stmt, stmt_children_number):
        CodeGenerator.add_continue_and_break_target_labels(
            continue_label=con_stmt,
            break_label=bre_stmt
        )
        statement_code = self.visit(tree.children[stmt_children_number])
        CodeGenerator.pop_continue_and_break_target_labels()
        return statement_code

    def convert_int_shared(self, tree, target_type, convert_code):
        expression_code = self.visit(tree.children[1])
        expr_var = GlobalVariables.STACK.pop()
        if expr_var.var_type.name != DecafTypes.int_type:
            raise SemanticError(6)
        output_code = expression_code
        output_code += convert_code
        GlobalVariables.STACK.append(
            Variable(
                var_type=tree.symbol_table.get_type(target_type)
            )
        )
        return output_code

    def int_to_bool(self, tree):
        return self.convert_int_shared(
            tree=tree,
            target_type=DecafTypes.bool_type,
            convert_code=MIPS.convert_int_to_bool
        )

    def int_to_double(self, tree):
        return self.convert_int_shared(
            tree=tree,
            target_type=DecafTypes.double_type,
            convert_code=MIPS.convert_int_to_double
        )

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
            raise SemanticError(5)
        target_label = GlobalVariables.CONTINUE_LOOP_STACK[-1]
        output_code = MIPSConditionalStmt.continue_stmt.format(
            target_label=target_label
        )
        return output_code

    def break_stmt(self, tree):
        if not len(GlobalVariables.BREAK_LOOP_STACK):
            raise SemanticError(3)
        target_label = GlobalVariables.BREAK_LOOP_STACK[-1]
        output_code = MIPSConditionalStmt.break_stmt.format(
            target_label=target_label
        )
        return output_code

    def for_shared_part(self, tree, expr_1, expr_2, expr_3, statement_num):
        expression_code_1 = expr_1
        expression_code_2 = expr_2
        expression_code_3 = expr_3
        version = CodeGenerator.get_version()
        statement_code = self.conditional_do_statement(
            tree=tree,
            con_stmt=LoopLabels.for_continue_label.format(version=version),
            bre_stmt=LoopLabels.for_break_label.format(version=version),
            stmt_children_number=statement_num
        )
        if not statement_code:
            statement_code = ''
        output_code = MIPSConditionalStmt.for_stmt.format(
            version=version,
            expression_code_1=expression_code_1,
            expression_code_2=expression_code_2,
            expression_code_3=expression_code_3,
            statement_code=statement_code
        )
        return output_code

    def for_1(self, tree):
        return self.for_shared_part(
            tree,
            expr_1='',
            expr_2=self.visit(tree.children[3]),
            expr_3='',
            statement_num=6
        )

    def for_2(self, tree):
        return self.for_shared_part(
            tree,
            expr_1=self.visit(tree.children[2]),
            expr_2=self.visit(tree.children[4]),
            expr_3='',
            statement_num=7
        )

    def for_3(self, tree):
        return self.for_shared_part(
            tree,
            expr_1='',
            expr_2=self.visit(tree.children[3]),
            expr_3=self.visit(tree.children[5]),
            statement_num=7
        )

    def for_4(self, tree):
        return self.for_shared_part(
            tree,
            expr_1=self.visit(tree.children[2]),
            expr_2=self.visit(tree.children[4]),
            expr_3=self.visit(tree.children[6]),
            statement_num=8
        )

    def if_stmt(self, tree):
        expression_code = self.visit(tree.children[1])
        GlobalVariables.STACK.pop()
        else_statement_code = ''
        statement_code = self.visit(tree.children[2])
        if len(tree.children) > 3:
            else_statement_code = self.visit(tree.children[4])
            if not else_statement_code:
                else_statement_code = ''
        if not statement_code:
            statement_code = ''
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

        for item in [*variables, *functions, *classes]:
            result += self.visit(item)

        result += MIPS.main.format(GlobalVariables.CLASS_INIT, GlobalVariables.VAR_INIT)
        result += MIPS.side_functions
        segment_code = MIPS.data_segment
        for index, item in enumerate(GlobalVariables.CONSTANTS):
            segment_code += MIPS.constant_str.format(index, item)
        segment_code += '\n'
        for index, item in GlobalVariables.ARRAYS:
            segment_code += MIPS.array_base.format(index, item)
        segment_code += '\n'
        result = segment_code + result
        return result

    @staticmethod
    def are_types_invalid(var1: Variable, var2: Variable):
        if var1.var_type.arr_type:
            return not var1.var_type.is_same(var2.var_type)
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
            raise SemanticError(29)
        GlobalVariables.STACK.append(var)
        return output_code

    def module(self, tree):
        var1, var2, expr1, expr2, output_code = self.prepare_calculations(tree)
        exclusive_var1 = var1 if var1.var_type.arr_type else var2
        exclusive_var2 = var2 if var1.var_type.arr_type else var1
        if not exclusive_var1.var_type.is_same(exclusive_var2.var_type):
            raise SemanticError(23)
        output_code += MIPS.module_int
        var_type = tree.symbol_table.get_type('int')
        GlobalVariables.STACK.append(Variable(var_type=var_type))
        return output_code

    def class_declaration(self, tree):
        class_name = tree.children[1].value

        class_ = tree.symbol_table.get_type(class_name).class_ref

        GlobalVariables.STACK_CLASS.append(class_)

        code = ''

        functions_trees = []
        variables_trees = []

        for subtree in tree.children:
            if isinstance(subtree, Tree) and subtree.data == Constants.field:
                if subtree.children[1].data == Constants.function_decl:
                    functions_trees.append(subtree)
                else:
                    variables_trees.append(subtree)

        for subtree in variables_trees:
            code += self.visit(subtree)

        for subtree in functions_trees:
            code += self.visit(subtree)

        vtable_size = class_.get_vtable_size()

        class_init_codes = ''
        class_init_codes += MIPS.class_init.format(class_.name, vtable_size * 4, class_.address).replace("\t\t", "\t")

        current_class = class_
        parent_classes = []
        while current_class:
            parent_classes.append(current_class)
            current_class = current_class.parent

        all_functions = []
        for current_class in parent_classes[::-1]:
            for class_function in current_class.member_functions.values():
                for func in all_functions:
                    if func.name == class_function.name:
                        for i in range(len(func.formals) - 1):
                            if func.formals[i + 1].type_.name != class_function.formals[i + 1].type_.name:
                                raise SemanticError()
                            elif func.formals[i + 1].type_.arr_type.are_equal(func.formals[i + 1].type_.arr_type):
                                raise SemanticError()
                        if func.return_type.name != class_function.return_type.name:
                            raise SemanticError()
                all_functions.append(class_function)
                func_label = class_function.label
                _, index = current_class.get_func_and_index(class_function.name)

                class_init_codes += MIPS.store_class_functions.format(func_label, index * 4).replace("\t\t", "")

        all_values = []
        for current_class in parent_classes[::-1]:
            for value in current_class.member_data.values():
                for val in all_values:
                    if val.name == value.name:
                        raise SemanticError()
                all_values.append(value)

        GlobalVariables.STACK_CLASS.pop()

        return code

    def assign(self, tree):
        GlobalVariables.ASSIGN_FLAG = True
        l_var, r_var, expr1_code, expr2_code, output_code = self.prepare_calculations(tree)
        if CodeGenerator.are_types_invalid(l_var, r_var):
            raise SemanticError(2)
        output_code += MIPS.assignment_int
        GlobalVariables.STACK.append(l_var)
        return output_code

    def div(self, tree):
        var1, var2, expr1_code, expr2_code, output_code = self.prepare_calculations(tree)
        if CodeGenerator.are_types_invalid(var1, var2) and not CodeGenerator.is_var_int_or_double(var1):
            raise SemanticError(7)
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
        var1 = GlobalVariables.STACK.pop()
        expr2_code = self.visit(var2_expr)
        var2 = GlobalVariables.STACK.pop()
        if isinstance(expr1_code, list):
            expr1_code = expr1_code[0]
        if isinstance(expr2_code, list):
            expr2_code = expr2_code[0]
        output_code = expr1_code
        output_code += expr2_code
        return var1, var2, expr1_code, expr2_code, output_code

    @staticmethod
    def is_var_int_or_double(var: Variable):
        return var.var_type.name in (DecafTypes.double_type, DecafTypes.int_type)

    def mul(self, tree):
        var1, var2, expr1_code, expr2_code, output_code = self.prepare_calculations(tree)
        if CodeGenerator.are_types_invalid(var1, var2) and not CodeGenerator.is_var_int_or_double(var1):
            raise SemanticError(24)
        if var1.var_type.name == DecafTypes.int_type:
            output_code += MIPS.mul_int
        elif var1.var_type.name == DecafTypes.double_type:
            output_code += MIPSDouble.mul
        GlobalVariables.STACK.append(Variable(var_type=var1.var_type))
        return output_code

    def sub(self, tree):
        var1, var2, expr1_code, expr2_code, output_code = self.prepare_calculations(tree)
        if CodeGenerator.are_types_invalid(var1, var2) and not CodeGenerator.is_var_int_or_double(var1):
            raise SemanticError(28)
        if var1.var_type.name == DecafTypes.int_type:
            output_code += MIPS.sub_int
        elif var1.var_type.name == DecafTypes.double_type:
            output_code += MIPSDouble.sub
        GlobalVariables.STACK.append(Variable(var_type=var1.var_type))
        return output_code

    def add(self, tree):
        var1, var2, expr1_code, expr2_code, output_code = self.prepare_calculations(tree)
        if CodeGenerator.are_types_invalid(var1, var2):
            raise SemanticError(1)
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
            value = 1
            if tree.children[0].value == 'false':
                value = 0
            var_type = tree.symbol_table.get_type(DecafTypes.bool_type)
            output_code += MIPS.bool_const.format(value=value)
        elif const_token_type == Constants.int_const:
            value = int(tree.children[0].value)
            var_type = tree.symbol_table.get_type(DecafTypes.int_type)
            output_code += MIPS.int_const.format(value=value)
        elif const_token_type == Constants.double_const:
            value = tree.children[0].value.lower()
            var_type = tree.symbol_table.get_type(DecafTypes.double_type)
            if value[-1] == '.':
                value += '0'
            if value[0] == '.':
                value = '0' + value
            if '.e' in value:
                value.replace('.e', '.0e')
            output_code = MIPS.double_const.format(value=value)

        elif const_token_type == Constants.str_const:
            value = tree.children[0].value[1:-1]
            var_type = tree.symbol_table.get_type(DecafTypes.str_type)
            val_size = len(value) + 1
            label = CodeGenerator.get_version()

            const_label = len(GlobalVariables.CONSTANTS)
            GlobalVariables.CONSTANTS.append(value)

            output_code = MIPS.str_const.format(
                val_size,
                const_label,
                label,
                label,
                label,
                label,
            )


        elif const_token_type == Constants.null_const:
            var_type = tree.symbol_table.get_type(DecafTypes.null_type)
            output_code += MIPS.null_const
        GlobalVariables.STACK.append(Variable(var_type=var_type))
        return output_code

    # class not implemented
    def l_value_ident(self, tree):
        var = tree.symbol_table.find_var(tree.children[0].value, tree=tree, error=True)
        GlobalVariables.STACK.append(var)
        output = MIPS.set_multiple_var(MIPS.l_value_assign_true, var.address,
                                       2) if GlobalVariables.ASSIGN_FLAG else MIPS.l_value_assign_false.format(
            var.address)

        GlobalVariables.ASSIGN_FLAG = False

        return output

    def logical_or(self, tree):
        var1, var2, expr1_code, expr2_code, output_code = self.prepare_calculations(tree)

        if CodeGenerator.are_boolean(var1, var2):
            raise SemanticError(22)

        output_code += MIPS.logical_or

        GlobalVariables.STACK.append(Variable(var_type=tree.symbol_table.get_type(DecafTypes.bool_type)))
        return output_code

    def logical_and(self, tree):
        var1, var2, expr1_code, expr2_code, output_code = self.prepare_calculations(tree)

        if CodeGenerator.are_boolean(var1, var2):
            raise SemanticError(10)

        output_code += MIPS.logical_and

        GlobalVariables.STACK.append(Variable(var_type=tree.symbol_table.get_type(DecafTypes.bool_type)))
        return output_code

    def logical_not(self, tree):
        expr1_code = self.visit(tree.children[0])

        out_put = expr1_code

        var = GlobalVariables.STACK.pop()

        if var.var_type.name != DecafTypes.bool_type:
            raise SemanticError(20)

        out_put += MIPS.logical_not

        GlobalVariables.STACK.append(Variable(var_type=tree.symbol_table.get_type(DecafTypes.bool_type)))
        return out_put

    def logical_equal(self, tree):
        var1, var2, expr1_code, expr2_code, output_code = self.prepare_calculations(tree)

        unknown_equal = bool((not (var1.var_type.name == 'null' and var2.var_type.name == 'null')) and \
                             (var1.var_type.name == var2.var_type.name or \
                              (var1.var_type.name == 'null' and var2.var_type.name not in ['double', 'int', 'bool',
                                                                                           'string',
                                                                                           'array']) or \
                              (var2.var_type.name == 'null' and var1.var_type.name not in ['double', 'int', 'bool',
                                                                                           'string',
                                                                                           'array'])))

        if var1.var_type.name == DecafTypes.double_type:
            version = CodeGenerator.get_version()
            output_code += MIPS.logical_double_equal.format(
                version=version
            )
        elif var1.var_type.name == DecafTypes.str_type:
            CodeGenerator.change_var()
            output_code += MIPS.set_multiple_var(
                MIPS.logical_string_equal,
                str(CodeGenerator.VARIABLE_NAME_COUNT),
                10
            )
        elif unknown_equal:
            output_code += MIPS.logical_unknown_equal
        else:
            raise SemanticError(11)

        GlobalVariables.STACK.append(Variable(var_type=tree.symbol_table.get_type(DecafTypes.bool_type)))
        return output_code

    def logical_not_equal(self, tree):
        var1, var2, expr1_code, expr2_code, output_code = self.prepare_calculations(tree)

        unknown_equal = bool(
            (not (var1.var_type.name == 'null' and var2.var_type.name == 'null')) and \
            (var1.var_type.name == var2.var_type.name or \
             (var1.var_type.name == 'null' and var2.var_type.name not in ['double', 'int', 'bool',
                                                                          'string',
                                                                          'array']) or \
             (var2.var_type.name == 'null' and var1.var_type.name not in ['double', 'int', 'bool',
                                                                          'string',
                                                                          'array'])))

        if var1.var_type.name == DecafTypes.double_type:
            CodeGenerator.change_var()
            output_code += MIPS.set_multiple_var(
                MIPS.logical_double_not_equal,
                str(CodeGenerator.VARIABLE_NAME_COUNT),
                2
            )

        elif var1.var_type.name == DecafTypes.str_type:
            CodeGenerator.change_var()
            output_code += MIPS.set_multiple_var(
                MIPS.logical_sring_not_equal,
                str(CodeGenerator.VARIABLE_NAME_COUNT),
                10
            )

        elif unknown_equal:
            output_code += MIPS.logical_unknown_not_equal

        else:
            raise SemanticError(21)

        GlobalVariables.STACK.append(Variable(var_type=tree.symbol_table.get_type(DecafTypes.bool_type)))
        return output_code

    def logical_less_than(self, tree):
        var1, var2, expr1_code, expr2_code, output_code = self.prepare_calculations(tree)

        if CodeGenerator.are_types_invalid(var1, var2):
            raise SemanticError(16)

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
            raise SemanticError(17)

        GlobalVariables.STACK.append(Variable(var_type=tree.symbol_table.get_type(DecafTypes.bool_type)))
        return output_code

    def logical_less_than_or_equal(self, tree):
        var1, var2, expr1_code, expr2_code, output_code = self.prepare_calculations(tree)

        if CodeGenerator.are_types_invalid(var1, var2):
            raise SemanticError(18)

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
            raise SemanticError(19)

        GlobalVariables.STACK.append(Variable(var_type=tree.symbol_table.get_type(DecafTypes.bool_type)))
        return output_code

    def logical_greater_than(self, tree):
        var1, var2, expr1_code, expr2_code, output_code = self.prepare_calculations(tree)

        if CodeGenerator.are_types_invalid(var1, var2):
            raise SemanticError(12)

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
            raise SemanticError(13)

        GlobalVariables.STACK.append(Variable(var_type=tree.symbol_table.get_type(DecafTypes.bool_type)))
        return output_code

    def logical_greater_than_or_equal(self, tree):
        var1, var2, expr1_code, expr2_code, output_code = self.prepare_calculations(tree)

        if CodeGenerator.are_types_invalid(var1, var2):
            raise SemanticError(14)

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
            raise SemanticError(15)

        GlobalVariables.STACK.append(Variable(var_type=tree.symbol_table.get_type(DecafTypes.bool_type)))
        return output_code

    def call(self, tree):
        function = tree.symbol_table.get_function(
            tree.children[0].value
        )
        stack_size = len(GlobalVariables.STACK)
        actuals = self.visit(tree.children[1])
        args_num = len(GlobalVariables.STACK) - stack_size
        if args_num != len(function.formals):
            raise SemanticError(101)
        formals_idx = args_num - 1
        while len(GlobalVariables.STACK) > stack_size:
            formal = function.formals[formals_idx]
            arg = GlobalVariables.STACK.pop()
            if arg.var_type.name != formal.var_type.name:
                raise SemanticError(102)
            formals_idx -= 1
        function_label = function.name
        if function_label == 'main':
            function_label = 'func_main'
        output_code = MIPSSpecials.method_call.format(
            actuals=actuals,
            func_name=function_label,
            args_size=args_num * 4
        )
        if function.return_type:
            output_code += MIPSSpecials.method_call_return
        GlobalVariables.STACK.append(Variable(var_type=function.return_type))
        return output_code

    def type(self, tree):
        return tree.symbol_table.get_type(tree.children[0].value)

    def function_decl(self, tree):
        _, var_1, var_2, var_3 = tree.children[:4]
        function_name = var_1.value
        function = tree.symbol_table.get_function(function_name, tree=tree)
        self.visit(var_2)

        formal = ''
        for index, val in enumerate(function.formals[::-1]):
            formal += MIPS.function_formal.format(4 * (index + 1), val.address)

        GlobalVariables.FUNCTION_STACK.append(function)

        stmt_block = self.visit(var_3)

        GlobalVariables.FUNCTION_STACK.pop()
        func_label = function.name
        if func_label == 'main':
            func_label = 'func_main'
        return MIPS.function.format(
            func_label,
            formal,
            stmt_block,
            func_label
        )

    def actuals(self, tree):
        return '\n'.join(self.visit_children(tree))

    def print_stmt(self, tree):

        pre_stack_len = len(GlobalVariables.STACK)

        output = self.visit(tree.children[1])

        if len(GlobalVariables.STACK) == pre_stack_len:
            return output

        stack_ptr_pos = 4 * (len(GlobalVariables.STACK) - (1 + pre_stack_len))

        for item in GlobalVariables.STACK[pre_stack_len:]:
            var_type_name = item.var_type.name
            if var_type_name == DecafTypes.int_type:
                output += MIPSPrintStmt.int_stmt.format(stack_ptr_pos)
            elif var_type_name == DecafTypes.double_type:
                output += MIPSPrintStmt.double_stmt.format(stack_ptr_pos)
            elif var_type_name == DecafTypes.bool_type:
                output += MIPSPrintStmt.bool_stmt.format(stack_ptr_pos)
            elif var_type_name == DecafTypes.str_type:
                output += MIPSPrintStmt.string_stmt.format(stack_ptr_pos)
            stack_ptr_pos = CodeGenerator.decrease_stack_ptr_pos(stack_ptr_pos)
            GlobalVariables.STACK.pop()

        output += MIPSPrintStmt.new_line_stmt.format(stack_ptr_pos)
        return output

    def return_stmt(self, tree):
        if not len(GlobalVariables.FUNCTION_STACK):
            raise SemanticError(26)
        function = GlobalVariables.FUNCTION_STACK[-1]
        variable = tree.symbol_table.get_type(DecafTypes.void_type)
        output_code = ''
        if len(tree.children) > 1:
            output_code += self.visit(tree.children[1])
            variable = GlobalVariables.STACK.pop()
            output_code += MIPS.return_calc_expr
        if variable.var_type.name != function.return_type.name:
            raise SemanticError(27)
        function_label = function.name
        if function_label == 'main':
            function_label = 'func_main'
        output_code += MIPS.return_back_to_caller.format(
            function_name=function_label
        )
        return output_code

    def field(self, tree):
        access_modifier = self.visit(tree.children[0])
        # TODO @Arab: why do not use access modifier
        return self.visit(tree.children[1])

    def access_modifier(self, tree):
        if tree.children:
            return tree.children[0].value
        return ''

    def new_identifier(self, tree):
        ident_name = tree.children[1].value
        var_type = tree.symbol_table.get_type(ident_name)

        class_ = var_type.class_ref
        if not class_:
            raise SemanticError(25)

        object_size = class_.get_object_size() + 1

        code = MIPS.new_identifier.Format(object_size * 4, class_.address).replace("\t\t", "\t")

        GlobalVariables.STACK.append(Variable(var_type=var_type))
        return code

    def variable(self, tree):
        output_code = ''
        var_type = self.visit(tree.children[0])
        var_name = tree.children[1].value
        variable = tree.symbol_table.find_var(var_name, tree=tree)
        output_code += MIPS.variable_init.format(variable.address)
        GlobalVariables.VAR_INIT += output_code
        return ''

    def bool_to_int(self, tree):
        main_code = self.visit(tree.children[1])
        source_var = GlobalVariables.STACK.pop()

        if source_var.var_type.name != DecafTypes.bool_type:
            raise SemanticError(4)

        GlobalVariables.STACK.append(Variable(var_type=tree.symbol_table.get_type(DecafTypes.int_type)))

        return main_code

    def new_array(self, tree):
        expression = self.visit(tree.children[0])
        GlobalVariables.STACK.pop()
        arr_type = self.visit(tree.children[1])
        var_type = Type(DecafTypes.array_type, arr_type=arr_type)
        output_code = MIPSArray.new_array.format(
            expression=expression
        )
        GlobalVariables.STACK.append(
            Variable(
                var_type=var_type
            )
        )
        return output_code

    def l_value_array(self, tree):

        store_addr_code = ''
        if GlobalVariables.ASSIGN_FLAG:
            store_addr_code = """
    		sw $t2, -4($sp)
    		addi $sp, $sp, -4
    		"""

        GlobalVariables.ASSIGN_FLAG = False

        code = ""
        code += self.visit(tree.children[0])
        l_side_variable = GlobalVariables.STACK.pop()

        code += self.visit(tree.children[1])
        index_var = GlobalVariables.STACK.pop()

        if index_var.type_.name != 'int':
            raise SemanticError(111)

        if l_side_variable.type_.name != 'array':
            raise SemanticError(110)

        code += f""" 
    			lw $t1, 0($sp) #index
    			addi $sp, $sp, 4

    			#lw $t2, {l_side_variable.address}($gp)
    			lw $t2, 0($sp) #array addr
    			addi $sp, $sp, 4
    			lw $t3, 0($t2) 	#array size

    			addi $t1, $t1, 1 # add one to index ('cause of size)

    			ble $t1, $zero, runtimeError
    			bgt $t1, $t3, runtimeError


    			mul $t1, $t1, 4 # index offset in bytes

    			add $t2, $t2, $t1	#t2: address khooneye arraye ke mikhaim

    			{store_addr_code}

    			lw $t0, 0($t2)		#t0: value khooneye arraye ke mikhaim
    			sw $t0, -4($sp)
    			addi $sp, $sp, -4


    			""".replace("\t\t\t", "")

        new_var = Variable(
            var_type=l_side_variable.type_.arr_type
        )
        GlobalVariables.STACK.append(new_var)

        return code

    def double_to_int(self, tree):
        main_code = self.visit(tree.children[1])
        source_var = GlobalVariables.STACK.pop()

        if source_var.var_type.name != DecafTypes.double_type:
            raise SemanticError(9)

        CodeGenerator.VARIABLE_NAME_COUNT += 1

        label = CodeGenerator.VARIABLE_NAME_COUNT

        main_code += MIPS.convert_double_to_int.format(label, label, label, label, label, label).replace("\t\t\t", "")

        GlobalVariables.STACK.append(Variable(var_type=tree.symbol_table.get_type(DecafTypes.int_type)))

        return main_code

    def array_type(self, tree):
        array_type = self.visit(tree.children[0])

        return Type(name=DecafTypes.double_type, arr_type=array_type)

    def initialize_array(self, tree):
        main_code = self.visit(tree.children[0])
        array_size = GlobalVariables.STACK.pop()

        array_type = self.visit(tree.children[1])

        CodeGenerator.VARIABLE_NAME_COUNT += 1

        main_code += MIPS.array_init.format(main_code).replace("\t\t\t", "")

        GlobalVariables.STACK.append(Variable(var_type=array_type))
        return main_code


def prepare_main_tree(tree):
    SymbolTableParentUpdater().visit_topdown(tree)
    tree.symbol_table = SymbolTable()
    tree.symbol_table.add_type(Type(DecafTypes.int_type, 4))
    tree.symbol_table.add_type(Type(DecafTypes.double_type, 4))
    tree.symbol_table.add_type(Type(DecafTypes.bool_type, 4))
    tree.symbol_table.add_type(Type(DecafTypes.void_type, 0))
    tree.symbol_table.add_type(Type(DecafTypes.str_type, 4))
    tree.symbol_table.add_type(Type(DecafTypes.array_type, 4))
    SymbolTableUpdater().visit(tree)
    TypeVisitor().visit(tree)


def generate(input_code):
    parser = Lark.open('./grammar.lark', parser="lalr", propagate_positions=True)
    try:
        tree = parser.parse(input_code)
        prepare_main_tree(tree)
        mips_code = CodeGenerator().visit(tree)
    except ParseError as e:
        return e
    except SemanticError as e:
        mips_code = MIPS.semantic_error
        print(e.token)
    return mips_code


if __name__ == "__main__":
    inputfile = 'example.d'
    with open(inputfile, "r") as input_file:
        code = input_file.read()
    code = generate(code)
    print("#### code ")
    print(code)
