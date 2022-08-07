class MIPS:
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
