from __future__ import annotations
from typing import Tuple, List, Dict

from memory import Bit  # your Bit class
import gates as g       # your gate primitives

ZERO = Bit(False)
ONE  = Bit(True)

def xor_gate(a: Bit, b: Bit) -> Bit:
    # XOR = (a OR b) AND ~(a AND b)
    a_or_b = g.or_gate(a, b)
    a_and_b = g.and_gate(a, b)
    not_a_and_b = g.not_gate(a_and_b)
    return g.and_gate(a_or_b, not_a_and_b)

def and3(a: Bit, b: Bit, c: Bit) -> Bit:
    return g.and_gate(g.and_gate(a, b), c)

def or3(a: Bit, b: Bit, c: Bit) -> Bit:
    return g.or_gate(g.or_gate(a, b), c)

def zeros(n: int) -> Tuple[Bit, ...]:
    return tuple(ZERO for _ in range(n))

def ones(n: int) -> Tuple[Bit, ...]:
    return tuple(ONE for _ in range(n))

def one_hot_lsb(n: int) -> Tuple[Bit, ...]:
    # 00...001  (MSB-first)
    return tuple(ZERO for _ in range(n-1)) + (ONE,)

def bits_equal(a: Tuple[Bit, ...], b: Tuple[Bit, ...]) -> bool:
    neq = ZERO
    for i in range(len(a)):
        neq = g.or_gate(neq, xor_gate(a[i], b[i]))
    return not bool(neq)

def bits_all_zero(a: Tuple[Bit, ...]) -> bool:
    acc = ZERO
    for b in a:
        acc = g.or_gate(acc, b)
    return not bool(acc)

def vec_or(a: Tuple[Bit, ...]) -> Bit:
    acc = ZERO
    for b in a:
        acc = g.or_gate(acc, b)
    return acc

def unsigned_less_than(a: Tuple[Bit, ...], b: Tuple[Bit, ...]) -> bool:
    # Lexicographic MSB-first compare
    n = len(a)
    for i in range(n):
        ai, bi = bool(a[i]), bool(b[i])
        if ai != bi:
            return (not ai) and bi
    return False

def add_unsigned(a: Tuple[Bit, ...], b: Tuple[Bit, ...], cin: Bit = ZERO) -> Tuple[Tuple[Bit, ...], Bit]:
    assert len(a) == len(b)
    n = len(a)
    s: List[Bit] = [ZERO] * n
    carry = cin
    for i in range(n - 1, -1, -1):  # LSB -> MSB
        axb = xor_gate(a[i], b[i])
        sm = xor_gate(axb, carry)
        ab  = g.and_gate(a[i], b[i])
        cax = g.and_gate(carry, axb)
        cout = g.or_gate(ab, cax)
        s[i] = sm
        carry = cout
    return tuple(s), carry

def not_vec(a: Tuple[Bit, ...]) -> Tuple[Bit, ...]:
    return tuple(g.not_gate(x) for x in a)

def inc_unsigned(a: Tuple[Bit, ...]) -> Tuple[Tuple[Bit, ...], Bit]:
    return add_unsigned(a, one_hot_lsb(len(a)))

def dec_unsigned(a: Tuple[Bit, ...]) -> Tuple[Tuple[Bit, ...], Bit]:
    inv = not_vec(one_hot_lsb(len(a)))  # 11..110
    return add_unsigned(a, inv, ONE)    # a + (111..110) == a - 1

def sub_unsigned(a: Tuple[Bit, ...], b: Tuple[Bit, ...]) -> Tuple[Tuple[Bit, ...], Bit]:
    # a - b = a + (~b + 1)
    nb = not_vec(b)
    nb_plus_1, _ = inc_unsigned(nb)
    s, carry = add_unsigned(a, nb_plus_1)
    borrow = g.not_gate(carry)  # carry==1 ⇒ no borrow
    return s, borrow

def shl_logical(a: Tuple[Bit, ...], steps: int = 1) -> Tuple[Bit, ...]:
    out = list(a)
    for _ in range(steps):
        for i in range(len(out) - 1):
            out[i] = out[i + 1]
        out[-1] = ZERO
    return tuple(out)

