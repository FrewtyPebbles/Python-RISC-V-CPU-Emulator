from __future__ import annotations
from typing import Tuple, Dict, List, Optional

from memory import Bit
from fpu import FPU32
from alu import ALU32
import gates as g

Bits32 = Tuple[Bit, ...]
Bits5  = Tuple[Bit, Bit, Bit, Bit, Bit]


def _u5(x: int) -> Bits5:
    """Encode unsigned 5-bit int to MSB-first Bits5."""
    x &= 0x1F
    return tuple(Bit(bool((x >> i) & 1)) for i in range(4, -1, -1))  # MSB..LSB


class ControlUnit:
    """
    A tiny, multi-cycle control unit that sequences ALU/FPU/MDU operations.
    It exposes a row of control signals per cycle for tracing / testing.
    """

    def __init__(self):
        self._ZERO = Bit(False)
        self._ONE  = Bit(True)

        self._fpu: Optional[FPU32] = FPU32() if FPU32 else None
        self._alu: Optional[ALU32] = ALU32() if ALU32 else None

        # latched operands / destinations for current op
        self._rs1: Optional[Bits32] = None
        self._rs2: Optional[Bits32] = None
        self._rd:  Optional[Bits5]  = None

        # current mode & state
        self._mode: str = "IDLE"          # "IDLE" | "FPU" | "ALU" | "MDU"
        self._fpu_state: str = "IDLE"     # FPU sub-state
        self._md_busy: Bit = self._ZERO
        self._md_done: Bit = self._ZERO
        self._md_count: int = 0
        self._md_total: int = 0
        self._md_kind: str = ""           # "MUL" | "DIV"

        self._alu_op: str = ""            # "ADD" | "SUB" | "SLL" | "SRL" | "SRA"
        self._sh_op: str  = ""            # mirror for trace

        self._round_mode: str = "RNE"     # default

        # last completed result (for a real datapath you’d write to RF)
        self._result: Optional[Bits32] = None
        self._flags: Optional[Dict[str, bool]] = None

        # trace log (list of per-cycle dict rows)
        self.trace: List[Dict[str, object]] = []

    def start_fpu(self, op: str, rs1: Bits32, rs2: Bits32, rd: Bits5, round_mode: str = "RNE"):
        """
        Begin a multi-cycle FPU op ('ADD', 'SUB', 'MUL').
        The actual arithmetic is delegated to FPU32; the CU just sequences states.
        """
        self._assert_idle()
        self._mode = "FPU"
        self._fpu_state = "IDLE"
        self._rs1, self._rs2, self._rd = rs1, rs2, rd
        self._round_mode = round_mode
        self._alu_op = ""   # not used in FPU
        self._sh_op  = ""   # not used in FPU
        self._result = None
        self._flags  = None
        self._md_busy = self._ZERO
        self._md_done = self._ZERO
        self.trace.clear()

        # Not strictly necessary, but we can precompute to hand back in WRITEBACK
        if self._fpu:
            if op.upper() == "ADD":
                out = self._fpu.add(rs1, rs2)
            elif op.upper() == "SUB":
                out = self._fpu.sub(rs1, rs2)
            elif op.upper() == "MUL":
                out = self._fpu.mul(rs1, rs2)
            else:
                raise ValueError("FPU op must be ADD/SUB/MUL")
            self._result = out["res_bits"]
            self._flags  = {k: bool(v) for k, v in out["flags"].items()}
        else:
            # Fallback if FPU32 not present: produce zeros; flags false
            self._result = tuple(self._ZERO for _ in range(32))
            self._flags  = {"overflow": False, "underflow": False, "invalid": False, "inexact": False, "divide_by_zero": False}

        # FPU micro-sequence plan:
        # IDLE → ALIGN → OP → NORMALIZE → ROUND → WRITEBACK
        self._fpu_plan = ["IDLE", "ALIGN", "OP", "NORMALIZE", "ROUND", "WRITEBACK"]

    def start_alu(self, op: str, rs1: Bits32, rs2: Bits32, rd: Bits5):
        """
        Begin an ALU op ('ADD','SUB','SLL','SRL','SRA').
        We model it as 1-cycle compute + WRITEBACK
        """
        self._assert_idle()
        self._mode = "ALU"
        self._rs1, self._rs2, self._rd = rs1, rs2, rd
        self._alu_op = op.upper()
        self._sh_op  = self._alu_op if self._alu_op in ("SLL","SRL","SRA") else ""
        self._round_mode = "RNE"
        self._result = None
        self._flags  = None
        self._md_busy = self._ZERO
        self._md_done = self._ZERO
        self.trace.clear()

        # Compute now (single-cycle)
        if self._alu:
            out = self._alu.exec(rs1, rs2, self._alu_op)
            self._result = out["result"]
            self._flags  = out["flags"]
        else:
            # Placeholder result if ALU32 not installed
            self._result = tuple(self._ZERO for _ in range(32))
            self._flags  = {"N": False, "Z": True, "C": False, "V": False}

        # micro-sequence: IDLE -> EXECUTE -> WRITEBACK
        self._alu_plan = ["IDLE", "EXECUTE", "WRITEBACK"]

    def start_mdu(self, kind: str, rs1: Bits32, rs2: Bits32, rd: Bits5, cycles: int = 32):
        """
        Begin a multiply/divide (simulated) with a fixed step count to show multi-cycle control.
        kind: "MUL" | "DIV"
        """
        self._assert_idle()
        self._mode = "MDU"
        self._rs1, self._rs2, self._rd = rs1, rs2, rd
        self._md_kind = kind.upper()
        self._md_total = max(1, int(cycles))
        self._md_count = 0
        self._md_busy = self._ONE
        self._md_done = self._ZERO
        self._alu_op = ""
        self._sh_op  = ""
        self._round_mode = "RNE"
        self._result = tuple(self._ZERO for _ in range(32))  # placeholder
        self._flags  = {}

        self.trace.clear()
        # micro-sequence: IDLE -> (TESTBIT -> SUB/RESTORE -> SHIFT)* -> WRITEBACK (for DIV)
        # or IDLE -> (ADD/SHIFT)* -> WRITEBACK (for MUL)
        # Here we just model a fixed number of body steps.
        self._mdu_plan = ["IDLE"] + ["BODY"] * self._md_total + ["WRITEBACK"]

    def step(self) -> Dict[str, object]:
        """
        Advance the FSM by one cycle and return the trace row (control signals snapshot).
        The control signals are recorded as simple scalars for readability.
        """
        row: Dict[str, object] = {
            "alu_op": self._alu_op,
            "rf_we": False,
            "rf_waddr": self._bits5_to_int(self._rd) if self._rd else None,
            "src_a_sel": "rs1",
            "src_b_sel": "rs2",
            "sh_op": self._sh_op,
            "md_start": False,
            "md_busy": bool(self._md_busy),
            "md_done": bool(self._md_done),
            "fpu_state": self._fpu_state if self._mode == "FPU" else "",
            "round_mode": self._round_mode,
            "mode": self._mode,
        }

        if self._mode == "IDLE":
            row["note"] = "IDLE"
            self.trace.append(row)
            return row

        if self._mode == "FPU":
            # pop next substate
            st = self._fpu_plan.pop(0)
            self._fpu_state = st
            row["fpu_state"] = st
            row["note"] = f"FPU:{st}"

            if st == "IDLE":
                # no side-effects
                pass
            elif st == "WRITEBACK":
                # write enable and address on WB
                row["rf_we"] = True
                row["rf_waddr"] = self._bits5_to_int(self._rd)
                # After WB we go idle
                self._reset_to_idle()
            # append and return
            self.trace.append(row)
            return row

        if self._mode == "ALU":
            st = self._alu_plan.pop(0)
            row["note"] = f"ALU:{st}"
            if st == "WRITEBACK":
                row["rf_we"] = True
                row["rf_waddr"] = self._bits5_to_int(self._rd)
                self._reset_to_idle()
            self.trace.append(row)
            return row

        if self._mode == "MDU":
            st = self._mdu_plan.pop(0)
            if st == "IDLE":
                row["note"] = f"{self._md_kind}:START"
                row["md_start"] = True
                self._md_busy = self._ONE
                row["md_busy"] = True
            elif st == "BODY":
                self._md_count += 1
                row["note"] = f"{self._md_kind}:STEP {self._md_count}/{self._md_total}"
                self._md_busy = self._ONE
                row["md_busy"] = True
            elif st == "WRITEBACK":
                row["note"] = f"{self._md_kind}:WRITEBACK"
                row["rf_we"] = True
                row["rf_waddr"] = self._bits5_to_int(self._rd)
                self._md_busy = self._ZERO
                self._md_done = self._ONE
                row["md_busy"] = False
                row["md_done"] = True
                self._reset_to_idle()
            self.trace.append(row)
            return row

        # Fallback
        row["note"] = "UNKNOWN"
        self.trace.append(row)
        return row

    def _assert_idle(self):
        if self._mode != "IDLE":
            raise RuntimeError("ControlUnit is busy; finish current op before starting a new one.")

    def _bits5_to_int(self, bits: Optional[Bits5]) -> Optional[int]:
        if bits is None:
            return None
        v = 0
        for b in bits:
            v = (v << 1) | (1 if b else 0)
        return v

    def _reset_to_idle(self):
        """Return to IDLE after a WRITEBACK state."""
        self._mode = "IDLE"
        self._fpu_state = "IDLE"
        self._md_busy = self._ZERO
        self._md_done = self._ZERO
        self._md_total = 0
        self._md_count = 0
        self._md_kind = ""
        self._alu_op = ""
        self._sh_op  = ""
        # keep _result/_flags for the caller to read if desired

    def get_result(self) -> Optional[Bits32]:
        return self._result

    def get_flags(self) -> Optional[Dict[str, bool]]:
        return self._flags
