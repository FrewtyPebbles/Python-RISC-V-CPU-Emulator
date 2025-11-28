# RV32F — Multiply two floats: 3.5 × 6.0 = 21.0
# No loops, only x-registers, only LUI/ADDI/SW/FLW/FMUL/FSW

.text
.globl _start
_start:

    # -------------------------------------------------
    # Build 3.5 in x10  → IEEE-754 single: 0x40600000
    lui   x10, 0x40600       # x10 = 0x40600000 = 3.5

    # Build 6.0 in x11  → IEEE-754 single: 0x40C00000
    lui   x11, 0x40C00       # x11 = 0x40C00000 = 6.0

    # Use 0x80000000 as a safe scratch memory area (works in Venus, RARS, Spike, QEMU, etc.)
    lui   x12, 0x80000       # x12 = 0x80000000 (pointer)

    # Store the two bit patterns into memory
    sw    x10, 0(x12)        # mem[0x80000000] = bit pattern of 3.5
    sw    x11, 4(x12)        # mem[0x80000004] = bit pattern of 6.0

    # Load them as proper floats into f-registers
    flw   f0,  0(x12)        # f0  = 3.5
    flw   f1,  4(x12)        # f1  = 6.0

    # Multiply → result goes to f3
    fmul.s f3, f0, f1        # f3 = 3.5 × 6.0 = 21.0

    # Optional: store the result so you can see the exact bit pattern in memory
    fsw   f3, 8(x12)         # mem[0x80000008] = 0x41A80000 (exactly 21.0)