def shr_logical(a: Tuple[Bit, ...], steps: int = 1) -> Tuple[Bit, ...]:
    out = list(a)
    for _ in range(steps):
        for i in range(len(out) - 1, 0, -1):
            out[i] = out[i - 1]
        out[0] = ZERO
    return tuple(out)

def shr_with_sticky_grs(mant_grs: Tuple[Bit, ...]) -> Tuple[Tuple[Bit, ...], Bit]:
    """
    Right shift by 1; the bit dropped from LSB is OR-ed into the last (sticky) bit.
    Input and output include G,R,S bits at the end of the vector.
    """
    out = list(mant_grs)
    dropped = out[-1]  # LSB before the shift
    for i in range(len(out) - 1, 0, -1):
        out[i] = out[i - 1]
    out[0] = ZERO
    out[-1] = g.or_gate(out[-1], dropped)  # accumulate sticky
    return tuple(out), out[-1]

BIAS_BITS = (ZERO, ONE, ONE, ONE, ONE, ONE, ONE, ONE)  # 127

def unpack_f32(bits32: Tuple[Bit, ...]) -> Tuple[Bit, Tuple[Bit, ...], Tuple[Bit, ...], str]:
    assert len(bits32) == 32
    s = bits32[0]
    e = bits32[1:9]
    f = bits32[9:32]
    # classify
    exp_all_zero = bits_all_zero(e)
    exp_all_one  = bits_all_zero(tuple(g.not_gate(b) for b in e))
    frac_zero    = bits_all_zero(f)
    if exp_all_one:
        klass = "inf" if frac_zero else "nan"
    elif exp_all_zero:
        klass = "zero" if frac_zero else "subnormal"
    else:
        klass = "normal"
    return s, e, f, klass

def pack_f32(sign: Bit, exp8: Tuple[Bit, ...], frac23: Tuple[Bit, ...]) -> Tuple[Bit, ...]:
    assert len(exp8) == 8 and len(frac23) == 23
    return (sign,) + exp8 + frac23

def make_qnan() -> Tuple[Bit, ...]:
    # canonical quiet-NaN: 0x7FC00000 -> s=0, exp=all 1s, frac MSB=1, rest 0
    return pack_f32(ZERO, ones(8), (ONE,) + tuple(ZERO for _ in range(22)))

def is_exp_all_ones(exp8: Tuple[Bit, ...]) -> bool:
    return bits_all_zero(tuple(g.not_gate(x) for x in exp8))

def is_exp_all_zeros(exp8: Tuple[Bit, ...]) -> bool:
    return bits_all_zero(exp8)

def mantissa24_with_hidden(exp8: Tuple[Bit, ...], frac23: Tuple[Bit, ...]) -> Tuple[Bit, ...]:
    # Hidden 1 for normal numbers, 0 for subnormal/zero
    hidden = ZERO if is_exp_all_zeros(exp8) else ONE
    return (hidden,) + frac23  # 24 bits

def extend_grs(mant24: Tuple[Bit, ...]) -> Tuple[Bit, ...]:
    # Append Guard, Round, Sticky = 0 initially
    return mant24 + (ZERO, ZERO, ZERO)  # 27 bits total

def extract_value_and_grs(m27: Tuple[Bit, ...]) -> Tuple[Tuple[Bit, ...], Bit, Bit, Bit]:
    assert len(m27) >= 4
    G = m27[-3]
    R = m27[-2]
    S = m27[-1]
    value24 = m27[:-3]
    return value24, G, R, S

def round_ties_to_even(value24: Tuple[Bit, ...],
                       G: Bit, R: Bit, S: Bit,
                       exp8: Tuple[Bit, ...]) -> Tuple[Tuple[Bit, ...], Tuple[Bit, ...], Bit]:
    """
    Round the 24-bit value using G,R,S (ties-to-even). Returns (rounded_value24, new_exp8, inexact_bit).
    If rounding overflows the 24-bit significand, it shifts right by 1 and increments exponent.
    """
    lsb = value24[-1]
    r_or_s = g.or_gate(R, S)
    up_cond = and3(G, g.or_gate(r_or_s, lsb), ONE)  # G && (R || S || LSB)
    inexact = g.or_gate(G, r_or_s)

    if bool(up_cond):
        rounded, carry = add_unsigned(value24, one_hot_lsb(len(value24)))
    else:
        rounded, carry = value24, ZERO

    if bool(carry):
        # shift right by 1 and increment exponent
        rounded = shr_logical(rounded, 1)
        exp8, _ = inc_unsigned(exp8)

    return rounded, exp8, inexact

