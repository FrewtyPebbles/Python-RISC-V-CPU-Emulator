import unittest
from memory import Bit
from fpu import fadd_f32, fsub_f32, fmul_f32

def hex32_to_bits_msb(h: str):
    """Hex string -> MSB-first tuple[Bit,...] of length 32."""
    h = h.strip().lower().replace("0x", "")
    val = int(h, 16) & 0xFFFFFFFF
    return tuple(Bit(bool((val >> i) & 1)) for i in range(31, -1, -1))

def bits_to_hex32(bits):
    """MSB-first tuple[Bit,...] -> '0x????????' uppercase."""
    v = 0
    for b in bits:
        v = (v << 1) | (1 if b else 0)
    return f"0x{v:08X}"

# Common constants
PZERO  = "00000000"
NZERO  = "80000000"
PINF   = "7F800000"
NINF   = "FF800000"
QNAN   = "7FC00000"  # canonical quiet NaN

ONE    = "3F800000"
TWO    = "40000000"
HALF   = "3F000000"
ONE_PT5= "3FC00000"
TWO_PT25 = "40100000"
THREE  = "40400000"

# Boundary magnitudes
MAX_NORM = "7F7FFFFF"  # max finite
MIN_NORM = "00800000"  # min normal = 2^-126
MIN_SUB  = "00000001"  # smallest subnormal
BIG_SUB  = "007FFFFF"  # largest subnormal


