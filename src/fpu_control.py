from memory import Bitx2, Bitx5, Bitx7, Bitx3

# FPU Control signals (5-bit tuples)
CTRL_FPU_ADD = (0, 0, 0, 0, 0)
CTRL_FPU_SUB = (0, 0, 0, 0, 1)
CTRL_FPU_MUL = (0, 0, 0, 1, 0)
CTRL_FPU_DIV = (0, 0, 0, 1, 1)
CTRL_FPU_SQRT = (0, 1, 0, 1, 1)
CTRL_FPU_MIN = (0, 1, 0, 1, 0)
CTRL_FPU_MAX = (0, 1, 0, 0, 1)
CTRL_FPU_EQ = (1, 0, 1, 0, 0)
CTRL_FPU_LT = (1, 0, 1, 0, 1)
CTRL_FPU_LE = (1, 0, 1, 1, 0)
CTRL_FPU_SGNJ = (0, 0, 1, 0, 0)
CTRL_FPU_SGNJN = (0, 0, 1, 0, 1)
CTRL_FPU_SGNJX = (0, 0, 1, 1, 0)
CTRL_FPU_CVT_W_S = (1, 1, 0, 0, 0)
CTRL_FPU_CVT_WU_S = (1, 1, 0, 0, 1)
CTRL_FPU_CVT_S_W = (1, 1, 0, 1, 0)
CTRL_FPU_CVT_S_WU = (1, 1, 0, 1, 1)
CTRL_FPU_MV_X_W = (1, 1, 1, 0, 0)
CTRL_FPU_MV_W_X = (1, 1, 1, 0, 1)
CTRL_FPU_CLASS = (1, 1, 1, 1, 0)

# funct7 values for RV32F instructions
FUNCT7_FADD = (0, 0, 0, 0, 0, 0, 0)
FUNCT7_FSUB = (0, 0, 0, 0, 1, 0, 0)
FUNCT7_FMUL = (0, 0, 0, 1, 0, 0, 0)
FUNCT7_FDIV = (0, 0, 0, 1, 1, 0, 0)
FUNCT7_FSQRT = (0, 1, 0, 1, 1, 0, 0)
FUNCT7_FSGNJ = (0, 0, 1, 0, 0, 0, 0)
FUNCT7_FMIN_MAX = (0, 0, 1, 0, 1, 0, 0)
FUNCT7_FCMP = (0, 1, 0, 1, 0, 0, 0)
FUNCT7_FCVT_W = (0, 0, 0, 0, 0, 1, 1)
FUNCT7_FCVT_S = (0, 0, 0, 1, 0, 1, 1)
FUNCT7_FMV_X_W = (0, 0, 0, 1, 1, 1, 1)
FUNCT7_FCLASS = (0, 0, 0, 1, 1, 1, 1)


class FPUControl:
    def __init__(self):
        pass
    
    def update(self, ALUOp: Bitx2, funct7: Bitx7, funct3: Bitx3, rs2: Bitx5):
        """
        Returns 5 bit FPU control signal
        """
        
        # FPU operations have ALUOp = (1,1)
        if ALUOp != (1, 1):
            raise RuntimeError(f"Invalid ALUOp for FPU: {ALUOp}")
        
        # Decode based on funct7
        if funct7 == FUNCT7_FADD:
            return CTRL_FPU_ADD
        
        elif funct7 == FUNCT7_FSUB:
            return CTRL_FPU_SUB
        
        elif funct7 == FUNCT7_FMUL:
            return CTRL_FPU_MUL
        
        elif funct7 == FUNCT7_FDIV:
            return CTRL_FPU_DIV
        
        elif funct7 == FUNCT7_FSQRT:
            return CTRL_FPU_SQRT
        
        elif funct7 == FUNCT7_FSGNJ:
            if funct3 == (0, 0, 0):
                return CTRL_FPU_SGNJ
            elif funct3 == (1, 0, 0):
                return CTRL_FPU_SGNJN
            elif funct3 == (0, 1, 0):
                return CTRL_FPU_SGNJX
        
        elif funct7 == FUNCT7_FMIN_MAX:
            if funct3 == (0, 0, 0):
                return CTRL_FPU_MIN
            elif funct3 == (1, 0, 0):
                return CTRL_FPU_MAX
        
        elif funct7 == FUNCT7_FCMP:
            if funct3 == (0, 1, 0):
                return CTRL_FPU_EQ
            elif funct3 == (1, 0, 0):
                return CTRL_FPU_LT
            elif funct3 == (0, 0, 0):
                return CTRL_FPU_LE
        
        elif funct7 == FUNCT7_FCVT_W:
            if rs2 == (0, 0, 0, 0, 0):
                return CTRL_FPU_CVT_W_S
            elif rs2 == (1, 0, 0, 0, 0):
                return CTRL_FPU_CVT_WU_S
        
        elif funct7 == FUNCT7_FCVT_S:
            if rs2 == (0, 0, 0, 0, 0):
                return CTRL_FPU_CVT_S_W
            elif rs2 == (1, 0, 0, 0, 0):
                return CTRL_FPU_CVT_S_WU
        
        elif funct7 == FUNCT7_FMV_X_W:            
            if funct3 == (0, 0, 0) and rs2 == (0, 0, 0, 0, 0):
                return CTRL_FPU_MV_X_W
        
        elif funct7 == FUNCT7_FCLASS:
            if funct3 == (1, 0, 0) and rs2 == (0, 0, 0, 0, 0):
                return CTRL_FPU_MV_W_X
            elif funct3 == (0, 0, 0) and rs2 == (0, 0, 0, 0, 0):
                return CTRL_FPU_CLASS
        
        raise RuntimeError(
            f"Unsupported FPUControl input:\n"
            f"ALUOp: {ALUOp}\n"
            f"funct7: {funct7}\n"
            f"funct3: {funct3}\n"
            f"rs2: {rs2}"
        )