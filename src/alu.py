from memory import Bit, Bitx12, Bitx32, Bitx4

import alu_control as ac

class ALU:
    def __init__(self):
        pass
        #might add attributes later
    
    def update(self, operation:Bitx4, read_data_1:Bitx32, read_data_2:Bitx32) -> tuple[Bit, Bitx32]:
        """
        Returns Zero bit signal and 32-bit alu result.
        """
        match operation:
            case ac.CTRL_ALU_ADD:
                return self.op_add(read_data_1, read_data_2)
            case ac.CTRL_ALU_SUB:
                return self.op_sub(read_data_1, read_data_2)
            case ac.CTRL_ALU_AND:
                return self.op_and(read_data_1, read_data_2)
            case ac.CTRL_ALU_OR:
                return self.op_or(read_data_1, read_data_2)
            case ac.CTRL_ALU_XOR:
                return self.op_xor(read_data_1, read_data_2)
            case ac.CTRL_ALU_SLL:
                return self.op_sll(read_data_1, read_data_2)
            case ac.CTRL_ALU_SRL:
                return self.op_srl(read_data_1, read_data_2)
            case ac.CTRL_ALU_SRA:
                return self.op_sra(read_data_1, read_data_2)
            case ac.CTRL_ALU_SLT:
                return self.op_slt(read_data_1, read_data_2)
            case ac.CTRL_ALU_SLTU:
                return self.op_sltu(read_data_1, read_data_2)

    @staticmethod
    def op_add(read_data_1:Bitx32, read_data_2:Bitx32):
        pass

    @staticmethod
    def op_sub(read_data_1:Bitx32, read_data_2:Bitx32):
        pass
    
    @staticmethod
    def op_and(read_data_1:Bitx32, read_data_2:Bitx32):
        pass
    
    @staticmethod
    def op_or(read_data_1:Bitx32, read_data_2:Bitx32):
        pass

    @staticmethod
    def op_xor(read_data_1:Bitx32, read_data_2:Bitx32):
        pass

    @staticmethod
    def op_sll(read_data_1:Bitx32, read_data_2:Bitx32):
        pass

    @staticmethod
    def op_srl(read_data_1:Bitx32, read_data_2:Bitx32):
        pass

    @staticmethod
    def op_sra(read_data_1:Bitx32, read_data_2:Bitx32):
        pass

    @staticmethod
    def op_slt(read_data_1:Bitx32, read_data_2:Bitx32):
        # EXTRA CREDIT
        pass

    @staticmethod
    def op_sltu(read_data_1:Bitx32, read_data_2:Bitx32):
        # EXTRA CREDIT
        pass
