class MIPS:

    @staticmethod
    def set_multiple_var(base_mips: str, value: str, count=1):
        while True:
            try:
                return base_mips.format(*list([value] * count))
            except:
                count += 1
                continue

    convert_int_to_bool = """
        lw $t0, 0($sp)
        sne $t0, $t0, $zero
        sw $t0, 0($sp)
    """

    convert_int_to_double = """
        l.s $f0, 0($sp)
        cvt.s.w $f1, $f0
        s.s $f1, 0($sp)
    """

    convert_double_to_int = """
				li.s $f4, -0.5
				li.s $f6, 0.0
				l.s $f0, 0($sp)
				c.eq.s $f0, $f4
				bc1t dtoi_half_{}
				c.lt.s $f0, $f6
				bc1t dtoi_{}
				li.s $f4, 0.5
			dtoi_{}:
				add.s $f0, $f0, $f4
				cvt.w.s $f2, $f0
				s.s $f2, 0($sp)
				j end_dtoi_{}
			dtoi_half_{}:
				li.s $f2, 0.0
				s.s $f2, 0($sp)
			end_dtoi_{}:
				"""

    bool_const = """
            li $t0, {value}
            addi $sp, $sp, -4
            sw $t0, 0($sp)
            """
    int_const = bool_const

    double_const = """
				li.s $f2, {value}
				addi $sp, $sp, -4
				s.s $f2, 0($sp)
				"""

    str_const = """
				li $v0, 9		
				li $a0, {}
				syscall

				move $s0, $v0		

				addi $sp, $sp, -4
				sw $s0, 0($sp)

				la $s1, constantStr_{}
				li $t1, 0

			constant_str_{}:
				lb $t1, 0($s1)
				sb $t1, 0($s0)
				beq $t1, $zero, constant_str_end_{} 
				addi $s1, $s1, 1
				addi $s0, $s0, 1
				b constant_str_{}

			constant_str_end_{}:

				"""

    null_const = """
			addi $sp, $sp, -4
			sw $zero, 0($sp)
            """
    add_int = """
            lw $t1, 0($sp)
			lw $t2, 4($sp)
			add $t3, $t1, $t2
			sw $t3, 4($sp) 
			addi $sp, $sp, 4
            """
    sub_int = """
            lw $t1, 0($sp)
			lw $t2, 4($sp)
			sub $t3, $t2, $t1
			sw $t3, 4($sp) 
			addi $sp, $sp, 4
            """
    mul_int = """
            lw $t1, 0($sp)
			lw $t2, 4($sp)
			mul $t3, $t1, $t2
			sw $t3, 4($sp) 
			addi $sp, $sp, 4
            """
    div_int = """
            lw $t1, 0($sp)
    		lw $t2, 4($sp)
    		div $t3, $t2, $t1
    		sw $t3, 4($sp) 
    		addi $sp, $sp, 4
            """

    assignment_int = """
                lw $t0, 0($sp)
				addi $sp, $sp, 4
				lw $t1, 4($sp) # load address from stack
				addi $sp, $sp, 8
				sw $t0, 0($t1)
				addi $sp, $sp, -4
				sw $t0, 0($sp) 
            """

    module_int = """
            lw $t0, 0($sp)
			lw $t1, 4($sp)
			div $t1, $t0
			mfhi $t2
			sw $t2, 4($sp) 
			addi $sp, $sp, 4
            """

    unary_neg_int = """
            lw $t0, 0($sp)
            sub $t0, $zero, $t0
            sw $t0, 0($sp)
            """
    read = """
        addi $v0, $zero, 5
        syscall
        addi $sp, $sp, -4
        sw $v0, 0($sp)
    """
    semantic_error = """
    		.text
    		.globl main
    		main:
    		la $a0 , errorMsg
    		addi $v0 , $zero, 4
    		syscall
			jr $ra
    		.data
    		errorMsg: .asciiz "Semantic Error"
    		"""

    logical_or = """
        			lw $t1, 0($sp)
    				lw $t0, 4($sp)
    				or $t2, $t0, $t1
    				sw $t2, 4($sp) 
    				addi $sp, $sp, 4
                    """

    logical_and = """
    				lw $t1, 0($sp)
    				lw $t0, 4($sp)
    				and $t2, $t0, $t1
    				sw $t2, 4($sp) 
    				addi $sp, $sp, 4
                    """

    logical_double_equal = """
        		l.s $f0, 0($sp)
        		l.s $f1, 4($sp)
        		li $t0 , 0
        		c.eq.s $f0, $f1
        		bc1f d_eq_{version}
        		li $t0 , 1
        	d_eq_{version}:
        		sw $t0, 4($sp)
        		addi $sp, $sp, 4
        		"""

    logical_string_equal = """
                        lw $s1, 0($sp)
                        lw $s0, 4($sp)

        				cmploop_{}:
        					lb $t2,0($s0)
        					lb $t3,0($s1)
        					bne $t2,$t3,cmpne_{}

        					beq $t2,$zero,cmpeq_{}
        					beq $t3,$zero,cmpeq_{}

        					addi $s0,$s0,1
        					addi $s1,$s1,1

        					j cmploop_{}

        				cmpne_{}:
        					li $t0,0
        					sw $t0, 4($sp)
        					addi $sp, $sp, 4
        					j end_{}

        				cmpeq_{}:
        					li $t0,1
        					sw $t0, 4($sp)
        					addi $sp, $sp, 4
        					j end_{}

        				end_{}:

        				"""

    logical_unknown_equal = """
        		lw $t1, 0($sp)
        		lw $t0, 4($sp)
        		seq $t2, $t0, $t1
        		sw $t2, 4($sp) 
        		addi $sp, $sp, 4
        		"""

    logical_double_not_equal = """
    					l.s $f2, 0($sp)
    					l.s $f4, 4($sp)
    					li $t0 , 1
    					c.eq.s $f4, $f2
    					bc1f d_neq_{}
    					li $t0 , 0
    				d_neq_{}:
    					sw $t0, 4($sp)
    					addi $sp, $sp, 4
    					"""

    logical_sring_not_equal = """
    					lw $s1, 0($sp)
    					lw $s0, 4($sp)

    				cmploop_{}:
    					lb $t2,0($s0)
    					lb $t3,0($s1)
    					bne $t2,$t3,cmpne_{}

    					beq $t2,$zero,cmpeq_{}
    					beq $t3,$zero,cmpeq_{}

    					addi $s0,$s0,1
    					addi $s1,$s1,1

    					j cmploop_{}

    				cmpne_{}:
    					li $t0,1
    					sw $t0, 4($sp)
    					addi $sp, $sp, 4
    					j end_{}

    				cmpeq_{}:
    					li $t0,0
    					sw $t0, 4($sp)
    					addi $sp, $sp, 4
    					j end_{}

    				end_{}:

    				"""
    logical_unknown_not_equal = """
    					lw $t1, 0($sp)
    					lw $t0, 4($sp)
    					sne $t2, $t0, $t1
    					sw $t2, 4($sp) 
    					addi $sp, $sp, 4
    					"""

    logical_less_than_int = """
    					lw $t1, 0($sp)
    					lw $t0, 4($sp)
    					slt $t2, $t0, $t1
    					sw $t2, 4($sp) 
    					addi $sp, $sp, 4
    					"""

    logical_less_than_double = """
    					l.s $f2, 0($sp)
    					l.s $f4, 4($sp)
    					li $t0 , 0
    					c.lt.s $f4, $f2
    					bc1f d_lt_{}
    					li $t0 , 1
    				d_lt_{}:
    					sw $t0, 4($sp)
    					addi $sp, $sp, 4
    					"""

    logical_less_than_or_equal_int = """
    					lw $t1, 0($sp)
    					lw $t0, 4($sp)
    					sle $t2, $t0, $t1
    					sw $t2, 4($sp) 
    					addi $sp, $sp, 4
    					"""
    logical_less_than_or_equal_double = """
    					l.s $f2, 0($sp)
    					l.s $f4, 4($sp)
    					li $t0 , 0
    					c.le.s $f4, $f2
    					bc1f d_le_{}
    					li $t0 , 1
    				d_le_{}:
    					sw $t0, 4($sp)
    					addi $sp, $sp, 4
    					"""

    logical_greater_than_int = """
    					lw $t1, 0($sp)
    					lw $t0, 4($sp)
    					sgt $t2, $t0, $t1
    					sw $t2, 4($sp) 
    					addi $sp, $sp, 4
    					"""

    logical_greater_than_double = """
    					l.s $f2, 0($sp)
    					l.s $f4, 4($sp)
    					li $t0 , 0
    					c.lt.s $f2, $f4
    					bc1f d_gt_{}
    					li $t0 , 1
    				d_gt_{}:
    					sw $t0, 4($sp)
    					addi $sp, $sp, 4
    					"""

    logical_greater_than_or_equal_int = """
    					lw $t1, 0($sp)
    					lw $t0, 4($sp)
    					sge $t2, $t0, $t1
    					sw $t2, 4($sp) 
    					addi $sp, $sp, 4
    					"""
    logical_greater_than_or_equal_double = """
    					l.s $f2, 0($sp)
    					l.s $f4, 4($sp)
    					li $t0 , 0
    					c.le.s $f2, $f4
    					bc1f d_ge_{}
    					li $t0 , 1
    				d_ge_{}:
    					sw $t0, 4($sp)
    					addi $sp, $sp, 4
    					"""

    logical_not = """
				lw $t0, 0($sp)
				xori $t1, $t0, 1
				sw $t1, 0($sp) 
				"""

    l_value_assign_true = """
				addi $t0, $gp, {}
				sw $t0, -4($sp)

				lw $t0, {}($gp)
				sw $t0, -8($sp)
				addi $sp, $sp, -8
				"""

    l_value_assign_false = """

				lw $t0, {}($gp)
				addi $sp, $sp, -4
				sw $t0, 0($sp)
				"""

    function_formal = """
			lw $t0, {}($fp)
			sw $t0, {}($gp)
			"""

    function = """
		{}:
			sw $fp, -4($sp)
			addi $fp, $sp, -4	# new frame pointer

			sw $ra, -4($fp)
			sw $s0, -8($fp)
			sw $s1, -12($fp)
			sw $s2, -16($fp)
			sw $s3, -20($fp)
			sw $s4, -24($fp)
			sw $s5, -28($fp)
			sw $s6, -32($fp)
			sw $s7, -36($fp)

			addi $sp, $sp, -36

			{}

			{}

		{}_end:

			lw $ra, -4($fp)
			lw $s0, -8($fp)
			lw $s1, -12($fp)
			lw $s2, -16($fp)
			lw $s3, -20($fp)
			lw $s4, -24($fp)
			lw $s5, -28($fp)
			lw $s6, -32($fp)
			lw $s7, -36($fp)

			addi $sp, $fp, 4  

			lw $fp, 0($fp)

			jr $ra
		"""

    main = """
		main:
			{}
			{}

			jal func_main

			li $v0, 10
			syscall

		"""

    side_functions = """
		print_bool: 
			beq $a0, $zero, print_bool_false
			b print_bool_true

		print_bool_false:
			la $a0, falseStr
			li $v0, 4
			syscall
			b print_bool_end

		print_bool_true:
			la $a0, trueStr
			li $v0, 4
			syscall
			b print_bool_end

		print_bool_end:
			jr $ra


		string_length: 
			li $v0, 0
			move $t1, $a0

		string_length_begin:
			lb $t2, 0($t1)
			beq $t2, $zero, string_length_end
			addi $v0, $v0, 1
			addi $t1, $t1, 1
			b string_length_begin

		string_length_end:
			jr $ra

		runtimeError:
			la $a0, runtimeErrorStr
			li $v0, 4	# sys call for print string
			syscall

			li $v0, 10
			syscall

		"""

    data_segment = """
		.data

		runtimeErrorStr: .asciiz "RUNTIME ERROR"
		falseStr: .asciiz "false"
		trueStr: .asciiz "true"
		newLineStr: .asciiz "\n"
		"""

    constant_str = "constantStr_{}: .asciiz \"{}\"\n"

    array_base = "array_{}: .word \"{}\"\n"

    return_calc_expr = """
    		lw $v0, 0($sp)
    		addi $sp, $sp, 4
    		"""

    return_back_to_caller = """
        j {function_name}_end
    """
    new_identifier = """
            	li $v0, 9
            	li $a0, {}
            	syscall

            	move $s0, $v0		# s0: address of object 

            	lw $t0, {}($gp) 	# t0: address of vtable
            	sw $t0, 0($s0)

            	addi $sp, $sp, -4
            	sw $s0, 0($sp)		# store object variable in stack

            	"""

    variable_init = """
        	li $t0, 0
        	sw $t0, {}($gp)
        	"""

    array_init = """
    				{}

    				lw $t1, 0($sp)	# array size
    				addi $sp, $sp, 4

    				ble $t1, $zero, runtimeError

    				add $t0, $t1, 1  # add one more place for size

    				mul $t0, $t0, 4	# array size in bytes

    				li $v0 , 9
    				move $a0 , $t0
    				syscall

    				move $s0, $v0		# s0: address of array

    				sw $t1, 0($s0)	# store size in first word

    				addi $sp, $sp, -4
    				sw $s0, 0($sp)

    				"""

    class_init = """

        		li $v0, 9
        		li $a0, {}
        		syscall

        		sw $v0, {}($gp)
        		move $s0, $v0		# s0: address of vtable 

        		"""

    store_class_functions = """
        				la $t0, {}
        				sw $t0, {}($s0)
        				"""


