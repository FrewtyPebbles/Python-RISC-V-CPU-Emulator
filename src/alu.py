from __future__ import annotations
from typing import Tuple, Dict, List

from memory import Bit
import gates as g

Bits32 = Tuple[Bit, ...]


class ALU32:
    """
    32-bit ALU operating purely on Bit vectors and gate primitives.
    Supported ops: ADD, SUB, SLL, SRL, SRA
    Outputs: result, flags (N,Z,C,V)
    - N: result MSB
    - Z: all result bits zero
    - C: carry-out of MSB for the adder (for SUB: 1 means 'no borrow')
    - V: signed overflow (two's-complement)
    """

    def __init__(self):
        self._ZERO = Bit(False)
        self._ONE  = Bit(True)

    def exec(self, a: Bits32, b: Bits32, op: str) -> Dict[str, object]:
        op = op.upper()
        if op == "ADD":
            return self._op_add(a, b)
        elif op == "SUB":
            return self._op_sub(a, b)
        elif op == "SLL":
            return self._op_sll(a, b)
        elif op == "SRL":
            return self._op_srl(a, b)
        elif op == "SRA":
            return self._op_sra(a, b)
        else:
            raise ValueError(f"Unsupported ALU op '{op}'")
        
    def _zeros(self, n: int) -> Tuple[Bit, ...]:
        return tuple(self._ZERO for _ in range(n))

    def _bits_all_zero(self, bits: Tuple[Bit, ...]) -> bool:
        acc = self._ZERO
        for b in bits:
            acc = g.or_gate(acc, b)
        return not bool(acc)

    def _mux_vec(self, a: Bits32, b: Bits32, sel: Bit) -> Bits32:
        """Vector 2:1 mux (MSB-first)."""
        assert len(a) == len(b)
        out: List[Bit] = []
        for i in range(len(a)):
            out.append(g.mux_gate(a[i], b[i], sel))
        return tuple(out)

    def _full_adder(self, a: Bit, b: Bit, cin: Bit) -> Tuple[Bit, Bit]:
        """
        sum = a XOR b XOR cin
        cout = (a AND b) OR (cin AND (a XOR b))
        """
        axb = g.xor_gate(a, b)
        s   = g.xor_gate(axb, cin)
        ab  = g.and_gate(a, b)
        cax = g.and_gate(cin, axb)
        cout = g.or_gate(ab, cax)
        return s, cout

    def _add_unsigned(self, a: Bits32, b: Bits32, cin: Bit = None) -> Tuple[Bits32, Bit]:
        assert len(a) == 32 and len(b) == 32
        cin = cin if cin is not None else self._ZERO
        s: List[Bit] = [self._ZERO] * 32
        carry = cin
        # LSB -> MSB (MSB-first vector, so walk right-to-left)
        for i in range(31, -1, -1):
            s[i], carry = self._full_adder(a[i], b[i], carry)
        return tuple(s), carry

    def _not_vec(self, v: Bits32) -> Bits32:
        return tuple(g.not_gate(x) for x in v)

    def _one_hot_lsb(self) -> Bits32:
        # 31 zeros followed by one 1 (MSB-first)
        return self._zeros(31) + (self._ONE,)

    def _shl1(self, x: Bits32) -> Bits32:
        # shift-left logical by 1 (MSB-first)
        out = list(x)
        for i in range(31):
            out[i] = out[i + 1]
        out[31] = self._ZERO
        return tuple(out)

    def _shr1(self, x: Bits32) -> Bits32:
        # shift-right logical by 1 (MSB-first)
        out = list(x)
        for i in range(31, 0, -1):
            out[i] = out[i - 1]
        out[0] = self._ZERO
        return tuple(out)

    def _sra1(self, x: Bits32) -> Bits32:
        # shift-right arithmetic by 1 (replicate sign bit)
        sign = x[0]
        out = list(x)
        for i in range(31, 0, -1):
            out[i] = out[i - 1]
        out[0] = sign
        return tuple(out)

    def _shl_n(self, x: Bits32, n: int) -> Bits32:
        out = x
        for _ in range(n):
            out = self._shl1(out)
        return out

    def _shr_n(self, x: Bits32, n: int) -> Bits32:
        out = x
        for _ in range(n):
            out = self._shr1(out)
        return out

    def _sra_n(self, x: Bits32, n: int) -> Bits32:
        out = x
        for _ in range(n):
            out = self._sra1(out)
        return out

    def _barrel_with_rs2(self, x: Bits32, rs2: Bits32, mode: str) -> Bits32:
        """
        Shift by the lower 5 bits of rs2 (MSB-first vector).
        We build a barrel shifter with stages 1,2,4,8,16 using muxes.
        mode: 'SLL' | 'SRL' | 'SRA'
        """
        stages = (1, 2, 4, 8, 16)
        ctrl_bits = (rs2[31], rs2[30], rs2[29], rs2[28], rs2[27])  # LSB..bit4 (MSB-first)
        cur = x
        for k, bit in zip(stages, ctrl_bits):
            if mode == "SLL":
                cand = self._shl_n(cur, k)
            elif mode == "SRL":
                cand = self._shr_n(cur, k)
            elif mode == "SRA":
                cand = self._sra_n(cur, k)
            else:
                raise ValueError("bad mode")
            # cur = bit ? cand : cur
            cur = self._mux_vec(cur, cand, bit)
        return cur

    # ----- flag helpers -----

    def _flag_N(self, res: Bits32) -> Bit:
        return res[0]

    def _flag_Z(self, res: Bits32) -> Bit:
        return self._ONE if self._bits_all_zero(res) else self._ZERO

    def _flag_V_add(self, a: Bits32, b: Bits32, r: Bits32) -> Bit:
        sa, sb, sr = a[0], b[0], r[0]
        same_ab = g.not_gate(g.xor_gate(sa, sb))
        diff_ar = g.xor_gate(sa, sr)
        return g.and_gate(same_ab, diff_ar)

    def _flag_V_sub(self, a: Bits32, b: Bits32, r: Bits32) -> Bit:
        # SUB overflow rule: sign(a) != sign(b) and sign(r) != sign(a)
        sa, sb, sr = a[0], b[0], r[0]
        diff_ab = g.xor_gate(sa, sb)
        diff_ar = g.xor_gate(sa, sr)
        return g.and_gate(diff_ab, diff_ar)

    # ----- operations -----

    def _op_add(self, a: Bits32, b: Bits32) -> Dict[str, object]:
        s, carry = self._add_unsigned(a, b, self._ZERO)
        N = self._flag_N(s)
        Z = self._flag_Z(s)
        C = carry
        V = self._flag_V_add(a, b, s)
        return {"result": s, "flags": {"N": bool(N), "Z": bool(Z), "C": bool(C), "V": bool(V)}}

    def _op_sub(self, a: Bits32, b: Bits32) -> Dict[str, object]:
        nb = self._not_vec(b)
        nb_plus1, _ = self._add_unsigned(nb, self._one_hot_lsb(), self._ZERO)  # ~b + 1
        s, carry = self._add_unsigned(a, nb_plus1, self._ZERO)
        N = self._flag_N(s)
        Z = self._flag_Z(s)
        C = carry  # carry==1 means NO borrow
        V = self._flag_V_sub(a, b, s)
        return {"result": s, "flags": {"N": bool(N), "Z": bool(Z), "C": bool(C), "V": bool(V)}}

    def _op_sll(self, a: Bits32, b: Bits32) -> Dict[str, object]:
        r = self._barrel_with_rs2(a, b, "SLL")
        N = self._flag_N(r)
        Z = self._flag_Z(r)
        C = self._ZERO
        V = self._ZERO
        return {"result": r, "flags": {"N": bool(N), "Z": bool(Z), "C": bool(C), "V": bool(V)}}

    def _op_srl(self, a: Bits32, b: Bits32) -> Dict[str, object]:
        r = self._barrel_with_rs2(a, b, "SRL")
        N = self._flag_N(r)
        Z = self._flag_Z(r)
        C = self._ZERO
        V = self._ZERO
        return {"result": r, "flags": {"N": bool(N), "Z": bool(Z), "C": bool(C), "V": bool(V)}}

    def _op_sra(self, a: Bits32, b: Bits32) -> Dict[str, object]:
        r = self._barrel_with_rs2(a, b, "SRA")
        N = self._flag_N(r)
        Z = self._flag_Z(r)
        C = self._ZERO
        V = self._ZERO
        return {"result": r, "flags": {"N": bool(N), "Z": bool(Z), "C": bool(C), "V": bool(V)}}


# convenience functional wrapper
_default_alu = ALU32()

def alu32(a: Bits32, b: Bits32, op: str) -> Dict[str, object]:
    return _default_alu.exec(a, b, op)
