from memory import Bit, Bitx7, bin_str_to_bits, bin_to_dec

OPCODE_R_TYPE = (0,1,1,0,0,1,1)
OPCODE_I_TYPE = (0,0,1,0,0,1,1)
OPCODE_LOAD = (0,0,0,0,0,1,1)
OPCODE_STORE = (0,1,0,0,0,1,1)
OPCODE_BRANCH = (1,1,0,0,0,1,1)
OPCODE_JAL = (1,1,0,1,1,1,1)
OPCODE_JALR = (1,1,0,0,1,1,1)
OPCODE_FP = (1,0,1,0,0,1,1)

class ControlUnit:
    def __init__(self):
        self.reset()

    def reset(self):
        self.RegDst = 0
        self.ALUSrc = 0
        self.MemToReg = 0
        self.RegWrite = 0
        self.MemRead = 0
        self.MemWrite = 0
        self.Branch = 0
        self.Jump = 0
        self.ALUOp = (0, 0)  # 2-bit tuple

    def decode(self, opcode: Bitx7):

        self.reset()

        # R-Type
        if opcode == OPCODE_R_TYPE:
            self.RegDst = 1
            self.RegWrite = 1
            self.ALUOp = (1, 0)   # 10

        # I-type
        elif opcode == OPCODE_I_TYPE:
            self.ALUSrc = 1
            self.RegWrite = 1
            self.ALUOp = (1, 0)   # 10

        # Load
        elif opcode == OPCODE_LOAD:
            self.ALUSrc = 1
            self.MemToReg = 1
            self.RegWrite = 1
            self.MemRead = 1
            self.ALUOp = (0, 0)  # 00

        # Store
        elif opcode == OPCODE_STORE:
            self.ALUSrc = 1
            self.MemWrite = 1
            self.ALUOp = (0, 0)  # 00

        # Branch
        elif opcode == OPCODE_BRANCH:
            self.Branch = 1
            self.ALUOp = (0, 1)   # 01

        # JAL
        elif opcode == OPCODE_JAL:
            self.Jump = 1
            self.RegWrite = 1
            self.ALUOp = (0, 0)  # 00 (PC + offset add)

        # JALR
        elif opcode == OPCODE_JALR:
            self.Jump = 1
            self.RegWrite = 1
            self.ALUOp = (0, 0)  # 00

        # FPU op
        elif opcode == OPCODE_FP:
            self.RegWrite = 1
            self.ALUOp = (1, 1)    # 11 = FP ALU

        else:
            raise ValueError(f"Unknown opcode: {opcode:07b}")
