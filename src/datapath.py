"""
This file contains the Datapath class
This will contain a memory_unit, an adder, and a program counter
The adder will increment the value held by the program counter, which contains the memory address of the instruction, which will be retrieved by the memory unit
"""
from memory import Bit, Bitx32, Byte, Memory
from memory_unit import memory_unit
from fpu import FPU32
#Note to self: this will have to work with the clock as well
class Datapath:
  mu:memory_unit
  adder:FPU32
  
  def __init__(self, memory_unit, fpu32):
    self.mu = memory_unit
    self.adder = fpu32

  def getInstruction(self, address:Bitx32)->str:
    result = self.mu.getInstruction(address)
    return result

  def execute(self, instruction:str):
    match instruction:
      #arithmetic  
      case "add": 
        pass
      case "sub":
        pass
      case "addi":
        pass
      #logical
      case "and":
        pass
      case "or":
        pass
      case "xor":
        pass
      #shifts
      case "sll":
        pass
      case "srl":
        pass
      case "sra":
        pass
      #memory
      case "lw":
        pass
      case "sw":
        pass
      #control
      case "beq":
        pass
      case "bne":
        pass
      case "jal":
        pass
      case "jair":
        pass
      #immediate/utility
      case "lui":
        pass
      case "auipc":
        pass
      #default case
      case _:
        raise ValueError("Instruction not found")
