.section .text
.globl _start
_start:
addi x1, x0, 5 # x1 = 5
addi x2, x0, 10 # x2 = 10
add x3, x1, x2 # x3 = 15
sub x4, x2, x1 # x4 = 5
lui x5, 0x00010 # x5 = 0x0001_0000 (data base)
sw x3, 0(x5) # mem[0x0001_0000] = 15
lw x4, 0(x5) # x4 = 15
beq x3, x4, label1 # branch forward by 8 bytes
addi x6, x0, 1 # skipped if branch taken
label1:
addi x6, x0, 2 # x6 = 2
jal x0, 0 # halt: infinite loop