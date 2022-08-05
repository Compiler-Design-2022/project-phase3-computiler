from compiler.semantic import SemanticError

def generate_code(tree):
    try:
        pass
    except SemanticError:
         mips_code = """
         .text
         .global main
         main:
         la $a0 , errorMsg
         addi $v0, $zero, 4
         syscall
         jr $ra

         .data
         errorMsg: .asciiz "Semantic Error"
         """
    return mips_code