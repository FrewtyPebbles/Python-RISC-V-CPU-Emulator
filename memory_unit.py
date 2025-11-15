"""
This file contains the class definition for the memory unit component of the data path
It contains instructions stored in read-only memory, which it knows by address
It takes in an address and outputs an instruction
"""

from memory import Bit, Byte, Memory

class MemoryUnit:
  instructions:dict = 
    {
      #filled later
    }

  #address will need to be 64-bit... not sure if I wanna do a 2-tuple of 32-bits or something else, this is just to get something down for now
  def getInstruction(self, address:tuple()) -> string:
    if address not in self.instructions:
      raise IndexError("Address not found")
    return self.instructions[address]
