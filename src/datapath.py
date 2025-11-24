from register_file import RegisterFile
from instruction_memory import InstructionMemory, PC
from alu import ALU
from alu_control import ALUControl
from memory import Bit, Bitx32, bin_str_to_bits, bin_to_dec, bin_to_hex, dec_to_hex, int_to_bits, Bits, repr_bits
from gates import high_level_mux
from control_unit import ControlUnit


def shift_left_2(bits: Bits) -> Bitx32:
    # LSB-first: shift left means append two 0 LSBs and drop two MSBs
    return bits[2:] + (0, 0)


def sign_extend(bits: Bits, target_len: int = 32) -> Bitx32:
    # LSB-first: bits[0] = LSB, extend MSBs
    sign_bit = bits[-1]
    extension = tuple(int(bool(sign_bit)) for _ in range(target_len - len(bits)))
    return bits + extension


class DataPath:
    def __init__(self):
        self.pc = PC(int_to_bits(0, 32))
        self.register_file = RegisterFile()
        self.instruction_memory = InstructionMemory()
        self.alu = ALU()
        self.alu_control = ALUControl()
        self.control = ControlUnit()
        self.memory = {}  # Simple memory dict addr -> Bitx32

    def load_program(self, prog: list[str]):
        self.instruction_memory.load(prog)

    def run(self):
        while instruction := self.instruction_memory.get_instruction(self.pc.value):
            pc_current = self.pc.value
            _, pc_plus_4 = self.alu.op_add(pc_current, int_to_bits(4, 32))

            # === Decode opcode (LSB-first) ===
            opcode = instruction[0:7]  # bits 0-6 = LSB-first
            self.control.decode(opcode)

            # === Extract registers ===
            rd  = instruction[7:12] # bits 7-11
            rs1 = instruction[12:17] # bits 12-16
            rs2 = instruction[17:22] # bits 17-21

            print("pc", bin_to_hex(self.pc.value))
            print("rd", repr_bits(rd))
            print("rs1", repr_bits(rs1))
            print("rs2", repr_bits(rs2))

            read_data_1, read_data_2 = self.register_file.update(
                rs1, rs2, rd, bin_str_to_bits("0"*32), 0
            )

            # === Immediate generation (LSB-first) ===
            imm_i = sign_extend(instruction[0:12], 32)  # I-type
            imm_s = sign_extend(instruction[0:7] + instruction[20:25], 32)  # S-type

            print("imm_i", imm_i, "[dec:", bin_to_dec(imm_i), "]")

            # B-type
            b_bits = (
                0,
                *instruction[20:24], # imm[4:1]
                *instruction[1:7], # imm[10:5]
                instruction[24], # imm[11]
                instruction[0] # imm[12]
            )
            imm_b = shift_left_2(sign_extend(b_bits, 32))

            # U-type
            imm_u = instruction[0:20] + (0,) * 12

            # J-type
            j_bits = (
                0, # imm[0] = 0
                *instruction[1:11], # imm[10:1]
                instruction[11], # imm[11]
                *instruction[12:20], # imm[19:12]
                instruction[0] # imm[20]
            )
            imm_j = shift_left_2(sign_extend(j_bits, 32))

            # === ALU input selection ===
            alu_src2 = high_level_mux(read_data_2, imm_i, self.control.ALUSrc)

            # === ALU operation ===
            alu_op = self.alu_control.update(
                self.control.ALUOp, instruction[17:20], instruction[30]
            )
            zero_flag, alu_result = self.alu.update(alu_op, read_data_1, alu_src2)

            # === Memory access ===
            mem_data = bin_str_to_bits("0"*32)
            if self.control.MemRead:
                mem_data = self.memory_read(alu_result)
            if self.control.MemWrite:
                self.memory_write(alu_result, read_data_2)

            # === Write-back selection ===
            write_back_data = high_level_mux(alu_result, mem_data, self.control.MemToReg)
            if self.control.RegWrite:
                self.register_file.update(rs1, rs2, rd, write_back_data, 1)

            # === Branch and jump logic ===
            branch_taken = self.control.Branch and zero_flag
            pc_branch = self.alu.op_add(pc_current, imm_b)[1]
            next_pc = high_level_mux(pc_plus_4, pc_branch, branch_taken)

            pc_jump = self.alu.op_add(pc_current, imm_j)[1]
            self.pc.value = high_level_mux(next_pc, pc_jump, self.control.Jump)

    def memory_read(self, addr: Bitx32) -> Bitx32:
        key = int("".join(str(b) for b in addr[::-1]), 2)  # LSB-first
        return self.memory.get(key, bin_str_to_bits("0"*32))

    def memory_write(self, addr: Bitx32, data: Bitx32):
        key = int("".join(str(b) for b in addr[::-1]), 2)  # LSB-first
        self.memory[key] = data
