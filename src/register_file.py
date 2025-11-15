from memory import Bit, Bitx32, Bitx5
from register import Register32bit, Register16bit, Register8bit, FloatRegister32bit, Register
from encoder_decoder import decoder5x32, one_hot_to_decimal

class RegisterFile:

    def __init__(self):
        self.registers:list[Register] = [Register32bit() for _ in range(32)]

    def update(self, read_reg_1_adr:Bitx5, read_reg_2_adr:Bitx5, write_reg_adr:Bitx5, write_data:Bitx32, control_reg_write:Bit, clock:Bit) -> tuple[Bitx32, Bitx32]:
        read_reg_1_pos_one_hot = decoder5x32(*read_reg_1_adr)
        read_reg_2_pos_one_hot = decoder5x32(*read_reg_2_adr)
        write_reg_pos_one_hot = decoder5x32(*write_reg_adr)

        read_reg_1_pos = one_hot_to_decimal(read_reg_1_pos_one_hot)
        read_reg_2_pos = one_hot_to_decimal(read_reg_2_pos_one_hot)
        write_reg_pos = one_hot_to_decimal(write_reg_pos_one_hot)

        if control_reg_write:
            write_reg = self.registers[write_reg_pos]
            for b_n, bit in enumerate(write_reg):
                bit.value = write_data[b_n].value

        return self.registers[read_reg_1_pos].read_bits(), self.registers[read_reg_2_pos].read_bits()
        

if __name__ == "__main__":

    # Helpers
    def bx5(val:int) -> Bitx5:
        return tuple(Bit(bool((val >> i) & 1)) for i in range(5))

    def bx32(val:int) -> Bitx32:
        return tuple(Bit(bool((val >> i) & 1)) for i in range(32))

    def b32_to_int(bits:Bitx32) -> int:
        result = 0
        for i, b in enumerate(bits):
            if b:
                result |= (1 << i)
        return result


    print("===== FULL EXHAUSTIVE REGISTER FILE TESTS =====")
    rf = RegisterFile()


    # ------------------------------------------------
    # Test 1: All registers initially zero
    # ------------------------------------------------
    print("TEST 1: Verify all 32 registers start at zero...")
    for r in range(32):
        out1, out2 = rf.update(bx5(r), bx5(0), bx5(0), bx32(0), Bit(False), Bit(False))
        assert b32_to_int(out1) == 0, f"Register x{r} is not initialized to 0!"
    print("  PASS")


    # ------------------------------------------------
    # Test 2: Write a unique value into every register using RegWrite=1
    # ------------------------------------------------
    print("TEST 2: Write unique values to all 32 registers...")
    for reg in range(32):
        rf.update(
            read_reg_1_adr = bx5(0),
            read_reg_2_adr = bx5(0),
            write_reg_adr  = bx5(reg),
            write_data     = bx32(reg + 1000),  # unique
            control_reg_write = Bit(True),
            clock = Bit(True)
        )
    print("  PASS")


    # ------------------------------------------------
    # Test 3: Fully exhaustively read all possible 32×32 combinations
    # ------------------------------------------------
    print("TEST 3: Exhaustively test all read address combinations...")

    for r1 in range(32):
        for r2 in range(32):
            out1, out2 = rf.update(bx5(r1), bx5(r2), bx5(0), bx32(0), Bit(False), Bit(False))

            expected1 = (0 if r1 == 0 else (r1 + 1000))
            expected2 = (0 if r2 == 0 else (r2 + 1000))

            assert b32_to_int(out1) == expected1, f"Read mismatch on x{r1}"
            assert b32_to_int(out2) == expected2, f"Read mismatch on x{r2}"

    print("  PASS")


    # ------------------------------------------------
    # Test 4: RegWrite = 0 MUST block updates for all 32 registers
    # ------------------------------------------------
    print("TEST 4: Verify RegWrite=0 blocks writes to all registers...")

    for reg in range(32):
        original = 0 if reg == 0 else (reg + 1000)

        rf.update(
            read_reg_1_adr = bx5(reg),
            read_reg_2_adr = bx5(0),
            write_reg_adr  = bx5(reg),
            write_data     = bx32(999999),
            control_reg_write = Bit(False),   # IMPORTANT
            clock = Bit(True)
        )

        out1, _ = rf.update(bx5(reg), bx5(0), bx5(0), bx32(0), Bit(False), Bit(False))
        assert b32_to_int(out1) == original, f"Register x{reg} changed when RegWrite=0!"
    print("  PASS")


    # ------------------------------------------------
    # Test 5: x0 must ALWAYS remain zero (RISC-V rule)
    # ------------------------------------------------
    print("TEST 5: Verify x0 is hardwired to zero...")

    # Attempt to write many different patterns (exhaustively over all 32 bits)
    for bit_index in range(32):
        val = (1 << bit_index)
        rf.update(
            read_reg_1_adr = bx5(0),
            read_reg_2_adr = bx5(0),
            write_reg_adr  = bx5(0),
            write_data     = bx32(val),
            control_reg_write = Bit(True),
            clock = Bit(True)
        )
        out, _ = rf.update(bx5(0), bx5(0), bx5(0), bx32(0), Bit(False), Bit(False))
        assert b32_to_int(out) == 0, "x0 changed! ILLEGAL in RISC-V!"

    print("  PASS")


    print("\n===== ALL EXHAUSTIVE TESTS PASSED SUCCESSFULLY =====")
