from memory import Bit, Bitx5, Bitx32
from register import FloatRegister32bit

class FREG:
    registers:list[FloatRegister32bit] #stores data
    fscr:FloatRegister32bit #stores status and exception flags

    def __init__(self):
        registers = [FloatRegister32bit() for _ in range(32)]
        fscr = FloatRegister32bit() 

    def update(self, read_reg_1_adr:Bitx5, read_reg_2_adr:Bitx5, write_reg_adr:Bitx5, write_data:Bitx32, control_reg_write:Bit) -> tuple[Bitx32, Bitx32]:
        pass

    