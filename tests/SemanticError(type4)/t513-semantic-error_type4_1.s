
    		.text
    		.globl main
    		main:
    		#print error message
    		la $a0 , errorMsg
    		addi $v0 , $zero, 4
    		syscall
    		.data
    		errorMsg: .asciiz "Semantic Error"
    		