class MIPSDouble:
    convert_double_to_int = """
       """

    unary_neg_double = """
        l.s $f0, 0($sp)
        neg.s $f0, $f0
        s.s $f0, 0($sp)
    """
    add = """
        l.s $f0, 0($sp)
        l.s $f1, 4($sp)
        add.s $f2, $f0, $f1
        addi $sp, $sp, 4
        s.s $f2, 0($sp)
    """

    sub = """
        l.s $f0, 0($sp)
        l.s $f1, 4($sp)
        sub.s $f2, $f1, $f0
        addi $sp, $sp, 4
        s.s $f2, 0($sp)
    """

    mul = """
        l.s $f1, 0($sp)
		l.s $f2, 4($sp)
		mul.s $f0, $f1, $f2
		s.s $f0, 4($sp) 
		addi $sp, $sp, 4
    """

    div = """
        l.s $f1, 0($sp)
		l.s $f2, 4($sp)
		div.s $f0, $f2, $f1
		s.s $f0, 4($sp) 
		addi $sp, $sp, 4
    """


class MIPSStr:
    concat = """
        lw $s0, 0($sp)
        lw $s1, 4($sp)

        move $a0, $s0
        move $s2, $ra
        jal str_len
        move $ra, $s2
        move $t0, $v0

        move $a0, $s1
        move $s2, $ra
        jal str_len
        move $ra, $s2
        add $t0, $t0, $v0
        addi $t0, $t0, 1

        li $v0, 9
		move $a0, $t0
		syscall
		move $s2, $v0
		addi $sp, $sp, 4
		sw $s2, 0($sp)
		add_str1_{version}:
		lb $t0, 0($s0)
		beq $t0, $zero, add_str2_{version}
		sb $t0, 0($s2)
		addi $s0, $s0, 1
		addi $s2, $s2, 1
		j add_str1_{version}

		add_str2_{version}:
		lb $t1, 0($s1)
		beq $t1, $zero, end_str_concat_{version}
		sb $t1, 0($s2)
		addi $s1, $s1, 1
		addi $s2, $s2, 1
		j add_str2_{version}

		end_str_concat_{version}:
    """

    # TODO: check is this true?
    read_line = """
    # allocate memory for input string
    li $a0, 2000
    li $v0, 9
    syscall
    addi $sp, $sp, -4
    sw $v0, 0($sp)

    # read string from input
    move $a0, $v0
    li $a1, 2000
    li $v0, 8
    syscall

    lw $a0, 0($sp)
    start_read_str_{version}:
    lb $t0, 0($a0)
    beq $t0, $zero, end_read_str_{version}
    bne $t0, 10, not_remove_char_{version}
	move $t2, $zero
	sb $t2, 0($a0)
	not_remove_char_{version}:
	addi $a0, $a0, 1
	j start_read_str_{version}
    end_read_str_{version}: 
    """


