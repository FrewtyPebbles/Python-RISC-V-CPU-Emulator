from memory import Bit, Bitx7, bin_to_dec

class ControlUnit:
    def __init__(self):
        self.RegDst = Bit(False)
        self.ALUSrc = Bit(False)
        self.MemToReg = Bit(False)
        self.RegWrite = Bit(False)
        self.MemRead = Bit(False)
        self.MemWrite = Bit(False)
        self.Branch = Bit(False)
        self.ALUOp = 0

    def decode(self, opcode: Bitx7):
        opcode:int = bin_to_dec(opcode)

        self.RegDst = Bit(False)
        self.ALUSrc = Bit(False)
        self.MemToReg = Bit(False)
        self.RegWrite = Bit(False)
        self.MemRead = Bit(False)
        self.MemWrite = Bit(False)
        self.Branch = Bit(False)
        self.ALUOp = 0

        if opcode == 0b0110011:
            self.RegDst = Bit(True)
            self.ALUSrc = Bit(False)
            self.RegWrite = Bit(True)
            self.ALUOp = 2
        elif opcode == 0b0010011:
            self.RegDst = Bit(True)
            self.ALUSrc = Bit(True)
            self.RegWrite = Bit(True)
            self.ALUOp = 0
        elif opcode == 0b0000011:
            self.RegDst = Bit(True)
            self.ALUSrc = Bit(True)
            self.MemToReg = Bit(True)
            self.RegWrite = Bit(True)
            self.MemRead = Bit(True)
            self.ALUOp = 0
        elif opcode == 0b0100011:
            self.ALUSrc = Bit(True)
            self.MemWrite = Bit(True)
            self.ALUOp = 0
        elif opcode == 0b1100011:
            self.ALUSrc = Bit(False)
            self.Branch = Bit(True)
            self.ALUOp = 1

        return {
            "RegDst": self.RegDst,
            "ALUSrc": self.ALUSrc,
            "MemToReg": self.MemToReg,
            "RegWrite": self.RegWrite,
            "MemRead": self.MemRead,
            "MemWrite": self.MemWrite,
            "Branch": self.Branch,
            "ALUOp": self.ALUOp
        }
