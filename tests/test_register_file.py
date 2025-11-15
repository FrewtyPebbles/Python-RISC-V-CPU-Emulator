import pytest
from memory import Bit, Bitx32, Bitx5
from register_file import RegisterFile  # adjust import to your module

# Unit Tests created with assistance from AI to ensure correctness.

# Helper functions
def bx5(val: int) -> Bitx5:
    return tuple(Bit(bool((val >> i) & 1)) for i in range(5))


def bx32(val: int) -> Bitx32:
    return tuple(Bit(bool((val >> i) & 1)) for i in range(32))


def b32_to_int(bits: Bitx32) -> int:
    result = 0
    for i, b in enumerate(bits):
        if b:
            result |= (1 << i)
    return result


# Creates a new RegisterFile for each test
@pytest.fixture
def rf():
    return RegisterFile()


# Test 1: All registers initially zero
def test_registers_initially_zero(rf):
    for r in range(32):
        out1, out2 = rf.update(bx5(r), bx5(0), bx5(0), bx32(0), Bit(False), Bit(False))
        assert b32_to_int(out1) == 0, f"Register x{r} is not initialized to 0!"


# Test 2: Write unique values into all registers with RegWrite=1
def test_write_unique_values(rf):
    for reg in range(32):
        rf.update(
            read_reg_1_adr=bx5(0),
            read_reg_2_adr=bx5(0),
            write_reg_adr=bx5(reg),
            write_data=bx32(reg + 1000),
            control_reg_write=Bit(True),
            clock=Bit(True)
        )


# Test 3: Exhaustively read all 32x32 combinations
def test_exhaustive_read(rf):
    # First populate registers
    for reg in range(32):
        rf.update(
            read_reg_1_adr=bx5(0),
            read_reg_2_adr=bx5(0),
            write_reg_adr=bx5(reg),
            write_data=bx32(reg + 1000),
            control_reg_write=Bit(True),
            clock=Bit(True)
        )

    # Now read all combinations
    for r1 in range(32):
        for r2 in range(32):
            out1, out2 = rf.update(bx5(r1), bx5(r2), bx5(0), bx32(0), Bit(False), Bit(False))
            expected1 = 0 if r1 == 0 else r1 + 1000
            expected2 = 0 if r2 == 0 else r2 + 1000
            assert b32_to_int(out1) == expected1, f"Read mismatch on x{r1}"
            assert b32_to_int(out2) == expected2, f"Read mismatch on x{r2}"


# Test 4: RegWrite=0 blocks all writes
def test_regwrite_zero_blocks_writes(rf):
    # First populate registers
    for reg in range(32):
        rf.update(
            read_reg_1_adr=bx5(0),
            read_reg_2_adr=bx5(0),
            write_reg_adr=bx5(reg),
            write_data=bx32(reg + 1000),
            control_reg_write=Bit(True),
            clock=Bit(True)
        )

    # Attempt to overwrite with RegWrite=0
    for reg in range(32):
        original = 0 if reg == 0 else reg + 1000
        rf.update(
            read_reg_1_adr=bx5(reg),
            read_reg_2_adr=bx5(0),
            write_reg_adr=bx5(reg),
            write_data=bx32(999999),
            control_reg_write=Bit(False),
            clock=Bit(True)
        )
        out1, _ = rf.update(bx5(reg), bx5(0), bx5(0), bx32(0), Bit(False), Bit(False))
        assert b32_to_int(out1) == original, f"Register x{reg} changed when RegWrite=0!"


# Test 5: x0 always remains zero
def test_x0_hardwired_zero(rf):
    for bit_index in range(32):
        val = 1 << bit_index
        rf.update(
            read_reg_1_adr=bx5(0),
            read_reg_2_adr=bx5(0),
            write_reg_adr=bx5(0),
            write_data=bx32(val),
            control_reg_write=Bit(True),
            clock=Bit(True)
        )
        out, _ = rf.update(bx5(0), bx5(0), bx5(0), bx32(0), Bit(False), Bit(False))
        assert b32_to_int(out) == 0, "x0 changed! ILLEGAL in RISC-V!"
