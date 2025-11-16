from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from memory import (
    Bit, Bitx10, Bitx12, Bitx2, Bitx20, Bitx3, Bitx32, Bitx4, Bitx5, Bitx6, Bitx7, Bitx8,
    bin_str_to_bits, hex_big_to_little_endian, bin_to_hex, dec_to_bin,
    hex_to_bin, octal_to_bin,
)

from abc import ABC, abstractmethod

class TokenType(Enum):
    INSTRUCTION = 0
    LABEL = 1
    DIRECTIVE = 2

class Token:
    """
    The base Token class.

    This contains logic for converting instructions into hex.
    """
    token_type:TokenType
    @abstractmethod
    def to_hex(self) -> str:
        pass
    
    @staticmethod
    def is_int_reg(name:str) -> bool:
        try:
            reg_num:int = int(name.lstrip("x"))
            if 0 <= reg_num <= 31:
                return True
        except ValueError:
            return False

    @staticmethod
    def reg_to_bin(name:str) -> Bitx5:
        try:
            reg_num:int = int(name.lstrip("x"))
            if 0 <= reg_num <= 31:
                return dec_to_bin(reg_num, 5)
            else:
                raise SyntaxError(f"{name} is not within the inclusive range of 0 to 31")
        except ValueError:
            raise SyntaxError(f"{name} is not a valid register")
        
@dataclass
class InstructionData:
    opcode:Bitx7 = None
    funct3:Bitx3 = None
    funct7:Bitx7 = None
    imm_i_0_11:Bitx12 = None
    imm_s_0_4:Bitx5 = None
    imm_s_5_11:Bitx7 = None
    imm_b_1_4:Bitx4 = None
    imm_b_11:Bit = None # this is the 11th bit of the immediate
    imm_b_5_10:Bitx6 = None
    imm_b_12:Bit = None
    imm_u_12_31:Bitx20 = None
    imm_j_12_19:Bitx8 = None
    imm_j_11:Bit = None
    imm_j_1_10:Bitx10 = None
    imm_j_20:Bit = None

R_type_instructions:set[str] = {"add", "sub", "and", "or", "xor", "sll", "srl", "sra"}
I_type_instructions:set[str] = {"addi", "lw", "jalr"}
S_type_instructions:set[str] = {"sw"}
B_type_instructions:set[str] = {"beq", "bne"}
U_type_instructions:set[str] = {"lui", "auipc"}
J_type_instructions:set[str] = {"jal"}

class InstructionType(Enum):
    R = 0
    I = 1
    S = 2
    B = 3
    U = 4
    J = 5

    @classmethod
    def get_instruction_type(cls, instruction:str) -> InstructionType:
        if instruction in R_type_instructions:
            return cls.R
        if instruction in I_type_instructions:
            return cls.I
        if instruction in S_type_instructions:
            return cls.S
        if instruction in B_type_instructions:
            return cls.B
        if instruction in U_type_instructions:
            return cls.U
        if instruction in J_type_instructions:
            return cls.J
        raise SyntaxError(f"instruction type not defined for {instruction}")

InsTyp = InstructionType

class LabelToken(Token):
    token_type = TokenType.LABEL
    name:str
    address:Bitx32
    label_lookup:dict[str, LabelToken] = {}

    def __init__(self, name:str, address:Bitx32):
        self.name = name
        self.address = address

    @classmethod
    def clear_label_lookup(cls):
        cls.label_lookup = {}
    
    @classmethod
    def get_label(cls, label:str) -> LabelToken:
        if label not in cls.label_lookup:
            raise SyntaxError(f"Reference to non-existant label {label} found")
        return cls.label_lookup[label]


