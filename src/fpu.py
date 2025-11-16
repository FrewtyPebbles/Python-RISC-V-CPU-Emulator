from __future__ import annotations
from typing import Tuple, List, Dict

from memory import Bit
import gates as g

Bits = Tuple[Bit, ...]


class FPU32:
    ZERO = Bit(False)
    ONE  = Bit(True)

    EXP_BITS  = 8
    FRAC_BITS = 23
    MANT_BITS = 24  # includes hidden bit
    GRS_BITS  = 3
    EXT_BITS  = MANT_BITS + GRS_BITS  # 27

    # 127 = 0b01111111 (MSB-first)
    BIAS_BITS = (Bit(False), Bit(True), Bit(True), Bit(True), Bit(True), Bit(True), Bit(True), Bit(True))

    EXP_ALL_ONES  = (Bit(True),)  * EXP_BITS
    EXP_ALL_ZEROS = (Bit(False),) * EXP_BITS

    def unpack_f32(self, bits32: Bits) -> Tuple[Bit, Bits, Bits, str]:
        """Return (sign, exp8, frac23, klass: 'zero'|'subnormal'|'normal'|'inf'|'nan')."""
        assert len(bits32) == 32
        s = bits32[0]
        e = bits32[1:1 + self.EXP_BITS]
        f = bits32[1 + self.EXP_BITS:32]

        exp_all_zero = self._bits_all_zero(e)
        exp_all_one  = self._bits_all_zero(tuple(g.not_gate(b) for b in e))
        frac_zero    = self._bits_all_zero(f)

        if exp_all_one:
            klass = "inf" if frac_zero else "nan"
        elif exp_all_zero:
            klass = "zero" if frac_zero else "subnormal"
        else:
            klass = "normal"
        return s, e, f, klass

    def pack_f32(self, sign: Bit, exp8: Bits, frac23: Bits) -> Bits:
        assert len(exp8) == self.EXP_BITS and len(frac23) == self.FRAC_BITS
        return (sign,) + exp8 + frac23

    def add(self, a_bits: Bits, b_bits: Bits) -> Dict[str, object]:
        return self._addsub_core(a_bits, b_bits, subtract=False)

    def sub(self, a_bits: Bits, b_bits: Bits) -> Dict[str, object]:
        return self._addsub_core(a_bits, b_bits, subtract=True)

    def mul(self, a_bits: Bits, b_bits: Bits) -> Dict[str, object]:
        trace: List[str] = []

        sA, eA, fA, kA = self.unpack_f32(a_bits)
        sB, eB, fB, kB = self.unpack_f32(b_bits)

        # NaN
        if kA == "nan" or kB == "nan":
            trace.append("SPECIAL: NaN operand → NaN")
            return {"res_bits": self._make_qnan(),
                    "flags": {"overflow": False, "underflow": False, "invalid": False, "inexact": False, "divide_by_zero": False},
                    "trace": trace}

        # INF / zero
        if kA == "inf" or kB == "inf":
            if kA == "zero" or kB == "zero":
                trace.append("SPECIAL: 0 · ∞ → invalid")
                return {"res_bits": self._make_qnan(),
                        "flags": {"overflow": False, "underflow": False, "invalid": True, "inexact": False, "divide_by_zero": False},
                        "trace": trace}
            s = g.xor_gate(sA, sB)
            trace.append("SPECIAL: finite · ∞ → ∞")
            return {"res_bits": self.pack_f32(s, self.EXP_ALL_ONES, self._zeros(self.FRAC_BITS)),
                    "flags": {"overflow": False, "underflow": False, "invalid": False, "inexact": False, "divide_by_zero": False},
                    "trace": trace}

        if kA == "zero" or kB == "zero":
            s = g.xor_gate(sA, sB)
            trace.append("SPECIAL: multiplicand or multiplier is zero → signed zero")
            return {"res_bits": self.pack_f32(s, self.EXP_ALL_ZEROS, self._zeros(self.FRAC_BITS)),
                    "flags": {"overflow": False, "underflow": False, "invalid": False, "inexact": False, "divide_by_zero": False},
                    "trace": trace}

        # Signs: XOR
        sR = g.xor_gate(sA, sB)

        # Effective exponents and significands with hidden
        eAeff = self._effective_exp_mul(eA)
        eBeff = self._effective_exp_mul(eB)
        mA24  = self._mantissa24_with_hidden(eA, fA)
        mB24  = self._mantissa24_with_hidden(eB, fB)

        # 24x24 → 48 product via shift-add
        trace.append("OP: 24x24 shift-add multiplier")
        prod48 = self._mul_mantissas_24x24(mA24, mB24, trace)

        # Exponent sum (9 bits) and subtract bias (127)
        zA = (self.ZERO,) + eAeff
        zB = (self.ZERO,) + eBeff
        sum9, _ = self._add_unsigned(zA, zB)
        bias9    = (self.ZERO,) + self.BIAS_BITS
        exp9, _b = self._sub_unsigned(sum9, bias9)

        # Normalize product and prepare GRS
        val24, adjust, (G, R, S) = self._normalize_product(prod48)
        if bool(adjust):
            exp9, _ = self._inc_unsigned(exp9)
            trace.append("NORMALIZE: product in [2,4) → exp++")

        # Convert to 8-bit exponent (drop top bit)
        exp8 = exp9[1:]

        # Round-to-nearest-even
        rounded24, exp8, inexact = self._round_ties_to_even(val24, G, R, S, exp8)

        flags = {"overflow": False, "underflow": False, "invalid": False, "inexact": bool(inexact), "divide_by_zero": False}

        # Overflow → ±∞
        if self._is_exp_all_ones(exp8):
            trace.append("PACK: exponent overflow → ±∞")
            flags["overflow"] = True
            flags["inexact"]  = True or flags["inexact"]
            return {"res_bits": self.pack_f32(sR, self.EXP_ALL_ONES, self._zeros(self.FRAC_BITS)),
                    "flags": flags, "trace": trace}

        # Underflow if exponent field is zero (subnormal/zero), even if exact
        if self._is_exp_all_zeros(exp8):
            flags["underflow"] = True
            trace.append("PACK: subnormal/zero result (underflow)")

        # Pack: normals drop hidden bit; subnormals keep top 23 (no hidden 1)
        if self._is_exp_all_zeros(exp8):
            frac23 = rounded24[0:23]   # include would-be hidden bit
        else:
            frac23 = rounded24[1:]     # drop hidden bit

        res_bits = self.pack_f32(sR, exp8, frac23)
        trace.append("PACK: done")
        return {"res_bits": res_bits, "flags": flags, "trace": trace}


    def _addsub_core(self, a_bits: Bits, b_bits: Bits, subtract: bool) -> Dict[str, object]:
        trace: List[str] = []

        sA, eA, fA, kA = self.unpack_f32(a_bits)
        sB, eB, fB, kB = self.unpack_f32(b_bits)

        # NaN
        if kA == "nan" or kB == "nan":
            trace.append("SPECIAL: NaN operand → NaN")
            return {"res_bits": self._make_qnan(),
                    "flags": {"overflow": False, "underflow": False, "invalid": False, "inexact": False, "divide_by_zero": False},
                    "trace": trace}

        # For subtraction, flip sign of B
        if subtract:
            sB = g.not_gate(sB)
            trace.append("SUB: flipping sign of B")

        # Infinities
        if kA == "inf" and kB == "inf":
            if bool(g.xor_gate(sA, sB)):
                trace.append("SPECIAL: +∞ and −∞ → invalid")
                return {"res_bits": self._make_qnan(),
                        "flags": {"overflow": False, "underflow": False, "invalid": True, "inexact": False, "divide_by_zero": False},
                        "trace": trace}
            trace.append("SPECIAL: ∞ + ∞ (same sign) → ∞")
            return {"res_bits": self.pack_f32(sA, self.EXP_ALL_ONES, self._zeros(self.FRAC_BITS)),
                    "flags": {"overflow": False, "underflow": False, "invalid": False, "inexact": False, "divide_by_zero": False},
                    "trace": trace}

        if kA == "inf":
            trace.append("SPECIAL: A is ∞ → return ∞")
            return {"res_bits": self.pack_f32(sA, self.EXP_ALL_ONES, self._zeros(self.FRAC_BITS)),
                    "flags": {"overflow": False, "underflow": False, "invalid": False, "inexact": False, "divide_by_zero": False},
                    "trace": trace}
        if kB == "inf":
            trace.append("SPECIAL: B is ∞ → return ∞")
            return {"res_bits": self.pack_f32(sB, self.EXP_ALL_ONES, self._zeros(self.FRAC_BITS)),
                    "flags": {"overflow": False, "underflow": False, "invalid": False, "inexact": False, "divide_by_zero": False},
                    "trace": trace}

        # zeros
        if kA == "zero" and kB == "zero":
            trace.append("SPECIAL: +0 and −0 → +0")
            return {"res_bits": self.pack_f32(self.ZERO, self.EXP_ALL_ZEROS, self._zeros(self.FRAC_BITS)),
                    "flags": {"overflow": False, "underflow": False, "invalid": False, "inexact": False, "divide_by_zero": False},
                    "trace": trace}
        if kA == "zero" and kB != "zero":
            trace.append("SPECIAL: A=0 → return B")
            return {"res_bits": self.pack_f32(sB, eB, fB),
                    "flags": {"overflow": False, "underflow": False, "invalid": False, "inexact": False, "divide_by_zero": False},
                    "trace": trace}
        if kB == "zero" and kA != "zero":
            trace.append("SPECIAL: B=0 → return A")
            return {"res_bits": self.pack_f32(sA, eA, fA),
                    "flags": {"overflow": False, "underflow": False, "invalid": False, "inexact": False, "divide_by_zero": False},
                    "trace": trace}

        # Prepare extended significands (with hidden and GRS)
        mA27 = self._extend_grs(self._mantissa24_with_hidden(eA, fA))
        mB27 = self._extend_grs(self._mantissa24_with_hidden(eB, fB))

        # Align exponents and mantissas via right shifts with sticky
        eA_eff, mA27, eB_eff, mB27 = self._align_operands(eA, mA27, eB, mB27, trace)

        # Determine sign/magnitude relation
        if self._bits_equal(eA_eff, eB_eff):
            a_gt_b = self._unsigned_less_than(mB27[:-3], mA27[:-3])
            b_gt_a = self._unsigned_less_than(mA27[:-3], mB27[:-3])
        else:
            a_gt_b = self._unsigned_less_than(eB_eff, eA_eff)
            b_gt_a = not a_gt_b

        same_sign = not bool(g.xor_gate(sA, sB))
        op_is_add = same_sign

        if op_is_add:
            trace.append("OP: add significands")
            sum27, carry = self._add_unsigned(mA27, mB27)
            res_sign = sA
            res_exp  = eA_eff

            # Correct carry handling: inject carry, shift >>1 with sticky, drop back to 27, exp++
            if bool(carry): 
                sum28 = (carry,) + sum27
                sh, _ = self._shr_with_sticky_grs(sum28)
                sum27 = sh[1:]
                res_exp, _ = self._inc_unsigned(res_exp)
                trace.append("NORMALIZE: carry → shift >>1 with carry injected, exp++")

            value24, G, R, S = self._extract_value_and_grs(sum27)

            if (not bool(value24[0])) and (not self._is_exp_all_zeros(res_exp)):
                res_exp = self.EXP_ALL_ZEROS
                trace.append("NORMALIZE: result < 1.0 with exp>0 → force subnormal (exp=0)")

        else:
            # subtraction of magnitudes
            if a_gt_b:
                big_m, sml_m = mA27, mB27
                res_sign = sA; res_exp = eA_eff
                trace.append("OP: sub B from A (|A|>=|B|)")
            elif b_gt_a:
                big_m, sml_m = mB27, mA27
                res_sign = sB; res_exp = eB_eff
                trace.append("OP: sub A from B (|B|>|A|)")
            else:
                trace.append("OP: equal magnitudes with different signs → +0")
                return {"res_bits": self.pack_f32(self.ZERO, self.EXP_ALL_ZEROS, self._zeros(self.FRAC_BITS)),
                        "flags": {"overflow": False, "underflow": False, "invalid": False, "inexact": False, "divide_by_zero": False},
                        "trace": trace}

            diff27, _borrow = self._sub_unsigned(big_m, sml_m)
            if self._bits_all_zero(diff27):
                trace.append("NORMALIZE: diff is zero → +0")
                return {"res_bits": self.pack_f32(self.ZERO, self.EXP_ALL_ZEROS, self._zeros(self.FRAC_BITS)),
                        "flags": {"overflow": False, "underflow": False, "invalid": False, "inexact": False, "divide_by_zero": False},
                        "trace": trace}

            value24, G, R, S = self._extract_value_and_grs(diff27)
            while not bool(value24[0]) and not self._is_exp_all_zeros(res_exp):
                value24   = self._shl_logical(value24, 1)
                res_exp, _ = self._dec_unsigned(res_exp)
                trace.append("NORMALIZE: shift <<1, exp--")

        # Round (RNE)
        rounded24, res_exp, inexact = self._round_ties_to_even(value24, G, R, S, res_exp)

        flags = {"overflow": False, "underflow": False, "invalid": False,
                 "inexact": bool(inexact), "divide_by_zero": False}

        if self._is_exp_all_ones(res_exp):
            trace.append("PACK: exponent overflow → ±∞")
            flags["overflow"] = True
            flags["inexact"]  = True or flags["inexact"]
            return {"res_bits": self.pack_f32(res_sign, self.EXP_ALL_ONES, self._zeros(self.FRAC_BITS)),
                    "flags": flags, "trace": trace}

        if self._is_exp_all_zeros(res_exp):
            if bool(g.or3_gate(G, R, S)) or not bool(value24[0]):
                flags["underflow"] = True
                trace.append("PACK: exponent zero → subnormal/zero (underflow)")

        frac23  = rounded24[1:]
        res_bits = self.pack_f32(res_sign, res_exp, frac23)
        trace.append("PACK: done")
        return {"res_bits": res_bits, "flags": flags, "trace": trace}

    def _zeros(self, n: int) -> Bits:
        return tuple(self.ZERO for _ in range(n))

    def _one_hot_lsb(self, n: int) -> Bits:
        return tuple(self.ZERO for _ in range(n - 1)) + (self.ONE,)

    def _bits_equal(self, a: Bits, b: Bits) -> bool:
        neq = self.ZERO
        for i in range(len(a)):
            neq = g.or_gate(neq, g.xor_gate(a[i], b[i]))
        return not bool(neq)

    def _bits_all_zero(self, a: Bits) -> bool:
        acc = self.ZERO
        for b in a:
            acc = g.or_gate(acc, b)
        return not bool(acc)

    def _vec_or(self, a: Bits) -> Bit:
        acc = self.ZERO
        for b in a:
            acc = g.or_gate(acc, b)
        return acc

    def _unsigned_less_than(self, a: Bits, b: Bits) -> bool:
        for i in range(len(a)):
            ai, bi = bool(a[i]), bool(b[i])
            if ai != bi:
                return (not ai) and bi
        return False

    def _add_unsigned(self, a: Bits, b: Bits, cin: Bit = None) -> Tuple[Bits, Bit]:
        assert len(a) == len(b)
        cin = cin if cin is not None else self.ZERO
        n = len(a); s: List[Bit] = [self.ZERO] * n
        carry = cin
        for i in range(n - 1, -1, -1):
            axb = g.xor_gate(a[i], b[i])
            sm  = g.xor_gate(axb, carry)
            ab  = g.and_gate(a[i], b[i])
            cax = g.and_gate(carry, axb)
            cout = g.or_gate(ab, cax)
            s[i] = sm; carry = cout
        return tuple(s), carry

    def _not_vec(self, a: Bits) -> Bits:
        return tuple(g.not_gate(x) for x in a)

    def _inc_unsigned(self, a: Bits) -> Tuple[Bits, Bit]:
        return self._add_unsigned(a, self._one_hot_lsb(len(a)))

    def _dec_unsigned(self, a: Bits) -> Tuple[Bits, Bit]:
        inv = self._not_vec(self._one_hot_lsb(len(a)))
        return self._add_unsigned(a, inv, self.ONE)

    def _sub_unsigned(self, a: Bits, b: Bits) -> Tuple[Bits, Bit]:
        nb = self._not_vec(b)
        nb_plus_1, _ = self._inc_unsigned(nb)
        s, carry = self._add_unsigned(a, nb_plus_1)
        borrow = g.not_gate(carry)  # carry==1 ⇒ no borrow
        return s, borrow

    def _shl_logical(self, a: Bits, steps: int = 1) -> Bits:
        out = list(a)
        for _ in range(steps):
            for i in range(len(out) - 1):
                out[i] = out[i + 1]
            out[-1] = self.ZERO
        return tuple(out)

    def _shr_logical(self, a: Bits, steps: int = 1) -> Bits:
        out = list(a)
        for _ in range(steps):
            for i in range(len(out) - 1, 0, -1):
                out[i] = out[i - 1]
            out[0] = self.ZERO
        return tuple(out)

    def _shr_with_sticky_grs(self, mant_grs: Bits) -> Tuple[Bits, Bit]:
        """
        Shift right by 1 on [mantissa24 | G | R | S], accumulating sticky: new_S = old_R OR old_S.
        """
        out = list(mant_grs)
        dropped = out[-1]  # old S
        for i in range(len(out) - 1, 0, -1):
            out[i] = out[i - 1]
        out[0] = self.ZERO
        out[-1] = g.or_gate(out[-1], dropped)  # new S = old R OR old S
        return tuple(out), out[-1]

    def _make_qnan(self) -> Bits:
        # 0x7FC00000: sign=0, exp=all 1s, frac MSB=1
        return self.pack_f32(self.ZERO, self.EXP_ALL_ONES, (self.ONE,) + self._zeros(self.FRAC_BITS - 1))

    def _is_exp_all_ones(self, exp8: Bits) -> bool:
        return self._bits_all_zero(tuple(g.not_gate(x) for x in exp8))

    def _is_exp_all_zeros(self, exp8: Bits) -> bool:
        return self._bits_all_zero(exp8)

    def _mantissa24_with_hidden(self, exp8: Bits, frac23: Bits) -> Bits:
        hidden = self.ZERO if self._is_exp_all_zeros(exp8) else self.ONE
        return (hidden,) + frac23  # 24 bits

    def _extend_grs(self, mant24: Bits) -> Bits:
        return mant24 + (self.ZERO, self.ZERO, self.ZERO)

    def _extract_value_and_grs(self, m27: Bits) -> Tuple[Bits, Bit, Bit, Bit]:
        G = m27[-3]; R = m27[-2]; S = m27[-1]
        value24 = m27[:-3]
        return value24, G, R, S
    
    def _round_ties_to_even(self, value24: Bits, G: Bit, R: Bit, S: Bit, exp8: Bits) -> Tuple[Bits, Bits, Bit]:
        lsb    = value24[-1]
        r_or_s = g.or_gate(R, S)
        up_cond = g.and3_gate(G, g.or_gate(r_or_s, lsb), self.ONE)  # G && (R || S || LSB)
        inexact = g.or_gate(G, r_or_s)

        if bool(up_cond):
            rounded, carry = self._add_unsigned(value24, self._one_hot_lsb(len(value24)))
        else:
            rounded, carry = value24, self.ZERO

        if bool(carry):
            rounded = self._shr_logical(rounded, 1)
            exp8, _ = self._inc_unsigned(exp8)

        return rounded, exp8, inexact

    def _eff_exp_for_align(self, exp8: Bits) -> Bits:
        return self._one_hot_lsb(8) if self._is_exp_all_zeros(exp8) else exp8

    def _align_operands(self, a_e: Bits, a_m27: Bits, b_e: Bits, b_m27: Bits, trace: List[str]) -> Tuple[Bits, Bits, Bits, Bits]:
        ea = list(self._eff_exp_for_align(a_e))
        eb = list(self._eff_exp_for_align(b_e))
        ma = a_m27
        mb = b_m27

        for _ in range(255):  # safe cap
            if self._bits_equal(tuple(ea), tuple(eb)):
                break
            if self._unsigned_less_than(tuple(ea), tuple(eb)):
                ma, _ = self._shr_with_sticky_grs(ma)
                ea, _ = self._inc_unsigned(tuple(ea))
                trace.append("ALIGN: shift A >> 1, inc exp(A)")
            else:
                mb, _ = self._shr_with_sticky_grs(mb)
                eb, _ = self._inc_unsigned(tuple(eb))
                trace.append("ALIGN: shift B >> 1, inc exp(B)")

        return tuple(ea), ma, tuple(eb), mb

    def _add_into(self, acc: List[Bit], addend: Bits, lsb_offset: int) -> None:
        idx = len(acc) - 1 - lsb_offset
        carry = self.ZERO
        for j in range(len(addend) - 1, -1, -1):
            axb = g.xor_gate(acc[idx], addend[j])
            sm  = g.xor_gate(axb, carry)
            ab  = g.and_gate(acc[idx], addend[j])
            cax = g.and_gate(carry, axb)
            cout = g.or_gate(ab, cax)
            acc[idx] = sm; carry = cout
            idx -= 1
        while bool(carry) and idx >= 0:
            axb = g.xor_gate(acc[idx], carry)
            sm  = axb
            carry = g.and_gate(acc[idx], carry)
            acc[idx] = sm
            idx -= 1

    def _mul_mantissas_24x24(self, a24: Bits, b24: Bits, trace: List[str]) -> Bits:
        prod = [self.ZERO for _ in range(48)]
        multiplier = b24
        multiplicand = a24  # aligned by offset in _add_into
        for i in range(24):      # iterate from LSB of multiplier
            bbit = multiplier[-1]
            if bool(bbit):
                self._add_into(prod, multiplicand, i)
                trace.append(f"MUL step{i}: add")
            multiplier = self._shr_logical(multiplier, 1)
        return tuple(prod)

    def _normalize_product(self, prod48: Bits) -> Tuple[Bits, Bit, Tuple[Bit, Bit, Bit]]:
        if bool(prod48[0]):  # [2,4)
            value24 = prod48[0:24]
            guard   = prod48[24] if len(prod48) > 24 else self.ZERO
            roundb  = prod48[25] if len(prod48) > 25 else self.ZERO
            sticky  = self._vec_or(prod48[26:]) if len(prod48) > 26 else self.ZERO
            return value24, self.ONE, (guard, roundb, sticky)
        else:                 # [1,2)
            value24 = prod48[1:25]
            guard   = prod48[25] if len(prod48) > 25 else self.ZERO
            roundb  = prod48[26] if len(prod48) > 26 else self.ZERO
            sticky  = self._vec_or(prod48[27:]) if len(prod48) > 27 else self.ZERO
            return value24, self.ZERO, (guard, roundb, sticky)

    def _effective_exp_mul(self, exp8: Bits) -> Bits:
        return self._one_hot_lsb(8) if self._is_exp_all_zeros(exp8) else exp8


_default_fpu = FPU32()

def fadd_f32(a_bits: Bits, b_bits: Bits) -> Dict[str, object]:
    return _default_fpu.add(a_bits, b_bits)

def fsub_f32(a_bits: Bits, b_bits: Bits) -> Dict[str, object]:
    return _default_fpu.sub(a_bits, b_bits)

def fmul_f32(a_bits: Bits, b_bits: Bits) -> Dict[str, object]:
    return _default_fpu.mul(a_bits, b_bits)

def unpack_f32(bits32: Bits):
    return _default_fpu.unpack_f32(bits32)

def pack_f32(sign: Bit, exp8: Bits, frac23: Bits) -> Bits:
    return _default_fpu.pack_f32(sign, exp8, frac23)
