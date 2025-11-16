import unittest
from memory import Bit
from fpu import fadd_f32, fsub_f32, fmul_f32

def hex32_to_bits_msb(h: str):
    h = h.strip().lower().replace("0x", "")
    val = int(h, 16) & 0xFFFFFFFF
    return tuple(Bit(bool((val >> i) & 1)) for i in range(31, -1, -1))

def bits_to_hex32(bits):  # MSB-first tuple[Bit,...] -> "0x????????"
    v = 0
    for b in bits:
        v = (v << 1) | (1 if b else 0)
    return f"0x{v:08X}"

class TestFPU_Basic(unittest.TestCase):
    def test_add_simple(self):
        a = hex32_to_bits_msb("3FC00000")  # 1.5
        b = hex32_to_bits_msb("40100000")  # 2.25
        res = fadd_f32(a, b)
        self.assertEqual(bits_to_hex32(res["res_bits"]), "0x40700000")  # 3.75
        self.assertFalse(res["flags"]["overflow"])
        self.assertFalse(res["flags"]["underflow"])
        self.assertFalse(res["flags"]["invalid"])

    def test_add_0_1_0_2(self):
        a = hex32_to_bits_msb("3DCCCCCD")  # 0.1
        b = hex32_to_bits_msb("3E4CCCCD")  # 0.2
        res = fadd_f32(a, b)
        self.assertEqual(bits_to_hex32(res["res_bits"]), "0x3E99999A")  # ties-to-even
        self.assertTrue(res["flags"]["inexact"])

    def test_sub_basic(self):
        a = hex32_to_bits_msb("40400000")  # 3.0
        b = hex32_to_bits_msb("3F800000")  # 1.0
        res = fsub_f32(a, b)
        self.assertEqual(bits_to_hex32(res["res_bits"]), "0x40000000")  # 2.0

    def test_add_signed_zero_tie(self):
        posz = hex32_to_bits_msb("00000000")
        negz = hex32_to_bits_msb("80000000")
        res = fadd_f32(posz, negz)
        self.assertEqual(bits_to_hex32(res["res_bits"]), "0x00000000")  # +0

    def test_inf_nan(self):
        pinf = hex32_to_bits_msb("7F800000")
        ninf = hex32_to_bits_msb("FF800000")
        res = fadd_f32(pinf, ninf)  # +inf + -inf → NaN (invalid)
        self.assertTrue(res["flags"]["invalid"])
        bits = res["res_bits"]
        # exp=all ones, frac != 0
        self.assertTrue(all(bits[1:9]))
        self.assertTrue(any(bits[9:]))

    def test_mul_simple(self):
        a = hex32_to_bits_msb("3FC00000")  # 1.5
        b = hex32_to_bits_msb("40000000")  # 2.0
        res = fmul_f32(a, b)
        self.assertEqual(bits_to_hex32(res["res_bits"]), "0x40400000")  # 3.0
        self.assertFalse(res["flags"]["overflow"])
        self.assertFalse(res["flags"]["underflow"])

    def test_mul_overflow_to_inf(self):
        max_norm = hex32_to_bits_msb("7F7FFFFF")
        two = hex32_to_bits_msb("40000000")
        res = fmul_f32(max_norm, two)
        self.assertTrue(res["flags"]["overflow"])
        self.assertEqual(bits_to_hex32(res["res_bits"]), "0x7F800000")  # +inf

if __name__ == "__main__":
    unittest.main()