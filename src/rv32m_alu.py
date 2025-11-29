from memory import Bit, Bitx32, Bitx4
import gates as g

import rv32m_alu_control as mc

class RV32MALU:
    def __init__(self):
        pass
    
    def update(self, operation: Bitx4, read_data_1: Bitx32, read_data_2: Bitx32) -> tuple[Bit, Bitx32]:
        """
        Returns Zero bit signal and 32-bit result.
        """
        match operation:
            case mc.CTRL_MALU_MUL:
                return self.op_mul(read_data_1, read_data_2)
            case mc.CTRL_MALU_MULH:
                return self.op_mulh(read_data_1, read_data_2)
            case mc.CTRL_MALU_MULHSU:
                return self.op_mulhsu(read_data_1, read_data_2)
            case mc.CTRL_MALU_MULHU:
                return self.op_mulhu(read_data_1, read_data_2)
            case mc.CTRL_MALU_DIV:
                return self.op_div(read_data_1, read_data_2)
            case mc.CTRL_MALU_DIVU:
                return self.op_divu(read_data_1, read_data_2)
            case mc.CTRL_MALU_REM:
                return self.op_rem(read_data_1, read_data_2)
            case mc.CTRL_MALU_REMU:
                return self.op_remu(read_data_1, read_data_2)
            case _:
                raise RuntimeError(f"RV32MALU Operation not supported {operation}")
    
    @staticmethod
    def compute_zero(res: Bitx32) -> Bit:
        return int(all(b == 0 for b in res))
    
    @staticmethod
    def op_mul(read_data_1: Bitx32, read_data_2: Bitx32) -> tuple[Bit, Bitx32]:
        pass
    
    @staticmethod
    def op_mulh(read_data_1: Bitx32, read_data_2: Bitx32) -> tuple[Bit, Bitx32]:
        pass
    
    @staticmethod
    def op_mulhsu(read_data_1: Bitx32, read_data_2: Bitx32) -> tuple[Bit, Bitx32]:
        pass
    
    @staticmethod
    def op_mulhu(read_data_1: Bitx32, read_data_2: Bitx32) -> tuple[Bit, Bitx32]:
        pass
    
    @staticmethod
    def op_div(read_data_1: Bitx32, read_data_2: Bitx32) -> tuple[Bit, Bitx32]:
        pass
    
    @staticmethod
    def op_divu(read_data_1: Bitx32, read_data_2: Bitx32) -> tuple[Bit, Bitx32]:
        pass
    
    @staticmethod
    def op_rem(read_data_1: Bitx32, read_data_2: Bitx32) -> tuple[Bit, Bitx32]:
        pass
    
    @staticmethod
    def op_remu(read_data_1: Bitx32, read_data_2: Bitx32) -> tuple[Bit, Bitx32]:
        pass