import pytest
from memory import Bitx32, Bitx5
from rv32i_register_file import RV32IRegisterFile

# --- Helpers ---------------------------------------------------

def bx5(n: int) -> Bitx5:
    return tuple(int(bool((n >> i) & 1)) for i in range(5))

def bx32(n: int) -> Bitx32:
    return tuple(int(bool((n >> i) & 1)) for i in range(32))

def bits_to_int(bits: Bitx32) -> int:
    return sum((bit << i) for i, bit in enumerate(bits))


# --- Tests ------------------------------------------------------

def test_initial_registers_are_zero():
    rf = RV32IRegisterFile()
    for i in range(32):
        val, _ = rf.update(bx5(i), bx5(0), bx5(0), bx32(0), 0)
        assert bits_to_int(val) == 0


def test_basic_write_and_read():
    rf = RV32IRegisterFile()
    rf.update(bx5(0), bx5(0), bx5(5), bx32(123), 1)  # write x5 = 123
    val, _ = rf.update(bx5(5), bx5(0), bx5(0), bx32(0), 0)
    assert bits_to_int(val) == 123


def test_x0_is_always_zero():
    rf = RV32IRegisterFile()
    rf.update(bx5(0), bx5(0), bx5(0), bx32(9999999), 1)
    val, _ = rf.update(bx5(0), bx5(0), bx5(0), bx32(0), 0)
    assert bits_to_int(val) == 0


def test_write_disabled_does_not_change_register():
    rf = RV32IRegisterFile()
    rf.update(bx5(3), bx5(0), bx5(3), bx32(555), 0)
    val, _ = rf.update(bx5(3), bx5(0), bx5(0), bx32(0), 0)
    assert bits_to_int(val) == 0


def test_write_and_read_all_registers():
    rf = RV32IRegisterFile()
    for i in range(1, 32):  # skip x0
        rf.update(bx5(0), bx5(0), bx5(i), bx32(i * 11), 1)
    for i in range(1, 32):
        val, _ = rf.update(bx5(i), bx5(0), bx5(0), bx32(0), 0)
        assert bits_to_int(val) == i * 11


def test_read_two_registers():
    rf = RV32IRegisterFile()
    rf.update(bx5(0), bx5(0), bx5(8), bx32(1010), 1)
    rf.update(bx5(0), bx5(0), bx5(9), bx32(2020), 1)

    v1, v2 = rf.update(bx5(8), bx5(9), bx5(0), bx32(0), 0)

    assert bits_to_int(v1) == 1010
    assert bits_to_int(v2) == 2020


def test_rs1_equals_rs2():
    rf = RV32IRegisterFile()
    rf.update(bx5(0), bx5(0), bx5(12), bx32(777), 1)
    v1, v2 = rf.update(bx5(12), bx5(12), bx5(0), bx32(0), 0)
    assert bits_to_int(v1) == 777
    assert bits_to_int(v2) == 777


def test_write_same_register_twice():
    rf = RV32IRegisterFile()
    rf.update(bx5(0), bx5(0), bx5(4), bx32(11), 1)
    rf.update(bx5(0), bx5(0), bx5(4), bx32(22), 1)
    v, _ = rf.update(bx5(4), bx5(0), bx5(0), bx32(0), 0)
    assert bits_to_int(v) == 22


def test_randomized_register_operations():
    rf = RV32IRegisterFile()
    import random
    random.seed(0)

    expected = [0] * 32

    # Perform random operations
    for _ in range(200):
        reg = random.randint(0, 31)
        val = random.randint(0, 0xFFFFFFFF)
        write = int(bool(random.getrandbits(1)))

        rf.update(bx5(0), bx5(0), bx5(reg), bx32(val), write)

        if write and reg != 0:
            expected[reg] = val

    # Verify results
    for i in range(32):
        v, _ = rf.update(bx5(i), bx5(0), bx5(0), bx32(0), 0)
        assert bits_to_int(v) == expected[i]


def test_read_port_independence():
    rf = RV32IRegisterFile()
    rf.update(bx5(0), bx5(0), bx5(3), bx32(100), 1)
    rf.update(bx5(0), bx5(0), bx5(7), bx32(200), 1)

    out1, out2 = rf.update(bx5(3), bx5(7), bx5(0), bx32(0), 0)
    assert bits_to_int(out1) == 100
    assert bits_to_int(out2) == 200