def eff_exp_for_align(exp8: Tuple[Bit, ...]) -> Tuple[Bit, ...]:
    # For subnormals, effective exponent is 1 (so they can be aligned against normals)
    if is_exp_all_zeros(exp8):
        return one_hot_lsb(8)  # 00000001
    return exp8

def align_operands(a_e: Tuple[Bit, ...], a_m27: Tuple[Bit, ...],
                   b_e: Tuple[Bit, ...], b_m27: Tuple[Bit, ...],
                   trace: List[str]) -> Tuple[Tuple[Bit, ...], Tuple[Bit, ...], Tuple[Bit, ...], Tuple[Bit, ...]]:
    """
    Repeatedly right-shift the mantissa of the operand with the smaller exponent,
    incrementing that exponent, until exponents match. Sticky accumulates in m27's S.
    """
    ea = list(eff_exp_for_align(a_e))
    eb = list(eff_exp_for_align(b_e))
    ma = a_m27
    mb = b_m27

    # Limit iterations to 255 to avoid runaway loops (safe upper bound for exp diff)
    for _ in range(255):
        if bits_equal(tuple(ea), tuple(eb)):
            break

        if unsigned_less_than(tuple(ea), tuple(eb)):
            # shift A right with sticky
            ma, _ = shr_with_sticky_grs(ma)
            ea, _ = inc_unsigned(tuple(ea))
            trace.append("ALIGN: shift A >> 1, inc exp(A)")
        else:
            mb, _ = shr_with_sticky_grs(mb)
            eb, _ = inc_unsigned(tuple(eb))
            trace.append("ALIGN: shift B >> 1, inc exp(B)")

    return tuple(ea), ma, tuple(eb), mb

