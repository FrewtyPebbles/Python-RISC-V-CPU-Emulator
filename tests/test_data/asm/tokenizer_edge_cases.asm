# === Test File for RISC-V Tokenizer Edge Cases ===

# 1. Instructions (R, I, S, B, U, J types)
add x0, x1, x2        # R-type
sub x31, x30, x29     # R-type with max registers
addi x5, x6, -42      # I-type with negative immediate
andi x7, x8, 0        # I-type with zero immediate
ori x9, x10, 123456   # I-type with large immediate
sll x11, x12, 31      # R-type shift
srl x13, x14, 0       # R-type shift by zero
sra x15, x16, 15      # R-type shift
lb x17, 0(x18)        # Load with parentheses
lh x19, -4(x20)       # Load with negative offset
lw x21, 100(x22)      # Load with large positive offset
sb x23, 8(x24)        # Store
sh x25, -8(x26)       # Store with negative offset
sw x27, 0(x28)        # Store zero offset
beq x29, x30, label1  # Branch to label
bne x1, x2, label2
blt x3, x4, label3
bge x5, x6, label4
jal x7, label5        # Jump
jalr x8, x9, 12
lui x10, 0xFFFFF
auipc x11, 0x12345

# 2. Labels
label1:
label2:
label3:
label4:
label5:

# 3. Identifiers
my_label:
anotherLabel123:
__hiddenLabel:

# 4. Numbers
0
-0
42
-999
1234567890

# 5. Registers edge cases
x0
x1
x31

# 6. Commas and parentheses
add x1 , x2 , x3       # spaces around commas
lw x4,0(x5)            # no spaces
sw x6, -12(x7)         # negative offset

# 7. Whitespace variations
    add x1, x2, x3     # leading spaces
add x4, x5, x6         # normal
add    x7 , x8 , x9    # multiple spaces

# 8. Comments edge cases
# Full line comment
add x1, x2, x3  # Inline comment
# Comment with symbols !@#$%^&*()_+
addi x4, x5, 10   # Comment after instruction

# 9. Mixed tricky cases
loop_start: addi x1, x2, 0
    beq x1, x0, loop_end
loop_end: jal x0, loop_start
