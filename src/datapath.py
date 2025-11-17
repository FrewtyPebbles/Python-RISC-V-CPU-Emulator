"""
This file contains the Datapath class
This will contain a memory_unit, an adder, and a program counter
The adder will increment the value held by the program counter, which contains the memory address of the instruction, which will be retrieved by the memory unit
"""
from memory import Bit, Bitx32, Bitx20, Bitx12, Bitx5, Byte, Memory
from memory_unit import memory_unit
from alu import ALU32
from fpu import FPU32
from register_file import RegisterFile
from instruction_memory import PC, InstructionMemory
from encoder_decoder import 

class Datapath:
  mu:memory_unit
  adder:ALU32
  fpu:FPU32
  program_counter:PC
  reg_file:RegisterFile
  
  def __init__(self, memory_unit, fpu32):
    self.mu = memory_unit
    self.adder = fpu32

  def get_instruction(self, address:Bitx32)->str:
    result = self.mu.get_instruction(address)
    return result

  def execute(self, instruction:tuple):
    match instruction():
      #immediate/utility
      case ["lui", input1, input2]:
        """
        input1 is a register
        input2 is a 20-bit immediate value
        This loads input2 into the first 20 bits of input1's storage and fills the lower 12 bits with 0s. 
        """ 
        if not (isinstance(input1, Bitx5) and isinstance(input2, Bitx20)):
          raise TypeError("Invalid input type")
      case ["auipc", input1, input2]:
        """
        input1 is a register
        input2 is a 20-bit immediate value
        This adds the 20-bit value to the program_counter and stores that in input1
        """
        if not (isinstance(input1, Bitx5) and isinstance(input2, Bitx20)):
          raise TypeError("Invalid input type") 
        
      #control
      case ["jal", input1, input2]:
        """
        input1 is a register
        input2 is a label
        The instruction at program_counter + 4 is stored in input1, and we jump to the label in input2
        """
        if not (isinstance(input1, Bitx5) and isinstance(input2, Bitx20)):
          raise TypeError("Invalid input type")
      case ["jalr", input1, input2]:
        """
        input1 is a register
        input2 is an offset of a register, formatted offset(register)
        This stores the address of the instruction at program_counter + 4 in input1, and we jump to offset+register from input2
        """
        if not (isinstance(input1, Bitx5) and isinstance(input2, Bitx5) and isinstance(input3, Bitx12)):
          raise TypeError("Invalid input type") 
      case ["beq", input1, input2, input3]:
        """
        input1 is a register
        input2 is a register
        input3 is a label
        If input1 == input2, jump to label
        """
        if not (isinstance(input1, Bitx5) and isinstance(input2, Bitx5) and isinstance(input3, Bitx12)):
          raise TypeError("Invalid input type") 
      case ["bne", input1, input2, input3]:
        """
        input1 is a register
        input2 is a register
        input3 is a label
        If input1 != input2, jump to label
        """
        if not (isinstance(input1, Bitx5) and isinstance(input2, Bitx5) and isinstance(input3, Bitx12)):
          raise TypeError("Invalid input type")
        
      #memory
      case ["lw", input1, input2, input3]:
        """
        input1 is a register
        input2 and 3 is an offset of a register, register in 2, offset in 3
        This loads from offset+register into input1
        """
        if not (isinstance(input1, Bitx5) and isinstance(input2, Bitx5) and isinstance(input3, Bitx12)):
          raise TypeError("Invalid input type") 
      case ["sw", input1, input2, input3]:
        """
        input1 is a register
        input2 and 3 is an offset of a register, register in 2, offset in 3
        This stores a word from input1 into offset+register
        """
        if not (isinstance(input1, Bitx5) and isinstance(input2, Bitx5) and isinstance(input3, Bitx12)):
          raise TypeError("Invalid input type") 
        
      #arithmetic  
      case ["add", input1, input2, input3]:
        """
        input1 is a register
        input2 is a register
        input3 is a register
        This performs input1 = input2 + input3
        """ 
        if not (isinstance(input1, Bitx5) and isinstance(input2, Bitx5) and isinstance(input3, Bitx5)):
          raise TypeError("Invalid input type")
        
        self.alu.exec(input2, input3, "ADD") #replace input 2 and 3 with the values, write to input1
      case ["sub", input1, input2, input3]:
        """
        input1 is a register
        input2 is a register
        input3 is a register
        This performs input1 = input2 - input3
        """ 
        if not (isinstance(input1, Bitx5) and isinstance(input2, Bitx5) and isinstance(input3, Bitx5)):
          raise TypeError("Invalid input type")
        
        self.alu.exec(input2, input3, "SUB") #replace input 2 and 3 with the values, write to 1
      case ["addi", input1, input2, input3]:
        """
        input1 is a register
        input2 is a register
        input3 is a 12-bit immediate value
        This performs input1 = input2 + input3
        """ 
        if not (isinstance(input1, Bitx5) and isinstance(input2, Bitx5) and isinstance(input3, Bitx12)):
          raise TypeError("Invalid input type")
        
        self.alu.exec(input2, input3, "ADD") #replace input 2 and 3 with the values, write to 1

      #logical
      case ["and", input1, input2, input3]:
        """
        input1 is a register
        input2 is a register
        input3 is a register
        This performs input1 = input2 AND input3
        """ 
        if not (isinstance(input1, Bitx5) and isinstance(input2, Bitx5) and isinstance(input3, Bitx5)):
          raise TypeError("Invalid input type")
      case ["or", input1, input2, input3]:
        """
        input1 is a register
        input2 is a register
        input3 is a register
        This performs input1 = input2 OR input3
        """ 
        if not (isinstance(input1, Bitx5) and isinstance(input2, Bitx5) and isinstance(input3, Bitx5)):
          raise TypeError("Invalid input type")
      case ["xor", input1, input2, input3]:
        """
        input1 is a register
        input2 is a register
        input3 is a register
        This performs input1 = input2 XOR input3
        """ 
        if not (isinstance(input1, Bitx5) and isinstance(input2, Bitx5) and isinstance(input3, Bitx5)):
          raise TypeError("Invalid input type")
      #shifts
      case ["sll", input1, input2, input3]:
        """
        input1 is a register
        input2 is a register
        input3 is a register
        This shifts the contents of input2 to the left by the amount specified in input3, and stores the result in input1
        """ 
        if not (isinstance(input1, Bitx5) and isinstance(input2, Bitx5) and isinstance(input3, Bitx5)):
          raise TypeError("Invalid input type")
      case ["srl", input1, input2, input3]:
        """
        input1 is a register
        input2 is a register
        input3 is a register
        This shifts the contents of input2 to the right by the amount specified in input3, and stores the result in input1
        """ 
        if not (isinstance(input1, Bitx5) and isinstance(input2, Bitx5) and isinstance(input3, Bitx5)):
          raise TypeError("Invalid input type")
      case ["sra", input1, input2, input3]:
        """
        input1 is a register
        input2 is a register
        input3 is a register
        This shifts the contents of input2 to the right by the amount specified in input3, and stores the result in input1
        """ 
        if not (isinstance(input1, Bitx5) and isinstance(input2, Bitx5) and isinstance(input3, Bitx5)):
          raise TypeError("Invalid input type")
      #default case
      case _:
        raise ValueError("Instruction not found")
