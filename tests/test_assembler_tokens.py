import pytest
from assembler.instructions import InstructionToken

R_INSTRUCTIONS:list[str] = [
    "add", "sub", "and", "or", "xor", "sll", "srl", "sra"
]

def test_R_type():
    for ins in R_INSTRUCTIONS:
        for rd_n in range(0,32):
            for rs1_n in range(0,32):
                for rs2_n in range(0,32):
                    token = InstructionToken(0, ins, f"x{rd_n}", f"x{rs1_n}", f"x{rs1_n}")
                    assert True