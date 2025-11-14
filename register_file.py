from memory import Bit, Bitx32, Bitx5
from register import Register32bit, Register16bit, Register8bit, FloatRegister32bit, Register

class RegisterFile:

    def __init__(self):
        self.registers:list[Register] = [Register32bit() for _ in range(32)]

    def update(read_reg_1:Bitx5, read_reg_2:Bitx5, write_reg:Bitx5, write_data:Bitx32, control_reg_write:Bit, clock:Bit) -> tuple[Bitx32, Bitx32]:
        pass