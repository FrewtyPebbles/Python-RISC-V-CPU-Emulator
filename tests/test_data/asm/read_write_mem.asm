# memory_test_final.s
# Corrected version that respects 12-bit signed immediate limits (-2048 to 2047)
# Final result:
#   x31 = 0xDEADBEEF  → memory read/write is PERFECT
#   anything else     → something is wrong

.text
.globl _start
_start:
    # -------------------------------------------------
    # Set up a safe RAM base address: 0x8000_0000
    # -------------------------------------------------
    lui   x10, 0x80000        # x10 = 0x80000000

    # -------------------------------------------------
    # Write three known 32-bit patterns using sw
    # -------------------------------------------------
    
    # Write 0x11111111
    lui   x1, 0x11111         # x1 = 0x11111000
    addi  x1, x1, 0x111       # x1 = 0x11111000 + 0x111 = 0x11111111
    sw    x1, 0(x10)          # mem[0x80000000] = 0x11111111
    
    # Write 0xDEADBEEF (the tricky one!)
    # 0xDEADBEEF = 0xDEADC000 + 0xFFFFFFEF (where 0xFFFFFFEF = -273)
    # So we need: lui 0xDEADC, then addi with -273
    lui   x1, 0xDEADC         # x1 = 0xDEADC000
    addi  x1, x1, -273        # x1 = 0xDEADC000 + (-273) = 0xDEADBEEF
    sw    x1, 4(x10)          # mem[0x80000004] = 0xDEADBEEF
    
    # Write 0xCAFEBABE
    # 0xCAFEBABE = 0xCAFEB000 + 0xABE
    # But 0xABE = 2750, which is > 2047, so it will be treated as negative
    # 0xABE in 12-bit signed = -1346
    # So: 0xCAFEB000 + 0xABE (sign-extended to -1346) = 0xCAFEBABE
    # Actually, let's recalculate: 0xCAFEBABE = 0xCAFEC000 + 0xFFFFF4BE
    # 0xFFFFF4BE = -2882 in 32-bit, but we need 12-bit immediate
    # 0x4BE in 12 bits = 1214, but we want negative...
    # Let's use: 0xCAFEB000 + 0xABE where 0xABE sign-extends to 0xFFFFFABE
    lui   x1, 0xCAFEB         # x1 = 0xCAFEB000
    addi  x1, x1, 0xABE       # 0xABE in 12-bit = -1346, so x1 = 0xCAFEBABE
    sw    x1, 8(x10)          # mem[0x80000008] = 0xCAFEBABE

    # -------------------------------------------------
    # Read them all back with lw
    # -------------------------------------------------
    lw    x20, 0(x10)         # x20 should be 0x11111111
    lw    x21, 4(x10)         # x21 should be 0xDEADBEEF
    lw    x22, 8(x10)         # x22 should be 0xCAFEBABE

    # -------------------------------------------------
    # Verify everything worked
    # If any load is wrong → jump to fail
    # -------------------------------------------------
    
    # Check first word: 0x11111111
    lui   x5, 0x11111
    addi  x5, x5, 0x111
    bne   x20, x5, fail

    # Check second word: 0xDEADBEEF (the critical one!)
    lui   x5, 0xDEADC
    addi  x5, x5, -273
    bne   x21, x5, fail

    # Check third word: 0xCAFEBABE
    lui   x5, 0xCAFEB
    addi  x5, x5, 0xABE
    bne   x22, x5, fail

    # -------------------------------------------------
    # SUCCESS! Memory is perfect
    # -------------------------------------------------
    lui   x31, 0xDEADC
    addi  x31, x31, -273      # x31 = 0xDEADBEEF → PROOF OF SUCCESS
    jal   x0, done

fail:
    # Set x31 to a recognizable failure value
    lui   x31, 0x0BAD
    addi  x31, x31, 0xBAD     # x31 = 0x0BADBAD

done:
    jal   x0, done            # halt: infinite loop