from register_file import RegisterFile
from instruction_memory import InstructionMemory, PC
from alu import ALU32
from fpu import FPU32
from memory import Bit, Bitx16, Bitx6, bin_str_to_bits, int_to_bits, Bitx32
from gates import high_level_mux
from control_unit_backup import ControlUnit

def shift_left_2(input_bits: Bitx32) -> Bitx32:
    shifted = input_bits[2:] + (Bit(False), Bit(False))
    return shifted

def sign_extend_16_to_32(input16: Bitx16) -> Bitx32:
    sign_bit = input16[0]
    extended = tuple(Bit(sign_bit.value) for _ in range(16)) + input16
    return extended


class DataPath:
    def __init__(self):
        self.register_file = RegisterFile()
        self.pc = PC(int_to_bits(0, 32))
        self.instruction_memory = InstructionMemory()
        self.alu = ALU32()
        self.fpu = FPU32()
        self.control = ControlUnit()

    def update(self, prog:list[str]):
        self.instruction_memory.load(prog)

        write_data = bin_str_to_bits("0"*32)

        ## Emulates a clock:
        while instruction := self.instruction_memory.get_instruction(self.pc.value):
            self.control.decode(instruction[26:32])
            mux_res = high_level_mux(instruction[16:21], instruction[11:16], self.control.RegDst)
            read_data1, read_data2 = self.register_file.update(instruction[21:26], instruction[16:21], mux_res, write_data, self.control.RegWrite)

            sign_extended = sign_extend_16_to_32(instruction[0:16])

            alu_mux = high_level_mux(read_data2, sign_extended, self.control.ALUSrc)

            # ALU would go here, but unfortunately it doesnt work
            
            





            