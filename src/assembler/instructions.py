from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from memory import (
    Bit, Bitx10, Bitx12, Bitx2, Bitx20, Bitx3, Bitx32, Bitx4, Bitx5, Bitx6, Bitx7, Bitx8,
    bin_str_to_bits, bin_to_dec, bits_to_hex_little_endian, bits_to_uint32, dec_to_bin_signed, hex_endian_swap, bin_to_hex, dec_to_bin,
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
    def to_hex(self, label_lookup:dict[str, LabelToken]) -> str:
        pass

    def does_codegen(self) -> bool:
        return False
    
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

R_type_instructions:set[str] = {"add", "sub", "and", "or", "xor", "sll", "srl", "sra", "slt", "sltu", "mul", "mulh", "mulsu", "mulu", "div","divu", "rem", "remu"}
I_type_instructions:set[str] = {"addi", "lw", "jalr", "xori", "ori", "andi","slli","srli", "srai", "slti", "sltiu", "lb", "lh", "lw", "lbu", "lhu", "jalr", "ecall", "ebreak"}
S_type_instructions:set[str] = {"sw", "sb", "sh"}
B_type_instructions:set[str] = {"beq", "bne", "blt", "bge", "bltu", "bgeu"}
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

class DirectiveToken(Token):
    token_type = TokenType.DIRECTIVE
    directive:str
    arguments:list[str]
    code_gen_directives:set[str] = {
        ".byte", ".half", ".word", ".ascii", ".ascii", ".asciz",
        ".string", ".word", ".float", ".double", ".align"
    }

    def __init__(self, directive:str, *arguments:list[str]):
        self.directive = directive
        self.arguments = arguments

    def does_codegen(self) -> bool:
        return self.directive in self.code_gen_directives

    def to_hex(self, label_lookup:dict[str, LabelToken]) -> str:
        # TODO
        return bin_to_hex(bin_str_to_bits("0"*32))


class LabelToken(Token):
    token_type = TokenType.LABEL
    name:str
    address:Bitx32
    address_dec:int

    def __init__(self, name:str, address:int|Bitx32):
        self.name = name
        self.address = dec_to_bin(address, 32) if isinstance(address, int) else address
        self.address_dec = address if isinstance(address, int) else bin_to_dec(address)


class InstructionToken(Token):
    token_type = TokenType.INSTRUCTION
    instruction_type:InstructionType
    instruction:str
    rs1:str
    rs2:str
    rd:str
    immediate:str
    address:Bitx32
    address_dec:int

    def __init__(self, address:int|Bitx32, instruction:str = None, *args:list[str]):
        self.instruction = instruction
        self.instruction_type = InstructionType.get_instruction_type(self.instruction)
        rd, rs1, rs2, immediate = None, None, None, None
        match self.instruction_type:
            case InsTyp.R:
                rd = args[0]
                rs1 = args[1]
                rs2 = args[2]
                immediate = None
            case InsTyp.I:
                rd = args[0]
                immediate, rs1 = self.separate_imm_offset(args[1])
                if len(args) > 2:
                    immediate = args[2]
            case InsTyp.S:
                rd = None
                immediate, rs1 = self.separate_imm_offset(args[1])
                rs2 = args[0]
            case InsTyp.B:
                rd = None
                rs1 = args[0]
                rs2 = args[1]
                immediate = args[2]
            case InsTyp.U|InsTyp.J:
                rd = args[0]
                rs1 = None
                rs2 = None
                immediate = args[1]

        self.rs1 = rs1
        self.rs2 = rs2
        self.rd = rd
        self.immediate = immediate
        self.address = dec_to_bin(address, 32) if isinstance(address, int) else address
        self.address_dec = address if isinstance(address, int) else bin_to_dec(address)

    def separate_imm_offset(self, imm:str) -> tuple[str, str]:
        """
        returns immediate, read_reg
        """
        if "(" in imm and ")" in imm:
            parts = imm.split("(")
            reg = parts[1][:-1]
            return parts[0], reg
        else:
            if self.is_int_reg(imm):
                return None, imm
            else:
                return imm, None
            
    def does_codegen(self) -> bool:
        return True

    def get_funct7(self) -> Bitx7:
        h7b = lambda s: hex_to_bin(s, 7)
        match self.instruction:
            case "add"|"xor"|"or"|"and"|"sll"|"srl"|"slt"|"sltu":
                return h7b("00")
            case "sub"|"sra":
                return h7b("20")
            case "mul"|"mulh"|"mulsu"|"mulu"|"div"|"divu"|"rem"|"remu":
                return h7b("01")
        raise SyntaxError(f"instruction '{self.instruction}' does not have a specified funct7")
            
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
        raise SyntaxError(f"instruction '{self.instruction}' does not have a specified funct3")

    def get_opcode(self) -> Bitx7:
        match self.instruction:
            case "add"|"sub"|"xor"|"or"|"and"|"sll"|"srl"|"sra"|"slt"|"sltu"\
                |"mul"|"mulh"|"mulsu"|"mulu"|"div"|"divu"|"rem"|"remu":
                return hex_to_bin("33", 7)
            case "addi"|"xori"|"ori"|"andi"|"slli"|"srli"|"srai"|"slti"|"sltiu":
                return hex_to_bin("13", 7)
            case "lb"|"lh"|"lw"|"lbu"|"lhu":
                return hex_to_bin("03", 7)
            case "sb"|"sh"|"sw":
                return hex_to_bin("23", 7)
            case "beq"|"bne"|"blt"|"bge"|"bltu"|"bgeu":
                return hex_to_bin("63", 7)
            case "jal":
                return hex_to_bin("6F", 7)
            case "jalr":
                return hex_to_bin("67", 7)
            case "lui":
                return hex_to_bin("37", 7)
            case "auipc":
                return hex_to_bin("17", 7)
            case "ecall"|"ebreak":
                return hex_to_bin("73", 7)

        raise SyntaxError(f"instruction '{self.instruction}' does not have a specified opcode")
    
    def get_imm(self, label_lookup: dict[str, 'LabelToken'], octal_enabled: bool = True) -> tuple[Bit, ...]:
        # R-type has no immediate
        if self.instruction_type == InsTyp.R:
            return None

        length = 32  # always return 32 bits for slicing convenience

        # Default immediate is zero
        if self.immediate is None:
            return tuple(0 for _ in range(length))

        imm_str = self.immediate.strip().lower()

        # --- Parse the immediate ---
        if imm_str.startswith("0x"):
            # Hexadecimal
            value = int(imm_str, 16)
        elif imm_str.startswith("0") and octal_enabled and len(imm_str) > 1:
            # Octal
            value = int(imm_str, 8)
        elif imm_str.startswith("0") and len(imm_str) > 1:
            # Leading zero but octal disabled → decimal
            value = int(imm_str.lstrip("0"), 10)
        elif imm_str in label_lookup:
            # Label
            value = label_lookup[imm_str].address_dec
        else:
            # Decimal signed
            value = int(imm_str, 10)

        # --- Convert to 32-bit tuple LSB-first ---
        bits = tuple(Bit((value >> i) & 1) for i in range(length))
        return bits
            

    def to_hex(self, label_lookup:dict[str, LabelToken]) -> str:
        """
        Build the 32-bit instruction as a LSB-first tuple of Bit objects,
        then convert with bits_to_hex_little_endian.
        """
        match self.instruction_type:
            case InsTyp.R:
                # LSB-first: opcode, rd, funct3, rs1, rs2, funct7
                bits = tuple([
                    *self.get_opcode(),
                    *self.reg_to_bin(self.rd),
                    *self.get_funct3(),
                    *self.reg_to_bin(self.rs1),
                    *self.reg_to_bin(self.rs2),
                    *self.get_funct7()
                ])
                return bin_to_hex(bits)

            case InsTyp.I:
                # LSB-first: opcode, rd, funct3, rs1, imm[0:12]
                imm = self.get_imm(label_lookup)
                bits = tuple([
                    *self.get_opcode(),
                    *self.reg_to_bin(self.rd),
                    *self.get_funct3(),
                    *self.reg_to_bin(self.rs1),
                    *imm[0:12]
                ])
                return bin_to_hex(bits)

            case InsTyp.S:
                # LSB-first: opcode, imm[0:5], funct3, rs1, rs2, imm[5:12]
                imm = self.get_imm(label_lookup)
                bits = tuple([
                    *self.get_opcode(),
                    *imm[0:5],
                    *self.get_funct3(),
                    *self.reg_to_bin(self.rs1),
                    *self.reg_to_bin(self.rs2),
                    *imm[5:12]
                ])
                return bin_to_hex(bits)

            case InsTyp.B:
                # LSB-first: opcode, imm[11], imm[1:5], funct3, rs1, rs2, imm[5:11], imm[12]
                imm = self.get_imm(label_lookup)
                bits = tuple([
                    *self.get_opcode(),
                    imm[11],
                    *imm[1:5],
                    *self.get_funct3(),
                    *self.reg_to_bin(self.rs1),
                    *self.reg_to_bin(self.rs2),
                    *imm[5:11],
                    imm[12]
                ])
                return bin_to_hex(bits)

            case InsTyp.U:
                # LSB-first: opcode, rd, imm[12:32]
                imm = self.get_imm(label_lookup)
                bits = tuple([
                    *self.get_opcode(),
                    *self.reg_to_bin(self.rd),
                    *imm[12:32]
                ])
                return bin_to_hex(bits)

            case InsTyp.J:
                # LSB-first: opcode, rd, imm[12:20], imm[11], imm[1:11], imm[20]
                imm = self.get_imm(label_lookup)
                bits = tuple([
                    *self.get_opcode(),
                    *self.reg_to_bin(self.rd),
                    *imm[12:20],
                    imm[11],
                    *imm[1:11],
                    imm[20]
                ])
                return bin_to_hex(bits)