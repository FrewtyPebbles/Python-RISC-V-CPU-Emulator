.text
.globl _start
_start:
    addi x2, x0, 3     # load 3
    addi x3, x0, 2     # load 2
    add  x1, x2, x3    # x1 = 3 + 2
# done:
#     jal  x0, done      # loop forever (optional)