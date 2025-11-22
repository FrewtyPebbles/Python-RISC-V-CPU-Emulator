from memory import Bit, Bitx7, bin_str_to_bits, bin_to_dec

OPCODE_R_TYPE   = 0b0110011
OPCODE_I_TYPE   = 0b0010011
OPCODE_LOAD     = 0b0000011
OPCODE_STORE    = 0b0100011
OPCODE_BRANCH   = 0b1100011
OPCODE_JAL      = 0b1101111
OPCODE_JALR     = 0b1100111
OPCODE_FP       = 0b1010011

class ControlUnit:
    def __init__(self):
        self.reset()

    def reset(self):
        self.RegDst   = Bit(False)
        self.ALUSrc   = Bit(False)
        self.MemToReg = Bit(False)
        self.RegWrite = Bit(False)
        self.MemRead  = Bit(False)
        self.MemWrite = Bit(False)
        self.Branch   = Bit(False)
        self.Jump     = Bit(False)
        self.ALUOp    = (Bit(False), Bit(False))  # 2-bit tuple

    def decode(self, opcode: Bitx7):
        opcode: int = bin_to_dec(opcode)

        self.reset()

        # R-Type
        if opcode == OPCODE_R_TYPE:
            self.RegDst = Bit(True)
            self.RegWrite = Bit(True)
            self.ALUOp = (Bit(True), Bit(False))   # 10

        # I-type
        elif opcode == OPCODE_I_TYPE:
            self.ALUSrc = Bit(True)
            self.RegWrite = Bit(True)
            self.ALUOp = (Bit(True), Bit(False))   # 10

        # Load
        elif opcode == OPCODE_LOAD:
            self.ALUSrc = Bit(True)
            self.MemToReg = Bit(True)
            self.RegWrite = Bit(True)
            self.MemRead = Bit(True)
            self.ALUOp = (Bit(False), Bit(False))  # 00

        # Store
        elif opcode == OPCODE_STORE:
            self.ALUSrc = Bit(True)
            self.MemWrite = Bit(True)
            self.ALUOp = (Bit(False), Bit(False))  # 00

        # Branch
        elif opcode == OPCODE_BRANCH:
            self.Branch = Bit(True)
            self.ALUOp = (Bit(False), Bit(True))   # 01

        # JAL
        elif opcode == OPCODE_JAL:
            self.Jump = Bit(True)
            self.RegWrite = Bit(True)
            self.ALUOp = (Bit(False), Bit(False))  # 00 (PC + offset add)

        # JALR
        elif opcode == OPCODE_JALR:
            self.Jump = Bit(True)
            self.RegWrite = Bit(True)
            self.ALUOp = (Bit(False), Bit(False))  # 00

        # FPU op
        elif opcode == OPCODE_FP:
            self.RegWrite = Bit(True)
            self.ALUOp = (Bit(True), Bit(True))    # 11 = FP ALU

        else:
            raise ValueError(f"Unknown opcode: {opcode:07b}")