def addsub_core(a_bits: Tuple[Bit, ...], b_bits: Tuple[Bit, ...], subtract: bool) -> Dict[str, object]:
    trace: List[str] = []

    sA, eA, fA, kA = unpack_f32(a_bits)
    sB, eB, fB, kB = unpack_f32(b_bits)

    # NaN handling
    if kA == "nan" or kB == "nan":
        trace.append("SPECIAL: NaN operand → NaN")
        return {"res_bits": make_qnan(),
                "flags": {"overflow": False, "underflow": False, "invalid": False, "inexact": False, "divide_by_zero": False},
                "trace": trace}

    # For subtraction, invert sign of B
    if subtract:
        sB = g.not_gate(sB)
        trace.append("SUB: flipping sign of B")

    # Infinity handling
    if kA == "inf" and kB == "inf":
        if bool(xor_gate(sA, sB)):
            trace.append("SPECIAL: +∞ and −∞ → invalid")
            return {"res_bits": make_qnan(),
                    "flags": {"overflow": False, "underflow": False, "invalid": True, "inexact": False, "divide_by_zero": False},
                    "trace": trace}
        else:
            trace.append("SPECIAL: ∞ + ∞ (same sign) → ∞")
            return {"res_bits": pack_f32(sA, ones(8), zeros(23)),
                    "flags": {"overflow": False, "underflow": False, "invalid": False, "inexact": False, "divide_by_zero": False},
                    "trace": trace}

    if kA == "inf":
        trace.append("SPECIAL: A is ∞ → return ∞")
        return {"res_bits": pack_f32(sA, ones(8), zeros(23)),
                "flags": {"overflow": False, "underflow": False, "invalid": False, "inexact": False, "divide_by_zero": False},
                "trace": trace}
    if kB == "inf":
        trace.append("SPECIAL: B is ∞ → return ∞")
        return {"res_bits": pack_f32(sB, ones(8), zeros(23)),
                "flags": {"overflow": False, "underflow": False, "invalid": False, "inexact": False, "divide_by_zero": False},
                "trace": trace}

    # Zeros: handle signed zero tie as +0
    if kA == "zero" and kB == "zero":
        trace.append("SPECIAL: +0 and −0 → +0")
        return {"res_bits": pack_f32(ZERO, zeros(8), zeros(23)),
                "flags": {"overflow": False, "underflow": False, "invalid": False, "inexact": False, "divide_by_zero": False},
                "trace": trace}
    if kA == "zero" and kB != "zero":
        trace.append("SPECIAL: A=0 → return B")
        return {"res_bits": pack_f32(sB, eB, fB),
                "flags": {"overflow": False, "underflow": False, "invalid": False, "inexact": False, "divide_by_zero": False},
                "trace": trace}
    if kB == "zero" and kA != "zero":
        trace.append("SPECIAL: B=0 → return A")
        return {"res_bits": pack_f32(sA, eA, fA),
                "flags": {"overflow": False, "underflow": False, "invalid": False, "inexact": False, "divide_by_zero": False},
                "trace": trace}

    # Prepare mantissas (with hidden) and extend with GRS
    mA27 = extend_grs(mantissa24_with_hidden(eA, fA))
    mB27 = extend_grs(mantissa24_with_hidden(eB, fB))

    # Align exponents and mantissas via right shifts with sticky
    eA_eff, mA27, eB_eff, mB27 = align_operands(eA, mA27, eB, mB27, trace)

    # Determine result sign for add/sub: sign of larger magnitude
    if bits_equal(eA_eff, eB_eff):
        a_gt_b = unsigned_less_than(mB27[:-3], mA27[:-3])
        b_gt_a = unsigned_less_than(mA27[:-3], mB27[:-3])
    else:
        a_gt_b = unsigned_less_than(eB_eff, eA_eff)
        b_gt_a = not a_gt_b

    same_sign = not bool(xor_gate(sA, sB))
    op_is_add = same_sign

    # Mantissa operation
    if op_is_add:
        trace.append("OP: add significands")
        sum27, carry = add_unsigned(mA27, mB27)
        res_sign = sA  # same sign
        res_exp = eA_eff
        # Normalize if carry across MSB (value >= 2.0)
        if bool(carry):
            sum27, _ = shr_with_sticky_grs(sum27)
            res_exp, _ = inc_unsigned(res_exp)
            trace.append("NORMALIZE: carry → shift >>1, exp++")
        value24, G, R, S = extract_value_and_grs(sum27)
    else:
        # subtract smaller magnitude from larger
        if a_gt_b:
            big_m, sml_m = mA27, mB27
            res_sign = sA
            res_exp = eA_eff
            trace.append("OP: sub B from A (|A|>=|B|)")
        elif b_gt_a:
            big_m, sml_m = mB27, mA27
            res_sign = sB
            res_exp = eB_eff
            trace.append("OP: sub A from B (|B|>|A|)")
        else:
            # exact cancellation
            trace.append("OP: equal magnitudes with different signs → +0")
            return {"res_bits": pack_f32(ZERO, zeros(8), zeros(23)),
                    "flags": {"overflow": False, "underflow": False, "invalid": False, "inexact": False, "divide_by_zero": False},
                    "trace": trace}

        diff27, _borrow = sub_unsigned(big_m, sml_m)
        if bits_all_zero(diff27):
            trace.append("NORMALIZE: diff is zero → +0")
            return {"res_bits": pack_f32(ZERO, zeros(8), zeros(23)),
                    "flags": {"overflow": False, "underflow": False, "invalid": False, "inexact": False, "divide_by_zero": False},
                    "trace": trace}

        value24, G, R, S = extract_value_and_grs(diff27)
        # Normalize left until hidden '1' is restored or exponent hits 0
        while not bool(value24[0]) and not is_exp_all_zeros(res_exp):
            value24 = shl_logical(value24, 1)
            res_exp, _ = dec_unsigned(res_exp)
            trace.append("NORMALIZE: shift <<1, exp--")
        # If exponent becomes zero while leading bit still 0 -> subnormal

    # ROUND (ties to even)
    rounded24, res_exp, inexact = round_ties_to_even(value24, G, R, S, res_exp)

    # Pack with flags
    flags = {"overflow": False, "underflow": False, "invalid": False,
             "inexact": bool(inexact), "divide_by_zero": False}

    # Exponent overflow to all 1s → ±∞
    if is_exp_all_ones(res_exp):
        trace.append("PACK: exponent overflow → ±∞")
        flags["overflow"] = True
        flags["inexact"] = True or flags["inexact"]
        return {"res_bits": pack_f32(res_sign, ones(8), zeros(23)),
                "flags": flags, "trace": trace}

    # Underflow if exponent is zero (subnormal or zero after rounding)
    if is_exp_all_zeros(res_exp):
        if bool(or3(G, R, S)) or not bool(value24[0]):
            flags["underflow"] = True
            trace.append("PACK: exponent zero → subnormal/zero (underflow)")

    # Build fraction (drop hidden)
    frac23 = rounded24[1:]
    res_bits = pack_f32(res_sign, res_exp, frac23)
    trace.append("PACK: done")
    return {"res_bits": res_bits, "flags": flags, "trace": trace}

