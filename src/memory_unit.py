"""
This file contains the class definition for the memory unit component of the data path
It contains instructions stored in read-only memory, which it knows by address
It takes in an address and outputs an instruction
"""

from memory import Bit, Bitx4, Bitx7, Bitx32, bits_to_10_tup
from encoder_decoder import one_hot_to_decimal

class MemoryUnit:
  FAIL_TUPLE = (1, 2, 3)
  #Note: The use of (1, 2, 3) is just an arbitrary tuple that will fail to trigger an erroneous instruction

  def get_instruction(self, instruction:Bitx32) -> tuple:
    opcode = bits_to_10_tup(instruction[0][6])
    rd = instruction[7][11]
    rs1 = instruction[15][19]    #these three are the addresses of the write, read1, and read2 registers
    rs2 = instruction[20][24]
    if opcode == (0,1,1,0,0,1,1): #Type R, needs further investigation
      funct3 = bits_to_10_tup(instruction[12][14]) #use funct3 to identify 
      if funct3 == (0,0,0): #add or sub, use funct7
        funct7 = bits_to_10_tup(instruction[25][31])
        if funct7 == (0,0,0,0,0,0,0): 
          return "add", rd, rs1, rs2
        elif funct7 == (0,1,0,0,0,0,0):
          return "sub", rd, rs1, rs2
        else:
          return self.FAIL_TUPLE
      elif funct3 == (1,0,1): #srl or sra, use funct7
        funct7 = bits_to_10_tup(instruction[25][31])
        if funct7 == (0,0,0,0,0,0,0):
          return "srl", rd, rs1, rs2
        elif funct7 == (0,1,0,0,0,0,0):
          return "sra", rd, rs1, rs2
        else:
          return self.FAIL_TUPLE
      elif funct3 == (1,0,0): #can only be xor
        return "xor", rd, rs1, rs2
      elif funct3 == (1,1,0): #can only be or
        return "or", rd, rs1, rs2
      elif funct3 == (1,1,1): #can only be and
        return "and", rd, rs1, rs2

    elif opcode == (1,1,0,0,0,1,1): #Type B, needs further investigation
      funct3 = bits_to_10_tup(instruction[12][14]) #use funct3 to identify
      imm = instruction[7][11]
      rs1 = instruction[15][19] 
      rs2 = instruction[20][24]
      if funct3 == (0,0,0): 
        return "beq", rs1, rs2, imm
      elif funct3 == (0,0,1):
        return "bne", rs1, rs2, imm
      else:
        return self.FAIL_TUPLE

    elif opcode == (0,0,1,0,0,1,1): #only instruction in the set with this opcode
      rd = instruction[7][11]
      rs1 = instruction[15][19]
      imm = instruction[20][31]
      return "addi", rd, rs1, imm 
    
    elif opcode == (0,0,0,0,0,1,1): #only instruction in the set with this opcode
      rd = instruction[7][11]
      rs1 = instruction[15][19]
      imm = instruction[20][31]
      return "lw", rd, rs1, imm
    
    elif opcode == (1,1,0,0,1,1,1): #only instruction in the set with this opcode
      rd = instruction[7][11]
      rs1 = instruction[15][19]
      imm = instruction[20][31]
      return "jalr", rd, rs1, imm
    
    elif opcode == (0,1,0,0,0,1,1): #only instruction in the set with this opcode
      imm = instruction[7][11] + instruction[25][31] 
      rs1 = instruction[15][19]
      rs2 = instruction[20][24]
      return "sw", imm, rs1, rs2
    
    elif opcode == (0,1,1,0,1,1,1): #only instruction in the set with this opcode
      rd = instruction[7][11]
      imm = instruction[12][31]
      return "lui", rd, imm
    
    elif opcode == (0,0,1,0,1,1,1): #only instruction in the set with this opcode
      rd = instruction[7][11]
      imm = instruction[12][31]
      return "auipc", rd, imm
    
    elif opcode == (1,1,0,1,1,1,1): #only instruction in the set with this opcode
      rd = instruction[7][11]
      imm = instruction[12][31] 
      return "jal", rd, imm
    
    else: #triggers default case in datapath, meaning the instruction was not found
      return self.FAIL_TUPLE 