class InstructionToken(Token):
    token_type = TokenType.INSTRUCTION
    instruction_type:InstructionType
    instruction:str
    rs1:str
    rs2:str
    rd:str
    immediate:str

    def __init__(self, instruction:str = None, rd:str = None, rs1:str = None, rs2:str = None, immediate:str = None):
        self.instruction = instruction
        self.rs1 = rs1
        self.rs2 = rs2
        self.rd = rd
        self.immediate = immediate
        self.instruction_type = InstructionType.get_instruction_type(self.instruction)

    def get_funct7(self) -> Bitx7:
        h7b = lambda s:hex_to_bin(s, 7)
        match self.instruction:
            case "add"|"xor"|"or"|"and"|"sll"|"srl"|"slt"|"sltu":
                return h7b("00")
            case "sub"|"sra":
                return h7b("20")
            case "mul"|"mulh"|"mulsu"|"mulu"|"div"|"divu"|"rem"|"remu":
                return h7b("01")
            
    def get_funct3(self) -> Bitx3:
        h3b = lambda s:hex_to_bin(s, 3)
        match self.instruction:
            case "add"|"sub"|"addi"|"lb"|"sb"|"beq"|"jalr"|"jal"|"lui"|"auipc"|"ecall"|"ebreak"|"mul":
                return h3b("0")
            case "sll"|"slli"|"lh"|"sh"|"bne"|"mulh":
                return h3b("1")
            case "slt"|"slti"|"lw"|"sw"|"mulsu":
                return h3b("2")
            case "sltu"|"sltiu"|"mulu":
                return h3b("3")
            case "xor"|"xori"|"lbu"|"blt"|"div":
                return h3b("4")
            case "srl"|"sra"|"srli"|"srai"|"lhu"|"bge"|"divu":
                return h3b("5")
            case "or"|"ori"|"bltu"|"rem":
                return h3b("6")
            case "and"|"andi"|"bgeu"|"remu":
                return h3b("7")

    def get_opcode(self) -> Bitx7:
        match self.instruction:
            case "add"|"sub"|"xor"|"or"|"and"|"sll"|"srl"|"sra"|"slt"|"sltu"\
                |"mul"|"mulh"|"mulsu"|"mulu"|"div"|"divu"|"rem"|"remu":
                return bin_str_to_bits("0110011")
            case "addi"|"xori"|"ori"|"andi"|"slli"|"srli"|"srai"|"slti"|"sltiu":
                return bin_str_to_bits("0010011")
            case "lb"|"lh"|"lw"|"lbu"|"lhu":
                return bin_str_to_bits("0000011")
            case "sb"|"sh"|"sw":
                return bin_str_to_bits("0100011")
            case "beq"|"bne"|"blt"|"bge"|"bltu"|"bgeu":
                return bin_str_to_bits("1100011")
            case "jal":
                return bin_str_to_bits("1101111")
            case "jalr":
                return bin_str_to_bits("1100111")
            case "lui":
                return bin_str_to_bits("0110111")
            case "auipc":
                return bin_str_to_bits("0010111")
            case "ecall"|"ebreak":
                return bin_str_to_bits("1110011")

        raise SyntaxError(f"instruction '{self.instruction}' does not have a specified opcode")
    
    def get_imm(self, octal_enabled:bool = True) -> tuple[Bit,...]:
        if self.instruction_type == InsTyp.R:
            return None
        
        length = (12, 12, 12, 20, 20)[self.instruction_type.value]

        if self.immediate == None:
            return bin_str_to_bits("0"*length)
        
        # parse the immediate string into binary
        lead:str = self.immediate[:2].lower()
        if lead == "0x":
            ## Hex
            return hex_to_bin(self.immediate, length)
        elif lead[0] == "0" and octal_enabled:
            ## Octal
            return octal_to_bin(self.immediate, length)
        elif lead[0] == "0":
            ## Not octal because disabled so it is decimal
            zeros_stripped = self.immediate.lstrip("0")
            return dec_to_bin(int(zeros_stripped), length)
        elif lead[1].isalpha():
            ## Label
            return LabelToken.get_label(self.immediate).address
            

    def to_hex(self) -> str:
        match self.instruction_type:
            case InsTyp.R:
                # no immediate
                big_endian_code = tuple(*self.get_funct7(), *self.reg_to_bin(self.rs2), *self.reg_to_bin(self.rs1), *self.get_funct3(), *self.reg_to_bin(self.rd), *self.get_opcode())
                return hex_big_to_little_endian(bin_to_hex(big_endian_code))
            case InsTyp.I:
                # imm[11:0], rs1, funct3, rd, opcode
                imm = self.get_imm()
                big_endian_code = tuple(*imm[0:12], *self.reg_to_bin(self.rs1), *self.get_funct3(), *self.reg_to_bin(self.rd), *self.get_opcode())
                return hex_big_to_little_endian(bin_to_hex(big_endian_code))
            case InsTyp.S:
                # 
                imm = self.get_imm()
                big_endian_code = tuple(*imm[5:12], *self.reg_to_bin(self.rs2), *self.reg_to_bin(self.rs1), *self.get_funct3(), *imm[0:5], *self.get_opcode())
                return hex_big_to_little_endian(bin_to_hex(big_endian_code))
            case InsTyp.B:
                # 
                imm = self.get_imm()
                big_endian_code = tuple(imm[12], *imm[5:11], *self.reg_to_bin(self.rs2), *self.reg_to_bin(self.rs1), *self.get_funct3(), *imm[1:5], imm[11], *self.get_opcode())
                return hex_big_to_little_endian(bin_to_hex(big_endian_code))
            case InsTyp.U:
                # 
                imm = self.get_imm()
                big_endian_code = tuple(*imm[12:32], *self.reg_to_bin(self.rd), *self.get_opcode())
                return hex_big_to_little_endian(bin_to_hex(big_endian_code))
            case InsTyp.J:
                # 
                imm = self.get_imm()
                big_endian_code = tuple(imm[20], *imm[1:11], imm[11], *imm[12:20], *self.reg_to_bin(self.rd), *self.get_opcode())
                return hex_big_to_little_endian(bin_to_hex(big_endian_code))