from __future__ import annotations
from array import array
from typing import Literal

class Bit:
    """
    This a class so that bits are mutable.
    """

    value:bool
    
    def __init__(self, value:bool = False):
        self.value = value

    def __bool__(self) -> bool:
        return self.value
    
    def __int__(self) -> int:
        return int(self.value)
    
    def __float__(self) -> int:
        return float(self.value)
    
    def __or__(self, other:Bit):
        """
        Analagous to connecting two wires together.
        """
        return Bit(self or other)


class Byte:
    memory: list[Bit]
    size:Literal[8] = 8

    def __init__(self, memory:list[Bit] = None):
        self.memory = memory if memory else [Bit(), Bit(), Bit(), Bit(), Bit(), Bit(), Bit(), Bit()]

    def __getitem__(self, index:int) -> Bit:
        if index < 0 or index >= self.size:
            raise IndexError("index out of memory bounds.")
        return self.memory[index]

    def __setitem__(self, index:int, value:bool):
        self.memory[index].value = value

    def __iter__(self):
        return self
    
    def __len__(self) -> int:
        return self.size
    

class Memory:
    """
    Because this cpu emulator stores registers in little endian,
    this class stores in little endian and itterates in big endian.
    """

    memory:list[Byte]
    size:int
    itterator_index:int

    def __init__(self, size:int = None, memory:list[Byte] = None):
        if size == None and memory == None:
            raise MemoryError("either size or memory must be supplied")
        
        self.size = len(memory) * 8 if size == None else size

        if memory != None and len(memory) != self.size // 8:
            raise MemoryError("memory's size does not match specified size")
        
        self.memory = memory if memory else [Byte() for _ in range(self.size // 8)]
        
        self.itterator_index = 0

    def __getitem__(self, index:int) -> Bit:
        """
        reads the little endian stored bytes reversed to get the correct order.
        """
        if index < 0 or index >= self.size:
            raise IndexError("index out of memory bounds.")
        reversed_index:int = self.size - index
        return self.memory[reversed_index // 8][index % 8]

    def __setitem__(self, index:int, value:bool):
        reversed_index:int = self.size - index
        self.memory[reversed_index // 8][index % 8] = value

    def __iter__(self):
        return self
    
    def __next__(self) -> Bit:
        if self.itterator_index < self.size:
            value = self[self.itterator_index]
            self.itterator_index += 1
            return value
        else:
            raise StopIteration
        
    def __len__(self) -> int:
        return self.size