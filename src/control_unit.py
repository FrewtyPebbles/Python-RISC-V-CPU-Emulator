from memory import Bit, Bits, Bitx32, Bitx7, bin_str_to_bits, bin_to_dec, sign_extend, shift_left_1, shift_left_2

# LSB first
OPCODE_LOAD = (1,1,0,0,0,0,0)
OPCODE_STORE = (1,1,0,0,0,1,0)
OPCODE_I_TYPE = (1,1,0,0,1,0,0)
OPCODE_R_TYPE = (1,1,0,0,1,1,0)
OPCODE_LUI = (1,1,1,0,1,1,0)
OPCODE_AUIPC = (1,1,1,0,1,0,0)
OPCODE_BRANCH = (1,1,0,0,0,1,1)
OPCODE_JALR = (1,1,1,0,0,1,1)
OPCODE_JAL = (1,1,1,1,0,1,1)
OPCODE_SYSTEM = (1,1,0,0,0,1,1)
OPCODE_MISC = (1,1,1,1,0,0,0)
OPCODE_FP = (1,1,0,0,1,0,1)
OPCODE_FLW = (1,1,0,0,0,0,1) # Load Float
OPCODE_FSW = (1,1,0,0,0,1,1) # Store Float

R_TYPE_OPCODES = {
    (1, 1, 0, 0, 1, 1, 0),
}

I_TYPE_OPCODES = {
    (1, 1, 0, 0, 1, 0, 0),
    (1, 1, 0, 0, 0, 0, 0),
    (1, 1, 1, 0, 0, 1, 1),
    (1, 1, 0, 0, 1, 1, 1),
}

S_TYPE_OPCODES = {
    (1, 1, 0, 0, 0, 1, 0),
}

B_TYPE_OPCODES = {
    (1, 1, 0, 0, 0, 1, 1),
}

U_TYPE_OPCODES = {
    (1, 1, 1, 0, 1, 1, 0),
    (1, 1, 1, 0, 1, 0, 0),
}

J_TYPE_OPCODES = {
    (1, 1, 1, 1, 0, 1, 1),
}

class ControlUnit:
    def __init__(self):
        self.reset()

    @staticmethod
    def get_imm_i(instruction: Bits) -> Bitx32:
        # I-type
        return sign_extend(instruction[20:32], 32)

    @staticmethod
    def get_imm_s(instruction: Bits) -> Bitx32:
        # S-type
        imm = instruction[7:12] + instruction[25:32]
        return sign_extend(imm, 32)

    @staticmethod
    def get_imm_b(instruction: Bits) -> Bitx32:
        # B-type
        imm = (
            instruction[7],
            *instruction[8:12],
            *instruction[25:31],
            instruction[31],
            0
        )
        return sign_extend(imm, 32)

    @staticmethod
    def get_imm_u(instruction: Bits) -> Bitx32:
        # U-type
        return (0,)*12 + instruction[12:32]

    @staticmethod
    def get_imm_j(instruction: Bits) -> Bitx32:
        # J-type
        imm = (
            instruction[20],
            *instruction[12:20],
            *instruction[21:31],
            instruction[31],
            0
        )
        return sign_extend(imm, 32)

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
        
        # RV32F Signals
        self.FPUOp = 0
        self.FPRegWrite = 0
        self.FPRegRead = 0
        self.FPALUSrc = 0
        self.FPMemToReg = 0
        self.RegFileSel = 0
        self.FPToInt = 0
        self.IntToFP = 0
        

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
            self.ALUOp = (0, 0)  # 00

        # JALR
        elif opcode == OPCODE_JALR:
            self.Jump = 1
            self.RegWrite = 1
            self.ALUOp = (0, 0)  # 00

        elif opcode == OPCODE_LUI:
            self.RegWrite = 1
            self.ALUOp = (0, 0)

        # FPU op
        elif opcode == OPCODE_FP:
            self.FPUOp = 1
            self.FPRegWrite = 1
            self.FPRegRead = 1
            self.RegFileSel = 1
            self.ALUOp = (1, 1)   # 11

        # FLW (LOAD)
        elif opcode == OPCODE_FLW:
            self.ALUSrc = 1
            self.FPMemToReg = 1
            self.FPRegWrite = 1
            self.MemRead = 1
            self.RegFileSel = 1
            self.ALUOp = (0, 0)

        # FSW (WRITE)
        elif opcode == OPCODE_FSW:
            self.ALUSrc = 1
            self.MemWrite = 1
            self.FPRegRead = 1
            self.RegFileSel = 1
            self.ALUOp = (0, 0)
        
        # AUIPC
        elif opcode == OPCODE_AUIPC:
            self.RegWrite = 1
            self.ALUSrc = 1
            self.ALUOp = (0, 0)

        # SYSTEM (ECALL, EBREAK, CSR instructions)
        elif opcode == OPCODE_SYSTEM:
            self.RegWrite = 0
            self.ALUOp = (0, 0)

        # MISC-MEM (FENCE / FENCE.I)
        elif opcode == OPCODE_MISC:
            self.RegWrite = 0
            self.ALUOp = (0, 0)

        else:
            raise ValueError(f"Unknown opcode: {opcode}")