class MIPSConditionalStmt:
    if_stmt = """
        {expression_code}
        lw $t0, 0($sp)
        addi $t1, $zero, 1
        beq $t0, $t1, if_stmt_block_{version}
        {else_statement_code}
        j end_if_stmt_{version}
        if_stmt_block_{version}:
        {statement_code}
        j end_if_stmt_{version}
        end_if_stmt_{version}:
    """

    while_stmt = """
        while_start_{version}:
        {expression_code}
        lw $t0, 0($sp)
        addi $t1, $zero, 1
        beq $t0, $t1, while_statement_{version}
        j end_while_{version}
        while_statement_{version}:
        {while_statement}
        j while_start_{version}
        end_while_{version}:
    """

    for_stmt = """
        {expression_code_1}
        for_start_{version}:
        {expression_code_2}
        lw $t0, 0($sp)
        addi $t1, $zero, 1
        bne $t0, $t1, for_end_{version}
        {statement_code}
        for_continue_label_{version}:
        {expression_code_3}
        j for_start_{version}
        for_end_{version}:
    """

    continue_stmt = """
        j {target_label}
    """

    break_stmt = continue_stmt


class MIPSPrintStmt:
    int_stmt = """
            li $v0, 1	
            lw $a0, {}($sp)
            syscall
			"""

    double_stmt = """
                li $v0, 2
                l.s $f12, {}($sp)
                syscall
                """

    bool_stmt = """
            lw $a0, {}($sp)
            move $s0, $ra 
            jal print_bool
            move $ra, $s0 
            """
    string_stmt = """
                li $v0, 4	 
                lw $a0, {}($sp)
                syscall
            """
    new_line_stmt = """
				la $a0, newLineStr
				addi $v0, $zero, 4
				syscall
				addi $sp, $sp, {}
            """

