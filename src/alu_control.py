from memory import Bit, Bitx2, Bitx3

CTRL_ALU_ADD = (0,0,0,0)
CTRL_ALU_SUB = (0,0,0,1)
CTRL_ALU_AND = (0,0,1,0)
CTRL_ALU_OR = (0,0,1,1)
CTRL_ALU_XOR = (0,1,0,0)
CTRL_ALU_SLL = (0,1,0,1)
CTRL_ALU_SRL = (0,1,1,0)
CTRL_ALU_SRA = (0,1,1,1)
CTRL_ALU_SLT = (1,0,0,0)
CTRL_ALU_SLTU = (1,0,0,1)

class ALUControl:
    def __init__(self):
        pass

    def update(self, ALUOp:Bitx2, funct3:Bitx3, funct7_bit_30:Bit):

        if ALUOp == (0,0):
            return CTRL_ALU_ADD
        elif ALUOp == (0,1):
            if funct3 in {(0,0,1), (0,0,0)}:
                return CTRL_ALU_SUB
            if funct3 in {(1,0,0), (1,0,1)}:
                return CTRL_ALU_SLT
            if funct3 in {(1,1,0), (1,1,1)}:
                return CTRL_ALU_SLTU
        elif ALUOp == (1,0):
            if funct3 == (0,0,0):
                if funct7_bit_30:
                    return CTRL_ALU_SUB
                else:
                    return CTRL_ALU_ADD
            if funct3 == (0,0,1):
                return CTRL_ALU_SLL
            if funct3 == (0,1,0):
                return CTRL_ALU_SLT
            if funct3 == (0,1,1):
                return CTRL_ALU_SLTU
            if funct3 == (1,0,0):
                return CTRL_ALU_XOR
            if funct3 == (1,0,1):
                if funct7_bit_30:
                    return CTRL_ALU_SRA
                else:
                    return CTRL_ALU_SRL
            if funct3 == (1,1,0):
                return CTRL_ALU_OR
            if funct3 == (1,1,1):
                return CTRL_ALU_AND
            
        raise RuntimeError(f"Unsupported ALUControl input:\nALUOp {ALUOp}\nfunct3{funct3}\nfunct7_bit_30{funct7_bit_30}")
        