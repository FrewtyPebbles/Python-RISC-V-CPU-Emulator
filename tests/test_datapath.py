# test_datapath_hex_le.py
import pytest
from datapath import DataPath

def test_pc_increment():
    dp = DataPath()
    
    # NOP: add x0, x0, x0 (R-type)
    nop_hex_le = "33000000"  # little-endian bytes of 0x00000033
    dp.instruction_memory.load([nop_hex_le])
    
    dp.run()
    
    pc_val = int("".join(str(b) for b in dp.pc.value[::-1]), 2)
    assert pc_val == 4

def test_branch_taken():
    dp = DataPath()
    
    # beq x0, x0, 4 (B-type)
    beq_hex_le = "63000000"  # little-endian of 0x00000063
    dp.instruction_memory.load([beq_hex_le])
    
    dp.run()
    
    pc_val = int("".join(str(b) for b in dp.pc.value[::-1]), 2)
    assert pc_val != 4

def test_jump():
    dp = DataPath()
    
    # jal x1, 8
    jal_hex_le = "EF800000"  # little-endian of 0x008000EF
    dp.instruction_memory.load([jal_hex_le])
    
    dp.run()
    
    pc_val = int("".join(str(b) for b in dp.pc.value[::-1]), 2)
    assert pc_val != 4

if __name__ == "__main__":
    pytest.main()