class TestFPU_Basic(unittest.TestCase):

    def test_add_simple(self):
        a = hex32_to_bits_msb(ONE_PT5)    # 1.5
        b = hex32_to_bits_msb(TWO_PT25)   # 2.25
        res = fadd_f32(a, b)
        self.assertEqual(bits_to_hex32(res["res_bits"]), "0x40700000")  # 3.75
        self.assertFalse(res["flags"]["overflow"])
        self.assertFalse(res["flags"]["underflow"])
        self.assertFalse(res["flags"]["invalid"])

    def test_add_one_plus_one_carry_normalize(self):
        a = hex32_to_bits_msb(ONE)
        b = hex32_to_bits_msb(ONE)
        res = fadd_f32(a, b)
        self.assertEqual(bits_to_hex32(res["res_bits"]), "0x40000000")  # 2.0
        # Expect a normalization with carry in the trace
        self.assertTrue(any("NORMALIZE: carry" in t for t in res["trace"]))

    def test_add_0_1_0_2_ties_to_even(self):
        a = hex32_to_bits_msb("3DCCCCCD")  # 0.1
        b = hex32_to_bits_msb("3E4CCCCD")  # 0.2
        res = fadd_f32(a, b)
        self.assertEqual(bits_to_hex32(res["res_bits"]), "0x3E99999A")  # 0.3000000119...
        self.assertTrue(res["flags"]["inexact"])

    def test_add_signed_zero_tie_gives_pos_zero(self):
        posz = hex32_to_bits_msb(PZERO)
        negz = hex32_to_bits_msb(NZERO)
        res = fadd_f32(posz, negz)
        self.assertEqual(bits_to_hex32(res["res_bits"]), "0x00000000")  # +0

    def test_add_alignment_trace_present(self):
        # 1.0 + MIN_NORM (exponents far apart) → result 1.0 with inexact due to sticky
        a = hex32_to_bits_msb(ONE)
        b = hex32_to_bits_msb(MIN_NORM)
        res = fadd_f32(a, b)
        self.assertEqual(bits_to_hex32(res["res_bits"]), "0x3F800000")
        self.assertTrue(res["flags"]["inexact"])
        self.assertTrue(any("ALIGN:" in t for t in res["trace"]))

    def test_add_overflow_to_inf(self):
        a = hex32_to_bits_msb(MAX_NORM)
        b = hex32_to_bits_msb(MAX_NORM)
        res = fadd_f32(a, b)
        self.assertTrue(res["flags"]["overflow"])
        self.assertEqual(bits_to_hex32(res["res_bits"]), "0x7F800000")  # +inf

    def test_add_subnormal_plus_subnormal_stays_subnormal_underflow(self):
        a = hex32_to_bits_msb(MIN_SUB)
        b = hex32_to_bits_msb(MIN_SUB)
        res = fadd_f32(a, b)
        # Still subnormal and exponent == 0 => underflow asserted by our FPU
        self.assertTrue(res["flags"]["underflow"])
        bits = res["res_bits"]
        self.assertTrue(all(not b for b in bits[1:9]))  # exp==0

    def test_add_subnormal_accumulate_to_min_normal(self):
        # (largest subnormal + smallest subnormal) = exactly MIN_NORMAL
        a = hex32_to_bits_msb(BIG_SUB)
        b = hex32_to_bits_msb(MIN_SUB)
        res = fadd_f32(a, b)
        self.assertEqual(bits_to_hex32(res["res_bits"]), "0x00800000")  # exact
        self.assertFalse(res["flags"]["inexact"])

    def test_sub_basic(self):
        a = hex32_to_bits_msb(THREE)  # 3.0
        b = hex32_to_bits_msb(ONE)    # 1.0
        res = fsub_f32(a, b)
        self.assertEqual(bits_to_hex32(res["res_bits"]), "0x40000000")  # 2.0

    def test_sub_cancellation_to_plus_zero(self):
        a = hex32_to_bits_msb(ONE)
        b = hex32_to_bits_msb(ONE)
        res = fsub_f32(a, b)
        self.assertEqual(bits_to_hex32(res["res_bits"]), "0x00000000")  # +0 exact
        self.assertFalse(res["flags"]["inexact"])

    def test_add_inf_plus_ninf_is_nan_invalid(self):
        pinf = hex32_to_bits_msb(PINF)
        ninf = hex32_to_bits_msb(NINF)
        res = fadd_f32(pinf, ninf)
        self.assertTrue(res["flags"]["invalid"])
        bits = res["res_bits"]
        self.assertTrue(all(bits[1:9]))   # exp all ones
        self.assertTrue(any(bits[9:]))    # fraction != 0

    def test_add_nan_operand_propagates_nan(self):
        qnan = hex32_to_bits_msb(QNAN)
        one  = hex32_to_bits_msb(ONE)
        res = fadd_f32(qnan, one)
        bits = res["res_bits"]
        self.assertTrue(all(bits[1:9]))   # exp all ones
        self.assertTrue(any(bits[9:]))    # fraction != 0
        # Our implementation does not set 'invalid' just for qNaN input
        self.assertFalse(res["flags"]["invalid"])

    def test_add_inf_same_sign(self):
        pinf = hex32_to_bits_msb(PINF)
        res = fadd_f32(pinf, pinf)
        self.assertEqual(bits_to_hex32(res["res_bits"]), "0x7F800000")
        self.assertFalse(res["flags"]["invalid"])

    def test_mul_simple(self):
        a = hex32_to_bits_msb(ONE_PT5)  # 1.5
        b = hex32_to_bits_msb(TWO)      # 2.0
        res = fmul_f32(a, b)
        self.assertEqual(bits_to_hex32(res["res_bits"]), "0x40400000")  # 3.0
        self.assertFalse(res["flags"]["overflow"])
        self.assertFalse(res["flags"]["underflow"])
        # Ensure the shift-add path ran
        self.assertTrue(any("OP: 24x24 shift-add multiplier" in t for t in res["trace"]))

    def test_mul_overflow_to_inf(self):
        max_norm = hex32_to_bits_msb(MAX_NORM)
        two      = hex32_to_bits_msb(TWO)
        res = fmul_f32(max_norm, two)
        self.assertTrue(res["flags"]["overflow"])
        self.assertEqual(bits_to_hex32(res["res_bits"]), "0x7F800000")  # +inf

    def test_mul_underflow_to_subnormal(self):
        # MIN_NORMAL * 0.5 = 2^-127 => subnormal 0x00400000
        a = hex32_to_bits_msb(MIN_NORM)
        b = hex32_to_bits_msb(HALF)
        res = fmul_f32(a, b)
        self.assertEqual(bits_to_hex32(res["res_bits"]), "0x00400000")
        self.assertTrue(res["flags"]["underflow"])

    def test_mul_zero_times_inf_is_nan_invalid(self):
        zero = hex32_to_bits_msb(PZERO)
        pinf = hex32_to_bits_msb(PINF)
        res = fmul_f32(zero, pinf)
        self.assertTrue(res["flags"]["invalid"])
        bits = res["res_bits"]
        self.assertTrue(all(bits[1:9]))
        self.assertTrue(any(bits[9:]))

    def test_mul_signed_zero(self):
        neg_zero = hex32_to_bits_msb(NZERO)
        two      = hex32_to_bits_msb(TWO)
        res = fmul_f32(neg_zero, two)
        self.assertEqual(bits_to_hex32(res["res_bits"]), "0x80000000")  # -0

    def test_mul_with_nan_operand_propagates(self):
        qnan = hex32_to_bits_msb(QNAN)
        two  = hex32_to_bits_msb(TWO)
        res = fmul_f32(qnan, two)
        bits = res["res_bits"]
        self.assertTrue(all(bits[1:9]))
        self.assertTrue(any(bits[9:]))    # NaN payload
        self.assertFalse(res["flags"]["invalid"])

    def test_add_commutativity_bits_match(self):
        a = hex32_to_bits_msb(ONE)
        b = hex32_to_bits_msb("41200000")  # 10.0
        r1 = fadd_f32(a, b)["res_bits"]
        r2 = fadd_f32(b, a)["res_bits"]
        self.assertEqual(bits_to_hex32(r1), bits_to_hex32(r2))

    def test_add_with_large_gap_rounds_away(self):
        # 1.0 + smallest subnormal => 1.0 (inexact)
        a = hex32_to_bits_msb(ONE)
        b = hex32_to_bits_msb(MIN_SUB)
        res = fadd_f32(a, b)
        self.assertEqual(bits_to_hex32(res["res_bits"]), "0x3F800000")
        self.assertTrue(res["flags"]["inexact"])