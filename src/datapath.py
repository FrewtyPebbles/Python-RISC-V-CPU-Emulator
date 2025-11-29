from dataclasses import dataclass
from fpu import FPU
from fpu_control import FPUControl
from memory_unit import MemoryUnit
from rv32f_register_file import RV32FRegisterFile
from rv32i_register_file import RV32IRegisterFile
from instruction_memory import InstructionMemory, PC
from rv32i_alu import RV32IALU
from rv32i_alu_control import RV32IALUControl
from memory import Bit, Bitx32, bin_str_to_bits, bin_to_dec, bin_to_hex, dec_to_hex, int_to_bits, Bits, repr_bits, shift_left_1, shift_left_2, sign_extend, slice_bits
from gates import high_level_mux
from control_unit import (
    OPCODE_AUIPC, OPCODE_FLW, OPCODE_FSW, OPCODE_LUI, OPCODE_STORE, ControlUnit,
    R_TYPE_OPCODES, I_TYPE_OPCODES, S_TYPE_OPCODES, B_TYPE_OPCODES, U_TYPE_OPCODES, J_TYPE_OPCODES
)
from rv32m_alu import RV32MALU
from rv32m_alu_control import RV32MALUControl

class DataPath:
    @dataclass
    class Config:
        show_immediate_values:bool = False
        show_rv32i_registers:bool = False
        show_rv32f_registers:bool = False
        show_step:bool = False
        show_memory:bool = False
        show_reads:bool = False
        show_writes:bool = False

    def __init__(self,
            show_immediate_values:bool = False,
            show_rv32i_registers:bool = False,
            show_rv32f_registers:bool = False,
            show_step:bool = False,
            show_memory:bool = False,
            show_reads:bool = False,
            show_writes:bool = False
        ):
        self.config = self.Config(
            show_immediate_values,
            show_rv32i_registers,
            show_rv32f_registers,
            show_step,
            show_memory,
            show_reads,
            show_writes
        )
        self.pc = PC(int_to_bits(0, 32))
        self.rv32i_register_file = RV32IRegisterFile()
        self.rv32f_register_file = RV32FRegisterFile()
        self.instruction_memory = InstructionMemory()
        self.rv32i_alu = RV32IALU()
        self.rv32m_alu = RV32MALU()
        self.rv32i_alu_control = RV32IALUControl()
        self.rv32m_alu_control = RV32MALUControl()
        self.fpu = FPU()
        self.fpu_control = FPUControl()
        self.control = ControlUnit()
        self.memory = MemoryUnit(memory_in_megabytes=4096)

    def load_program(self, prog: list[str]):
        self.instruction_memory.load(prog)

    def run(self):
        step_count = 0
        while instruction := self.instruction_memory.get_instruction(self.pc.value):
            if self.config.show_step:
                print(f"STEP #{step_count} {{")

            pc_current = self.pc.value
            _, pc_plus_4 = self.rv32i_alu.op_add(pc_current, int_to_bits(4, 32))

            # Decode opcode (LSB-first)
            opcode = instruction[0:7]
            self.control.decode(opcode)

            # Extract registers
            rd  = slice_bits(instruction, 7, 11)
            rs1 = slice_bits(instruction, 15, 19)
            rs2 = slice_bits(instruction, 20, 24)
            funct7 = instruction[25:32]

            if self.config.show_step:
                print("\tpc", bin_to_hex(self.pc.value))
                print("\trd", repr_bits(rd))
                print("\trs1", repr_bits(rs1))
                print("\trs2", repr_bits(rs2))

            if self.control.RegFileSel:

                fp_read_data_1, fp_read_data_2 = self.rv32f_register_file.update(
                    rs1, rs2, rd, bin_str_to_bits("0"*32), 0
                )
                read_data_1 = fp_read_data_1
                read_data_2 = fp_read_data_2

            else:
                # Read registers (no write)
                read_data_1, read_data_2 = self.rv32i_register_file.update(
                    rs1, rs2, rd, bin_str_to_bits("0"*32), 0
                )

            # Immediate generation
            imm_i = self.control.get_imm_i(instruction)
            imm_s = self.control.get_imm_s(instruction)
            imm_b = self.control.get_imm_b(instruction)
            imm_u = self.control.get_imm_u(instruction)
            imm_j = self.control.get_imm_j(instruction)

            if self.config.show_step and self.config.show_immediate_values:
                if opcode in I_TYPE_OPCODES:
                    print("I-Type immediate\n\tBIN:", repr_bits(imm_i), "\n\tdec:", bin_to_dec(imm_i))
                if opcode in S_TYPE_OPCODES:
                    print("S-Type immediate\n\tBIN:", repr_bits(imm_s), "\n\tdec:", bin_to_dec(imm_s))
                if opcode in B_TYPE_OPCODES:
                    print("B-Type immediate\n\tBIN:", repr_bits(imm_b), "\n\tdec:", bin_to_dec(imm_b))
                if opcode in U_TYPE_OPCODES:
                    print("U-Type immediate\n\tBIN:", repr_bits(imm_u), "\n\tdec:", bin_to_dec(imm_u))
                if opcode in J_TYPE_OPCODES:
                    print("J-Type immediate\n\tBIN:", repr_bits(imm_j), "\n\tdec:", bin_to_dec(imm_j))
            
            if self.control.FPUOp:
                # FPU operation
                fpu_op = self.fpu_control.update(
                    self.control.ALUOp,
                    funct7,
                    instruction[12:15],
                    rs2
                )
                zero_flag, execution_result = self.fpu.update(fpu_op, read_data_1, read_data_2)
            elif self.control.MulDivOp:
                # RV32M operation (multiplication/division)
                malu_op = self.rv32m_alu_control.update(
                    self.control.ALUOp,
                    instruction[12:15]
                )
                zero_flag, execution_result = self.rv32m_alu.update(malu_op, read_data_1, read_data_2)
            else:
                # RV32IALU operation
                # RV32IALU source selection
                # Handle LUI/AUIPC specially
                if opcode == OPCODE_LUI:
                    # imm_u is passthrough
                    alu_src1 = int_to_bits(0, 32)
                    alu_src2 = imm_u
                elif opcode == OPCODE_AUIPC:
                    # AUIPC
                    alu_src1 = pc_current
                    alu_src2 = imm_u
                elif opcode == OPCODE_STORE or opcode == OPCODE_FSW:
                    alu_src1 = read_data_1
                    alu_src2 = imm_s
                elif opcode == OPCODE_FLW:
                    # FLW uses rs1 (integer register) for address calculation
                    int_read_data_1, _ = self.rv32i_register_file.update(
                        rs1, rs2, rd, bin_str_to_bits("0"*32), 0
                    )
                    alu_src1 = int_read_data_1
                    alu_src2 = imm_i
                else:
                    alu_src1 = read_data_1
                    alu_src2 = high_level_mux(read_data_2, imm_i, self.control.ALUSrc)

                # RV32IALU operation
                alu_op = self.rv32i_alu_control.update(
                    self.control.ALUOp,
                    instruction[12:15],
                    instruction[30]
                )

                zero_flag, execution_result = self.rv32i_alu.update(alu_op, alu_src1, alu_src2)

            # Memory access
            mem_data = bin_str_to_bits("0"*32)
            if self.control.MemRead:
                mem_data = self.memory.read(execution_result)
                if self.config.show_reads:
                    print(f"MEMORY READ at: 0x{bin_to_hex(execution_result)}  data: 0x{bin_to_hex(mem_data)}")
            if self.control.MemWrite:
                write_data = read_data_2 if self.control.RegFileSel else read_data_2
                if self.config.show_writes:
                    print(f"MEMORY WRITE at: 0x{bin_to_hex(execution_result)}  data: 0x{bin_to_hex(write_data)}")
                self.memory.write(execution_result, write_data)

            # Write-back data selection
            if self.control.FPMemToReg:
                # FP load
                write_back_data = mem_data
            elif self.control.MemToReg:
                # int load
                write_back_data = mem_data
            else:
                # Execution result
                write_back_data = execution_result

            if self.control.FPRegWrite:
                # Write to RV32F register file
                self.rv32f_register_file.update(rs1, rs2, rd, write_back_data, 1)
            elif self.control.RegWrite:
                # Write to RV32I register file
                self.rv32i_register_file.update(rs1, rs2, rd, write_back_data, 1)

            if self.control.FPToInt:
                # Transfer from FP register to Int register
                self.rv32i_register_file.update(rs1, rs2, rd, write_back_data, 1)
            elif self.control.IntToFP:
                # Transfer from Int register to FP register
                self.rv32f_register_file.update(rs1, rs2, rd, write_back_data, 1)

            # Branch and jump logic
            branch_taken = self.control.Branch and zero_flag
            pc_branch = self.rv32i_alu.op_add(pc_current, imm_b)[1]
            next_pc = high_level_mux(pc_plus_4, pc_branch, branch_taken)

            pc_jump = self.rv32i_alu.op_add(pc_current, imm_j)[1]
            self.pc.value = high_level_mux(next_pc, pc_jump, self.control.Jump)

            if self.config.show_step:
                if self.config.show_rv32i_registers:
                    print("Integer Register File:")
                    print(repr(self.rv32i_register_file))
                if self.config.show_rv32f_registers:
                    print("Floating-Point Register File:")
                    print(repr(self.rv32f_register_file))

                if self.config.show_memory:
                    print("Memory Unit:")
                    print(repr(self.memory))
                print("}")

            step_count += 1
