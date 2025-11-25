# branch_test_supported.s
# Uses only: add, addi, beq, bne, jal, jalr, lui, auipc, lw, sw
# Final result:
#   x31 = 1234  → ALL branches work perfectly
#   x31 = 0xBAD → at least one branch failed

    .text
    .globl _start
_start:
    lui   x1, 0x00001        # x1 = 0x1000
    addi  x2, x0, 10         # x2 = 10
    addi  x3, x0, 10         # x3 = 10
    addi  x4, x0, 20         # x4 = 20

    # Test 1: BEQ taken (x2 == x3)
    beq   x2, x3, beq_ok
    addi  x31, x0, 0xBAD      # should be SKIPPED
    jal   x0, fail

beq_ok:
    addi  x30, x0, 100       # proof we took the branch

    # Test 2: BNE taken (x2 != x4)
    bne   x2, x4, bne_ok
    addi  x31, x0, 0xBAD      # should be SKIPPED
    jal   x0, fail

bne_ok:
    addi  x30, x30, 200      # x30 = 300

    # Test 3: BEQ not taken (backward branch test)
    addi  x5, x0, 5
loop:
    addi  x5, x5, -1
    bne   x5, x0, loop       # backward branch (should work if B-type is correct)
    beq   x5, x0, loop_exit  # x5 == 0 → take this forward branch
    addi  x31, x0, 0xBAD
    jal   x0, fail

loop_exit:
    addi  x30, x30, 300      # x30 = 600

    # Test 4: Forward branch over junk
    beq   x0, x0, final      # always taken (x0 == x0)
    addi  x31, x0, 0xBAD      # SKIPPED
    sw    x0, 0(x1)           # SKIPPED
    lw    x6, 0(x1)           # SKIPPED

final:
    addi  x30, x30, 634      # x30 = 1234
    addi  x31, x0, 1234      # x31 = 1234 → SUCCESS!

done:
    jal   x0, done           # infinite loop

fail:
    addi  x31, x0, 0xBAD     # obvious failure
    jal   x0, fail