"""
This file contains the class definition for the memory unit component of the data path
It contains instructions stored in read-only memory, which it knows by address
It takes in an address and outputs an instruction
"""

from memory import Bit, Bitx32, Byte, Memory, bin_str_to_bits
from encoder_decoder import one_hot_to_decimal

class MemoryUnit:
  instructions:list[str] =  [
      #arithmetic
      "add",
      "sub",
      "addi",
      #logical
      "and",
      "or",
      "xor",
      #shifts
      "sll",
      "srl",
      "sra",
      #memory
      "lw",
      "sw",
      #control
      "beq",
      "bne",
      "jal",
      "jalr",
      #immediate/utility
      "lui",
      "auipc"    
  ]

  def get_instruction(self, address:Bitx32) -> str:
    if address not in self.instructions:
      raise IndexError("Address not found")
    return self.instructions[one_hot_to_decimal(address)]
