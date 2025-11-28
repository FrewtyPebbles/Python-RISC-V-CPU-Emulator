# RV32I + RV32F — only allowed instructions, only x-registers, no loop

.text
.globl _start
_start:

    # Build 1.5 (0x3FC00000) in x5
    lui   x5, 0x3FC00       # x5 = 0x3FC00000 = 1.5

    # Build 2.25 (0x40200000) in x6
    lui   x6, 0x40200       # x6 = 0x40200000 = 2.25

    # Use x7 as temporary memory pointer (any writable address, e.g. 0x80000000)
    lui   x7, 0x80000       # x7 = 0x80000000 (safe writable area in most sims)

    # Store the bit patterns
    sw    x5, 0(x7)         # mem[0x80000000] = 1.5 bits
    sw    x6, 4(x7)         # mem[0x80000004] = 2.25 bits

    # Load as floats
    flw   f0, 0(x7)         # f0 = 1.5
    flw   f1, 4(x7)         # f1 = 2.25

    # Add → result in f3
    fadd.s f3, f0, f1       # f3 = 3.75

    # Optional: store result back so you can see it in memory
    fsw   f3, 8(x7)         # mem[0x80000008] = 0x40700000 = 3.75

    # Done — program ends here (no loop, simulator will stop)