.text
.globl _start
_start:

    # Load 32-bit constants manually (no %hi/%lo, only plain numbers)

    lui   x1,  0x0000A
    addi  x1,  x1, 0x5A5        # x1  = 0x0000A5A5   ( 43605)

    lui   x2,  0xFFFF5
    addi  x2,  x2, 0xA5A        # x2  = 0xFFFF5A5A   (-43606 signed)

    lui   x3,  0x00001
    addi  x3,  x3, 0x337        # x3  = 0x00001337   ( 4919)

    lui   x4,  0xFFFFF
    addi  x4,  x4, -2           # x4  = 0xFFFFFFFE   (-2)

    # RV32M instructions — each uses unique registers

    mul     x10, x1, x2         # low 32 bits of signed x signed
    mulh    x11, x1, x2         # high 32 bits (signed x signed)
    mulhsu  x12, x1, x3         # high 32 bits (signed x unsigned)
    mulhu   x13, x2, x3         # high 32 bits (unsigned x unsigned)

    div     x14, x1, x4         # signed division by -2
    divu    x15, x2, x3         # unsigned division
    rem     x16, x1, x4         # signed remainder
    remu    x17, x2, x3         # unsigned remainder