def fadd_f32(a_bits: Tuple[Bit, ...], b_bits: Tuple[Bit, ...]) -> Dict[str, object]:
    return addsub_core(a_bits, b_bits, subtract=False)

def fsub_f32(a_bits: Tuple[Bit, ...], b_bits: Tuple[Bit, ...]) -> Dict[str, object]:
    return addsub_core(a_bits, b_bits, subtract=True)

def add_into(acc: List[Bit], addend: Tuple[Bit, ...], lsb_offset: int) -> None:
    """
    acc: mutable 48-bit product vector (MSB-first)
    addend: 24-bit to add
    lsb_offset: how far from LSB to align addend's LSB (0 means align at LSB)
    """
    idx = len(acc) - 1 - lsb_offset
    carry = ZERO
    for j in range(len(addend) - 1, -1, -1):
        axb = xor_gate(acc[idx], addend[j])
        sm  = xor_gate(axb, carry)
        ab  = g.and_gate(acc[idx], addend[j])
        cax = g.and_gate(carry, axb)
        cout = g.or_gate(ab, cax)
        acc[idx] = sm
        carry = cout
        idx -= 1
    # propagate carry leftward if needed
    while bool(carry) and idx >= 0:
        axb = xor_gate(acc[idx], carry)
        sm  = axb
        carry = g.and_gate(acc[idx], carry)
        acc[idx] = sm
        idx -= 1

def mul_mantissas_24x24(a24: Tuple[Bit, ...], b24: Tuple[Bit, ...]) -> Tuple[Bit, ...]:
    """
    Shift-add multiplier for 24x24 -> 48 bits.
    a24, b24 are MSB-first (bit[0] is MSB, bit[23] is LSB)
    """
    prod = [ZERO for _ in range(48)]
    for i in range(24):              # iterate multiplier bits from LSB to MSB
        bbit = b24[-1 - i]
        if bool(bbit):
            add_into(prod, a24, i)
    return tuple(prod)

def normalize_product(prod48: Tuple[Bit, ...]) -> Tuple[Tuple[Bit, ...], Bit, Tuple[Bit, ...]]:
    """
    Returns (value24, carry_adjust_bit, grs_bits (G,R,S combined into 3-bits))
    If prod in [2,4) → take top 24 bits and set carry_adjust=1 (exp++).
    Else take next 24 bits. GRS from following bits; sticky is OR of rest.
    """
    if bool(prod48[0]):  # top bit set → [2,4)
        value24 = prod48[0:24]
        guard   = prod48[24] if len(prod48) > 24 else ZERO
        roundb  = prod48[25] if len(prod48) > 25 else ZERO
        sticky  = vec_or(prod48[26:]) if len(prod48) > 26 else ZERO
        return value24, ONE, (guard, roundb, sticky)
    else:  # [1,2)
        value24 = prod48[1:25]
        guard   = prod48[25] if len(prod48) > 25 else ZERO
        roundb  = prod48[26] if len(prod48) > 26 else ZERO
        sticky  = vec_or(prod48[27:]) if len(prod48) > 27 else ZERO
        return value24, ZERO, (guard, roundb, sticky)

