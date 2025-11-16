import unittest
from memory import Bit
from control_fsm import ControlUnit, _u5
from fpu import fadd_f32  # used to validate the final value matches FPU in the FPU test

# Helpers (MSB-first)
def hex32_to_bits_msb(h: str):
    h = h.strip().lower().replace("0x", "")
    val = int(h, 16) & 0xFFFFFFFF
    return tuple(Bit(bool((val >> i) & 1)) for i in range(31, -1, -1))

def bits_to_hex32(bits):
    v = 0
    for b in bits:
        v = (v << 1) | (1 if b else 0)
    return f"0x{v:08X}"


class TestControlFSM(unittest.TestCase):

    def test_fpu_add_full_sequence_and_writeback(self):
        cu = ControlUnit()
        rs1 = hex32_to_bits_msb("3FC00000")  # 1.5
        rs2 = hex32_to_bits_msb("40100000")  # 2.25
        rd  = _u5(10)

        # Precompute with the FPU for result check
        ref = fadd_f32(rs1, rs2)["res_bits"]

        cu.start_fpu("ADD", rs1, rs2, rd, round_mode="RNE")

        # Expect 6 steps: IDLE, ALIGN, OP, NORMALIZE, ROUND, WRITEBACK
        notes = []
        for _ in range(6):
            row = cu.step()
            notes.append(row["note"])

        self.assertEqual(notes[0], "FPU:IDLE")
        self.assertEqual(notes[-1], "FPU:WRITEBACK")

        # WRITEBACK must assert rf_we and target rd
        last = cu.trace[-1]
        self.assertTrue(last["rf_we"])
        self.assertEqual(last["rf_waddr"], 10)

        # Result equals the FPU's computation
        self.assertEqual(bits_to_hex32(cu.get_result()), bits_to_hex32(ref))

    def test_alu_single_cycle_sequence(self):
        cu = ControlUnit()
        rs1 = hex32_to_bits_msb("7FFFFFFF")
        rs2 = hex32_to_bits_msb("00000001")
        rd  = _u5(1)

        cu.start_alu("ADD", rs1, rs2, rd)
        notes = []
        for _ in range(3):  # IDLE, EXECUTE, WRITEBACK
            notes.append(cu.step()["note"])

        self.assertEqual(notes, ["ALU:IDLE", "ALU:EXECUTE", "ALU:WRITEBACK"])
        last = cu.trace[-1]
        self.assertTrue(last["rf_we"])
        self.assertEqual(last["rf_waddr"], 1)

    def test_mdu_busy_done_handshake(self):
        cu = ControlUnit()
        rs1 = hex32_to_bits_msb("00000003")
        rs2 = hex32_to_bits_msb("00000007")
        rd  = _u5(5)

        cu.start_mdu("MUL", rs1, rs2, rd, cycles=8)

        notes = []
        starts = 0
        bodies = 0
        for _ in range(10):  # IDLE + 8 BODY + WB = 10
            row = cu.step()
            notes.append(row["note"])
            if row["note"].endswith("START"):
                starts += 1
                self.assertTrue(row["md_start"])
                self.assertTrue(row["md_busy"])
            elif "STEP" in row["note"]:
                bodies += 1
                self.assertTrue(row["md_busy"])
                self.assertFalse(row["md_done"])
            elif row["note"].endswith("WRITEBACK"):
                self.assertTrue(row["rf_we"])
                self.assertTrue(row["md_done"])
                self.assertFalse(row["md_busy"])

        self.assertEqual(starts, 1)
        self.assertEqual(bodies, 8)
        self.assertTrue(notes[0].endswith("START"))
        self.assertTrue(notes[-1].endswith("WRITEBACK"))


if __name__ == "__main__":
    unittest.main()
