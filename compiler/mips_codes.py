class MIPS:

    @staticmethod
    def set_multiple_var(base_mips: str, value: str, count=1):
        while True:
            try:
                return base_mips.format(*list([value] * count))
            except:
                count += 1
                continue

    bool_const = """
            li $t0, {value}
            addi $sp, $sp, -4
            sw $t0, 0($sp)
            """
    int_const = bool_const
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
			sub $t3, $t1, $t2
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
    		div $t3, $t1, $t2
    		sw $t3, 4($sp) 
    		addi $sp, $sp, 4
            """

    assignment_int = """
            lw $t0, 0($sp)
    		lw $t1, 4($sp)
    		addi $sp, $sp, 4
    		sw $t0, 0($sp) 
            """

    module_int = """
            lw $t0, 0($sp)
			lw $t1, 4($sp)
			div $t1, $t0
			sw $hi, 4($sp) 
			addi $sp, $sp, 4
            """

    unary_neg_int = """
            lw $t0, 0($sp)
            sub $t0, $zero, $t0
            sw $t0, 0($sp)
            """
    semantic_error = """
    		.text
    		.globl main
    		main:
    		#print error message
    		la $a0 , errorMsg
    		addi $v0 , $zero, 4
    		syscall
    		.data
    		errorMsg: .asciiz "Semantic Error"
    		"""


class MIPSDouble:
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


class MIPSStr:
    concat = """
        
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
    		l.s $f2, 0($sp)
    		l.s $f4, 4($sp)
    		li $t0 , 0
    		c.eq.s $f4, $f2
    		bc1f d_eq_{}
    		li $t0 , 1
    	d_eq_{}:
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
					### not_equal string
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