def effective_exp_mul(exp8: Tuple[Bit, ...]) -> Tuple[Bit, ...]:
    # For subnormal, use 1 as effective exponent
    return one_hot_lsb(8) if is_exp_all_zeros(exp8) else exp8

def fmul_f32(a_bits: Tuple[Bit, ...], b_bits: Tuple[Bit, ...]) -> Dict[str, object]:
    trace: List[str] = []

    sA, eA, fA, kA = unpack_f32(a_bits)
    sB, eB, fB, kB = unpack_f32(b_bits)

    # NaN handling
    if kA == "nan" or kB == "nan":
        trace.append("SPECIAL: NaN operand → NaN")
        return {"res_bits": make_qnan(),
                "flags": {"overflow": False, "underflow": False, "invalid": False, "inexact": False, "divide_by_zero": False},
                "trace": trace}

    # INF and zero special cases
    if kA == "inf" or kB == "inf":
        if kA == "zero" or kB == "zero":
            trace.append("SPECIAL: 0 · ∞ → invalid")
            return {"res_bits": make_qnan(),
                    "flags": {"overflow": False, "underflow": False, "invalid": True, "inexact": False, "divide_by_zero": False},
                    "trace": trace}
        s = xor_gate(sA, sB)
        trace.append("SPECIAL: finite · ∞ → ∞")
        return {"res_bits": pack_f32(s, ones(8), zeros(23)),
                "flags": {"overflow": False, "underflow": False, "invalid": False, "inexact": False, "divide_by_zero": False},
                "trace": trace}

    if kA == "zero" or kB == "zero":
        trace.append("SPECIAL: multiplicand or multiplier is zero → signed zero")
        s = xor_gate(sA, sB)
        return {"res_bits": pack_f32(s, zeros(8), zeros(23)),
                "flags": {"overflow": False, "underflow": False, "invalid": False, "inexact": False, "divide_by_zero": False},
                "trace": trace}

    # Signs: XOR
    sR = xor_gate(sA, sB)

    # Effective exponents and significands with hidden
    eAeff = effective_exp_mul(eA)
    eBeff = effective_exp_mul(eB)
    mA24 = mantissa24_with_hidden(eA, fA)
    mB24 = mantissa24_with_hidden(eB, fB)

    # Exponent sum (9 bits): eAeff + eBeff
    zA = (ZERO,) + eAeff
    zB = (ZERO,) + eBeff
    sum9, _ = add_unsigned(zA, zB)

    # Subtract bias (127) from sum9
    bias9 = (ZERO,) + BIAS_BITS
    exp9, _borrow = sub_unsigned(sum9, bias9)  # 9-bit biased exponent

    trace.append("OP: 24x24 shift-add multiplier")
    prod48 = mul_mantissas_24x24(mA24, mB24)

    # Normalize product and prepare GRS
    val24, adjust, (G, R, S) = normalize_product(prod48)
    if bool(adjust):
        trace.append("NORMALIZE: product in [2,4) → exp++")
        exp9, _ = inc_unsigned(exp9)

    # Rounding
    exp8 = exp9[1:]  # drop top bit; if it becomes all ones after rounding, it's overflow
    rounded24, exp8, inexact = round_ties_to_even(val24, G, R, S, exp8)

    flags = {"overflow": False, "underflow": False, "invalid": False, "inexact": bool(inexact), "divide_by_zero": False}

    # Exponent overflow
    if is_exp_all_ones(exp8):
        trace.append("PACK: exponent overflow → ±∞")
        flags["overflow"] = True
        flags["inexact"] = True or flags["inexact"]
        return {"res_bits": pack_f32(sR, ones(8), zeros(23)), "flags": flags, "trace": trace}

    # Underflow (subnormal after rounding)
    if is_exp_all_zeros(exp8):
        if bool(or3(G, R, S)):
            flags["underflow"] = True
            trace.append("PACK: underflow to subnormal/zero")

    frac23 = rounded24[1:]
    res_bits = pack_f32(sR, exp8, frac23)
    trace.append("PACK: done")
    return {"res_bits": res_bits, "flags": flags, "trace": trace}