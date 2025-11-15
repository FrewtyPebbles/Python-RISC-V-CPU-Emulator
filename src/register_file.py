from memory import Bit, Bitx32, Bitx5
from register import Register32bit, Register16bit, Register8bit, FloatRegister32bit, Register
from encoder_decoder import decoder5x32, one_hot_to_decimal

class RegisterFile:

    def __init__(self):
        self.registers:list[Register] = [Register32bit() for _ in range(32)]

    def update(self, read_reg_1_adr:Bitx5, read_reg_2_adr:Bitx5, write_reg_adr:Bitx5, write_data:Bitx32, control_reg_write:Bit, clock:Bit) -> tuple[Bitx32, Bitx32]:
        read_reg_1_pos_one_hot = decoder5x32(*read_reg_1_adr)
        read_reg_2_pos_one_hot = decoder5x32(*read_reg_2_adr)
        write_reg_pos_one_hot = decoder5x32(*write_reg_adr)

        read_reg_1_pos = one_hot_to_decimal(read_reg_1_pos_one_hot)
        read_reg_2_pos = one_hot_to_decimal(read_reg_2_pos_one_hot)
        write_reg_pos = one_hot_to_decimal(write_reg_pos_one_hot)

        if control_reg_write:
            write_reg = self.registers[write_reg_pos]
            for b_n, bit in enumerate(write_reg):
                bit.value = write_data[b_n].value

        return self.registers[read_reg_1_pos].read_bits(), self.registers[read_reg_2_pos].read_bits()
        

