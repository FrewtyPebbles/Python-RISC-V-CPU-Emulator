"""
This file contains the class definition for the memory unit component of the data path
It contains instructions stored in read-only memory, which it knows by address
It takes in an address and outputs an instruction
"""

from memory import Bit, Bitx4, Bitx7, Bitx32, bin_str_to_bits
from encoder_decoder import one_hot_to_decimal

class MemoryUnit:
  FAIL_TUPLE = (1, 2, 3)
  #Note: The use of (1, 2, 3) is just an arbitrary tuple that will fail to trigger an erroneous instruction

  instructions:dict =  [
    
  ]

  def get_instruction(self, instruction:Bitx32) -> tuple:
    opcode = instruction[0][6]
    if opcode == (0,1,1,0,0,1,1): #Type R, needs further investigation
      funct3 = instruction[12][14] #use funct3 to identify 
      if funct3 == (0,0,0): #add or sub, use funct7
        funct7 = instruction[25][31]
        if funct7 == (0,0,0,0,0,0,0): 
          return "add", arguments
        elif funct7 == (0,1,0,0,0,0,0):
          return "sub", arguments
        else:
          return self.FAIL_TUPLE
      elif funct3 == (1,0,1): #srl or sra, use funct7
        funct7 = instruction[25][31]
        if funct7 == (0,0,0,0,0,0,0):
          return "srl", arguments
        elif funct7 == (0,1,0,0,0,0,0):
          return "sra", arguments
        else:
          return self.FAIL_TUPLE
      elif funct3 == (1,0,0): #can only be xor
        return "xor", arguments
      elif funct3 == (1,1,0): #can only be or
        return "or", arguments
      elif funct3 == (1,1,1): #can only be and
        return "and", arguments

    elif opcode == (1,1,0,0,0,1,1): #Type B, needs further investigation
      funct3 = instruction[12][14] #use funct3 to identify
      if funct3 == (0,0,0): 
        return "beq", arguments
      elif funct3 == (0,0,1):
        return "bne", arguments
      else:
        return self.FAIL_TUPLE

    elif opcode == (0,0,1,0,0,1,1): #only instruction in the set with this opcode

      return "addi", arguments 
    
    elif opcode == (0,0,0,0,0,1,1): #only instruction in the set with this opcode

      return "lw", arguments
    
    elif opcode == (1,1,0,0,1,1,1): #only instruction in the set with this opcode

      return "jalr", arguments
    
    elif opcode == (0,1,0,0,0,1,1): #only instruction in the set with this opcode

      return "sw", arguments
    
    elif opcode == (0,1,1,0,1,1,1): #only instruction in the set with this opcode

      return "lui", arguments
    
    elif opcode == (0,0,1,0,1,1,1): #only instruction in the set with this opcode

      return "auipc", arguments
    
    elif opcode == (1,1,0,1,1,1,1): #only instruction in the set with this opcode

      return "jal", arguments
    
    else: #triggers default case in datapath, meaning "instruction not found"
      return self.FAIL_TUPLE 
    