class MIPSSpecials:
	method_call = """
		{actuals}
		jal {func_name}
		addi $sp, $sp, {args_size}
	"""

	method_call_return = """
		sw $v0, -4($sp)
		addi $sp, $sp, -4
	"""

class MIPSArray:
	array_assign = """
		sw $t2, -4($sp)
		addi $sp, $sp, -4
	"""

	new_array_var = """
		        lw $t1, 0($sp) #index
				addi $sp, $sp, 4
				lw $t2, 0($sp) #array addr
				addi $sp, $sp, 4
				lw $t3, 0($t2) 	#array size

				addi $t1, $t1, 1 # add one to index ('cause of size)

				ble $t1, $zero, runtimeError
				bgt $t1, $t3, runtimeError


				mul $t1, $t1, 4 # index offset in bytes

				add $t2, $t2, $t1	#t2: address khooneye arraye ke mikhaim

				{assign_code}

				lw $t0, 0($t2)		#t0: value khooneye arraye ke mikhaim
				sw $t0, -4($sp)
				addi $sp, $sp, -4

	"""

	new_array = """
	    {expression}
		lw $t0, 0($sp)
		addi $sp, $sp, 4
		addi $t1, $t0, 1
		mul $t1, $t1, 4

		li $v0, 9
		move $a0, $t1
		syscall

		move $a0, $v0
		sw $t1, 0($sp)
		addi $sp, $sp, -4
		sw $s0, 0($sp)
	"""