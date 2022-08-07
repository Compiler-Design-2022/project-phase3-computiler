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
