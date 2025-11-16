"""
This file contains the class definition for the memory unit component of the data path
It contains instructions stored in read-only memory, which it knows by address
It takes in an address and outputs an instruction
"""

from memory import Bit, Byte, Memory, bin_str_to_bits

Bits = Tuple[Bit, 32]

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
      Tuple(Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(1),Bit(1),Bit(1)): "srl",
      Tuple(Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(1),Bit(0),Bit(0),Bit(0)): "sra",
      #memory
      Tuple(Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(1),Bit(0),Bit(0),Bit(1)): "lw",
      Tuple(Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(1),Bit(0),Bit(1),Bit(0)): "sw",
      #control
      Tuple(Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(1),Bit(0),Bit(1),Bit(1)): "beq",
      Tuple(Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(1),Bit(1),Bit(0),Bit(0)): "bne",
      Tuple(Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(1),Bit(1),Bit(0),Bit(1)): "jal",
      Tuple(Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(1),Bit(1),Bit(1),Bit(0)): "jalr",
      #immediate/utility
      Tuple(Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(1),Bit(1),Bit(1),Bit(1)): "lui",
      Tuple(Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(0),Bit(1),Bit(0),Bit(0),Bit(0),Bit(0)): "auipc"    
  ]

  def getInstruction(self, address:Bits) -> string:
    if address not in self.instructions:
      raise IndexError("Address not found")
    return self.instructions[address]
