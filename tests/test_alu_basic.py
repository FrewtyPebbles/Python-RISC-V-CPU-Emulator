import unittest
from memory import Bit
from alu import ALU32, alu32

# Helpers
def hex32_to_bits_msb(h: str):
    h = h.strip().lower().replace("0x", "")
    val = int(h, 16) & 0xFFFFFFFF
    return tuple(Bit(bool((val >> i) & 1)) for i in range(31, -1, -1))

def bits_to_hex32(bits):
    v = 0
    for b in bits:
        v = (v << 1) | (1 if b else 0)
    return f"0x{v:08X}"


class TestALU32(unittest.TestCase):
    def setUp(self):
        self.alu = ALU32()

    def test_add_overflow_and_flags(self):
        a = hex32_to_bits_msb("7FFFFFFF")
        b = hex32_to_bits_msb("00000001")
        out = self.alu.exec(a, b, "ADD")
        self.assertEqual(bits_to_hex32(out["result"]), "0x80000000")
        self.assertEqual(out["flags"], {"N": True, "Z": False, "C": False, "V": True})

    def test_sub_overflow_and_flags(self):
        a = hex32_to_bits_msb("80000000")
        b = hex32_to_bits_msb("00000001")
        out = self.alu.exec(a, b, "SUB")
        self.assertEqual(bits_to_hex32(out["result"]), "0x7FFFFFFF")
        self.assertEqual(out["flags"], {"N": False, "Z": False, "C": True, "V": True})

    def test_add_neg1_plus_neg1(self):
        a = hex32_to_bits_msb("FFFFFFFF")
        b = hex32_to_bits_msb("FFFFFFFF")
        out = self.alu.exec(a, b, "ADD")
        self.assertEqual(bits_to_hex32(out["result"]), "0xFFFFFFFE")
        self.assertEqual(out["flags"], {"N": True, "Z": False, "C": True, "V": False})

    def test_add_13_plus_neg13_zero(self):
        a = hex32_to_bits_msb("0000000D")
        b = hex32_to_bits_msb("FFFFFFF3")
        out = self.alu.exec(a, b, "ADD")
        self.assertEqual(bits_to_hex32(out["result"]), "0x00000000")
        # C=1 means "no borrow" in subtraction; for addition here carry=1 is OK
        self.assertEqual(out["flags"]["Z"], True)
        self.assertEqual(out["flags"]["V"], False)

    def test_sll_by_1(self):
        a = hex32_to_bits_msb("00000001")
        shamt = hex32_to_bits_msb("00000001")  # lower 5 bits = 1
        out = self.alu.exec(a, shamt, "SLL")
        self.assertEqual(bits_to_hex32(out["result"]), "0x00000002")
        self.assertEqual(out["flags"]["C"], False)
        self.assertEqual(out["flags"]["V"], False)

    def test_sll_by_4(self):
        a = hex32_to_bits_msb("00000003")
        shamt = hex32_to_bits_msb("00000004")  # lower 5 bits = 4
        out = self.alu.exec(a, shamt, "SLL")
        self.assertEqual(bits_to_hex32(out["result"]), "0x00000030")

    def test_srl_by_1(self):
        a = hex32_to_bits_msb("80000001")
        shamt = hex32_to_bits_msb("00000001")
        out = self.alu.exec(a, shamt, "SRL")
        self.assertEqual(bits_to_hex32(out["result"]), "0x40000000")

    def test_sra_by_1(self):
        a = hex32_to_bits_msb("80000001")  # negative
        shamt = hex32_to_bits_msb("00000001")
        out = self.alu.exec(a, shamt, "SRA")
        # arithmetic: sign bit replicated
        self.assertEqual(bits_to_hex32(out["result"]), "0xC0000000")
        self.assertTrue(out["flags"]["N"])

    def test_srl_large_amount(self):
        a = hex32_to_bits_msb("F0000000")
        shamt = hex32_to_bits_msb("00000010")  # 16
        out = self.alu.exec(a, shamt, "SRL")
        self.assertEqual(bits_to_hex32(out["result"]), "0x0000F000")

    def test_sll_large_amount(self):
        a = hex32_to_bits_msb("0000F0F0")
        shamt = hex32_to_bits_msb("00000010")  # 16
        out = self.alu.exec(a, shamt, "SLL")
        self.assertEqual(bits_to_hex32(out["result"]), "0xF0F00000")

    def test_sra_all_ones_stays_all_ones(self):
        a = hex32_to_bits_msb("FFFFFFFF")
        shamt = hex32_to_bits_msb("0000001F")  # shift by 31
        out = self.alu.exec(a, shamt, "SRA")
        self.assertEqual(bits_to_hex32(out["result"]), "0xFFFFFFFF")
        self.assertTrue(out["flags"]["N"])

    def test_function_wrapper(self):
        a = hex32_to_bits_msb("00000002")
        b = hex32_to_bits_msb("00000003")
        out = alu32(a, b, "ADD")
        self.assertEqual(bits_to_hex32(out["result"]), "0x00000005")  # sanity