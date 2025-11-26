.text
.globl _start
_start:
    # Program to store 0xDEADBEEF at memory address 0x1000

    # Load upper 20 bits of 0xDEADBEEF into x5
    lui x5, 0xDEADB          # x5 = 0xDEADB000

    # Add lower 12 bits (0xEEF) to complete the value
    addi x5, x5, 0xEEF       # x5 = 0xDEADB000 + 0xEEF = 0xDEADBEEF

    # Load the target memory address into x6
    lui x6, 0x1              # x6 = 0x1000 (address where we'll store)

    # Store the word at memory address
    sw x5, 0(x6)             # Memory[0x1000] = 0xDEADBEEF

    # Optional: Load it back to verify
    lw x7, 0(x6)             # x7 = Memory[0x1000] (should be 0xDEADBEEF)

# Infinite loop (halt)
# loop:
    # beq x0, x0, loop     # Branch to self forever