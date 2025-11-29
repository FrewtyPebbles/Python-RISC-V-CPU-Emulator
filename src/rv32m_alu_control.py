from memory import Bit, Bitx2, Bitx3

# RV32M ALU Control signals
CTRL_MALU_MUL = (0, 0, 0, 0)
CTRL_MALU_MULH = (1, 0, 0, 0)
CTRL_MALU_MULHSU = (0, 1, 0, 0)
CTRL_MALU_MULHU = (1, 1, 0, 0)
CTRL_MALU_DIV = (0, 0, 1, 0)
CTRL_MALU_DIVU = (1, 0, 1, 0)
CTRL_MALU_REM = (0, 1, 1, 0)
CTRL_MALU_REMU = (1, 1, 1, 0)

class RV32MALUControl:
    def __init__(self):
        pass

    def update(self, ALUOp: Bitx2, funct3: Bitx3):
        # RV32M operations use ALUOp = (1,1)
        if ALUOp == (1, 1):
            if funct3 == (0, 0, 0): # MUL
                return CTRL_MALU_MUL
            if funct3 == (1, 0, 0): # MULH
                return CTRL_MALU_MULH
            if funct3 == (0, 1, 0): # MULHSU
                return CTRL_MALU_MULHSU
            if funct3 == (1, 1, 0): # MULHU
                return CTRL_MALU_MULHU
            if funct3 == (0, 0, 1): # DIV
                return CTRL_MALU_DIV
            if funct3 == (1, 0, 1): # DIVU
                return CTRL_MALU_DIVU
            if funct3 == (0, 1, 1): # REM
                return CTRL_MALU_REM
            if funct3 == (1, 1, 1): # REMU
                return CTRL_MALU_REMU
        
        raise RuntimeError(f"Unsupported RV32MALUControl input:\nALUOp {ALUOp}\nfunct3 {funct3}")