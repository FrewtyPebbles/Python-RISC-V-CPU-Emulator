from memory import Bit, Bitx32, Bitx5, bin_to_dec
from register import Register32bit, Register16bit, Register8bit, FloatRegister32bit, Register
from encoder_decoder import decoder5x32, one_hot_to_decimal

import os

class RV32IRegisterFile:

    def __init__(self):
        self.registers:list[Register32bit] = [Register32bit() for _ in range(32)]

    def __repr__(self) -> str:
        display_list:list[str] = []
        for r_n, register in enumerate(self.registers):
            display_list.append(f"x{r_n:<2} {register}")
        
        lines:list[str] = []
        line_buffer = ""
        term_size:os.terminal_size = os.get_terminal_size()
        for reg_str in display_list:
            if len(line_buffer) + 3 + len(reg_str) > term_size.columns:
                lines.append(line_buffer)
                line_buffer = reg_str
            else:
                if line_buffer == "":
                    line_buffer = reg_str
                else:
                    line_buffer += f"   {reg_str}"
        
        lines.append(line_buffer)
        
        return "\n".join(lines)
            

    def update(self, read_reg_1_adr:Bitx5, read_reg_2_adr:Bitx5, write_reg_adr:Bitx5, write_data:Bitx32, control_reg_write:Bit) -> tuple[Bitx32, Bitx32]:
        read_reg_1_pos_one_hot = decoder5x32(*read_reg_1_adr)
        read_reg_2_pos_one_hot = decoder5x32(*read_reg_2_adr)
        write_reg_pos_one_hot = decoder5x32(*write_reg_adr)

        read_reg_1_pos = one_hot_to_decimal(read_reg_1_pos_one_hot)
        read_reg_2_pos = one_hot_to_decimal(read_reg_2_pos_one_hot)
        write_reg_pos = one_hot_to_decimal(write_reg_pos_one_hot)

        # Read first
        read1 = self.registers[read_reg_1_pos].read_bits()
        read2 = self.registers[read_reg_2_pos].read_bits()


        if control_reg_write and write_reg_pos != 0:
            write_reg = self.registers[write_reg_pos]
            write_reg.write_bits(write_data)

        return read1, read2
        

