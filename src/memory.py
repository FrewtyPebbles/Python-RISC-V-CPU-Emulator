from __future__ import annotations
from array import array
from typing import Iterable, Literal
from typing import Iterable

Bit = Literal[0, 1]

Bits = tuple[Bit,...]
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
Bitx14 = tuple[Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit]
Bitx15 = tuple[Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit]
Bitx16 = tuple[Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit]
Bitx20 = tuple[Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit]
Bitx23 = tuple[Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit]
Bitx24 = tuple[Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit]



class Byte:
    memory: list[Bit]
    size:Literal[8] = 8

    def __init__(self, memory:list[Bit] = None):
        self.memory = memory if memory else [0,0,0,0,0,0,0,0]

    def __getitem__(self, index:int) -> Bit:
        if index < 0 or index >= self.size:
            raise IndexError("index out of memory bounds.")
        return self.memory[index]

    def __setitem__(self, index:int, value:Bit):
        self.memory[index] = value

    def __iter__(self):
        return iter(self.memory)
    
    def __len__(self) -> int:
        return self.size
    
    def write_bits(self, bits:Iterable[Bit]):
        assert len(bits) == len(self)
        for b_n, bit in enumerate(bits):
            self.memory[b_n] = bit

    def read_bits(self) -> Bitx8:
        return tuple(bit for bit in self)
    
    def to_hex(self) -> str:
        return bin_to_hex(self.read_bits())
    
    def __repr__(self):
        # Switch to MSB-First
        return "".join([repr(bit) for bit in reversed(self.memory)])
    
    

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
        self.memory[index // 8][index % 8] = int(bool(value))

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
            self[b_n] = bit

    def read_bits(self) -> tuple[Bit,...]:
        return tuple(bit for bit in self)
    
    def to_hex(self) -> str:
        return bin_to_hex(self.read_bits())
    
    def __repr__(self):
        # Switch to MSB-First
        return " ".join([repr(byte) for byte in reversed(self.memory)])
    

## UTILITY FUNCTIONS


def dec_to_bin(value: int, size: int) -> tuple[Bit, ...]:
    if value < 0:
        raise ValueError("Only non-negative integers supported.")
    bits = []
    for _ in range(size):
        bits.append(int(bool(value & 1)))
        value >>= 1
    return tuple(bits)  # LSB first

def dec_to_bin_signed(value: int, size: int) -> tuple[Bit, ...]:
    min_val = -(1 << (size - 1))
    max_val = (1 << (size - 1)) - 1
    if not (min_val <= value <= max_val):
        raise ValueError(f"Value {value} cannot be represented in {size} bits.")

    if value < 0:
        value = (1 << size) + value

    bits = []
    for _ in range(size):
        bits.append(int(bool(value & 1)))
        value >>= 1
    return tuple(bits)

def bin_to_dec(bits: Iterable[Bit]) -> int:
    return sum(bit << i for i, bit in enumerate(bits))

def dec_to_hex(num:int):
    return hex(num)[2:].upper()

def bin_to_hex(bits:tuple[Bit,...]):
    # build integer from bits
    value = 0
    for i, b in enumerate(bits):
        if b:
            value |= (1 << i)

    # number of hex digits needed (4 bits per hex digit)
    hex_digits = (len(bits) + 3) // 4

    # format with zero-padding
    return f"{value:0{hex_digits}X}"

def hex_to_bin(hex_str:str, bit_length:int) -> tuple[Bit,...]:
    # remove common prefixes like "0x"
    hex_str = hex_str.strip().lower().replace("0x", "")
    
    # convert hex to integer
    value = int(hex_str, 16)
    
    # bitmask to requested bit length (keeps low bits)
    value &= (1 << bit_length) - 1
    
    # convert integer to tuple of booleans (LSB-first, little-endian)
    bits = tuple(int(bool((value >> i) & 1)) for i in range(bit_length))
    
    return bits

def octal_to_bin(octal_str: str, bit_length:int) -> tuple[Bit, ...]:
    if any(c not in '01234567' for c in octal_str):
        raise ValueError(f"Invalid octal digit in '{octal_str}'")

    value = int(octal_str, 8)

    if value >= (1 << bit_length):
        raise ValueError(f"Octal value {octal_str} = {value} exceeds {bit_length} bits")

    return tuple(int(bool((value >> i) & 1)) for i in range(bit_length))

def bin_endian_swap(bits:tuple[Bit,...]) -> tuple[Bit,...]:
    if len(bits) % 8 != 0:
        raise ValueError("Bit length must be a multiple of 8 for endian swap.")

    swapped = []
    for byte_start in range(len(bits)-8, -1, -8):
        # append one byte in the same internal order
        swapped.extend(bits[byte_start:byte_start+8])

    return tuple(swapped)

def hex_endian_swap(hex_str: str) -> str:
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
    return tuple(int(bool(True if bit == "1" else False)) for bit in binary[::-1])

def bits_to_uint32(bits: tuple[Bit, ...]) -> int:
    v = 0
    for i, b in enumerate(bits):
        if bool(b):
            v |= 1 << i
    return v

def int_to_bits(value:int, size:int) -> tuple[Bit,...]:
    return tuple(int(bool((value >> i) & 1)) for i in range(size))

def bits_to_hex_little_endian(bits: tuple[Bit, ...]) -> str:
    if len(bits) % 8 != 0:
        raise ValueError("Bit length must be a multiple of 8")

    # Convert internal LSB-first bits to integer
    value = 0
    for i, b in enumerate(bits):
        value |= (int(b) << i)

    # Convert to big-endian hex (human readable)
    hex_be = f"{value:0{len(bits)//4}X}"

    # Now swap bytes for file output
    return hex_endian_swap(hex_be)

def bits_to_10_tup(bits:tuple[Bit,...]) -> tuple[Literal[1]|Literal[0],...]:
    return tuple([1 if bit else 0 for bit in bits])

def repr_bits(bits:Bits) -> str:
    ret = ""
    for b_n, bit in enumerate(reversed(bits), 1):
        ret += str(bit)
        if b_n % 8 == 0:
            ret += " "

    return ret


def shift_left_2(bits: Bits) -> Bitx32:
    # LSB-first: multiply by 4
    return (0, 0) + bits[:30]

def shift_left_1(bits: Bits) -> Bitx32:
    return (0,) + bits[:31]


def sign_extend(bits: Bits, target_len: int = 32) -> Bitx32:
    # LSB-first: bits[0] = LSB, extend MSBs
    sign_bit = bits[-1]
    extension = tuple(int(bool(sign_bit)) for _ in range(target_len - len(bits)))
    return bits + extension

def slice_bits(instr: Bits, lo: int, hi: int) -> tuple:
    return tuple(instr[i] for i in range(lo, hi + 1))