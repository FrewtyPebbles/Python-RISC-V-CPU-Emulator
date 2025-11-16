from __future__ import annotations
from array import array
from typing import Iterable, Literal
from typing import Iterable

class Bit:
    """
    This a class so that bits are mutable.
    """

    value:bool
    
    def __init__(self, value:bool = False):
        self.value = bool(value)

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
    
    def to_hex(self) -> str:
        return bin_to_hex(self.read_bits())
    
    def __repr__(self):
        return "1" if self.value else "0"

Bitx32 = tuple[Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit]
Bitx2 = tuple[Bit,Bit]
Bitx3 = tuple[Bit,Bit,Bit]
Bitx4 = tuple[Bit,Bit,Bit,Bit]
Bitx5 = tuple[Bit,Bit,Bit,Bit,Bit]
Bitx6 = tuple[Bit,Bit,Bit,Bit,Bit,Bit]
Bitx7 = tuple[Bit,Bit,Bit,Bit,Bit,Bit,Bit]
Bitx8 = tuple[Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit]
Bitx9 = tuple[Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit]
Bitx10 = tuple[Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit]
Bitx11 = tuple[Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit]
Bitx12 = tuple[Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit]
Bitx13 = tuple[Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit]
Bitx20 = tuple[Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit]

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
    
    def write_bits(self, bits:Iterable[Bit]):
        assert len(bits) == len(self)
        for b_n, bit in enumerate(bits):
            self.memory[b_n].value = bit.value

    def read_bits(self) -> Bitx8:
        return tuple(bit for bit in self)
    
    def to_hex(self) -> str:
        return bin_to_hex(self.read_bits())
    
    def __repr__(self):
        return "".join([repr(bit) for bit in self.memory])
    
    

class Memory:
    """
    Because this cpu emulator stores data in little endian,
    this class stores in little endian and itterates in big endian.
    """

    memory:list[Byte]
    size:int
    itterator_index:int

    def __init__(self, size:int):
        self.size = size
        self.memory = [Byte() for _ in range(size // 8)]
        
        self.itterator_index = 0

    def __getitem__(self, index:int) -> Bit:
        """
        reads the little endian stored bytes reversed to get the correct order.
        """
        if index < 0 or index >= self.size:
            raise IndexError("index out of memory bounds.")
        return self.memory[index // 8][index % 8]

    def __setitem__(self, index:int, value:bool):
        self.memory[index // 8][index % 8] = bool(value)

    def __iter__(self):
        return self
    
    def __next__(self) -> Bit:
        if self.itterator_index < self.size:
            value = self[self.itterator_index]
            self.itterator_index += 1
            return value
        else:
            self.itterator_index = 0
            raise StopIteration
        
    def __len__(self) -> int:
        return self.size

    def write_bits(self, bits:Iterable[Bit]):
        assert len(bits) == len(self)
        for b_n, bit in enumerate(bits):
            self[b_n].value = bit.value

    def read_bits(self) -> tuple[Bit,...]:
        return tuple(Bit(bit.value) for bit in self)
    
    def to_hex(self) -> str:
        return bin_to_hex(self.read_bits())
    
    def __repr__(self):
        return " ".join([repr(byte) for byte in self.memory])
    

## UTILITY FUNCTIONS


def dec_to_bin(value: int, size: int) -> tuple[Bit, ...]:
    if value < 0:
        raise ValueError("Only non-negative integers supported.")
    bits = []
    for _ in range(size):
        bits.append(Bit(value & 1))
        value >>= 1
    return tuple(bits)  # LSB first

def bin_to_dec(bits: Iterable[Bit]) -> int:
    value = 0
    for i, b in enumerate(bits):
        value += int(b) << i
    return value

def dec_to_hex(num:int):
    return hex(num)[2:].upper()

def bin_to_hex(bits:tuple[Bit,...]):
    return dec_to_hex(bin_to_dec(bits))

def hex_to_bin(hex_str:str, bit_length:int) -> tuple[Bit,...]:
    # remove common prefixes like "0x"
    hex_str = hex_str.strip().lower().replace("0x", "")
    
    # convert hex to integer
    value = int(hex_str, 16)
    
    # bitmask to requested bit length (keeps low bits)
    value &= (1 << bit_length) - 1
    
    # convert integer to tuple of booleans (LSB-first, little-endian)
    bits = tuple(Bit((value >> i) & 1) for i in range(bit_length))
    
    return bits

def octal_to_bin(octal_str: str, bit_length:int) -> tuple[Bit, ...]:
    if any(c not in '01234567' for c in octal_str):
        raise ValueError(f"Invalid octal digit in '{octal_str}'")

    value = int(octal_str, 8)

    if value >= (1 << bit_length):
        raise ValueError(f"Octal value {octal_str} = {value} exceeds {bit_length} bits")

    return tuple(Bit((value >> i) & 1) for i in range(bit_length))

def bin_big_to_little_endian(bits:tuple[Bit,...]) -> tuple[Bit,...]:
    length:int = len(bits)
    ret_bits:list[Bit] = []
    for i in range(length):
        reverse_i:int = length - i
        ret_bits.append(bits[(reverse_i // 8) - 1 + i % 8])
    
    return tuple(ret_bits)

def hex_big_to_little_endian(hex_str: str) -> str:
    # Ensure even length by padding with a leading zero if needed
    if len(hex_str) % 2 != 0:
        raise SyntaxError(f"The provided hex '{hex_str}' has an odd number of hex digits")

    # split the hex into bytes which is 2 digits per byte
    bytes_list = [hex_str[i:i+2] for i in range(0, len(hex_str), 2)]

    little_endian_bytes = bytes_list[::-1]

    # make back into a string
    return ''.join(little_endian_bytes).upper()

def is_int(s:str) -> bool:
    try:
        int(s)
        return True
    except ValueError:
        return False
    
def bin_str_to_bits(binary:str) -> tuple[Bit,...]:
    return tuple(Bit(True if bit == "1" else False) for bit in binary)