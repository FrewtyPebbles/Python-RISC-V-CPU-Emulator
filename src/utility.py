from typing import Iterable
from memory import Bit


def bin_to_dec(memory: Iterable[Bit], signed_value:bool = True):
    sum:int = 0
    for i in range(len(memory)):
        sum += memory[i] * pow(2, len(memory) - 1 - i)

    if signed_value and memory[0]: # Check if signed
        max_value:int = pow(2, len(memory))
        sum -= max_value
    
    return sum

def dec_to_bin(value: int, memory_size:int) -> tuple[Bit,...]:
    if value < 0:
        raise ValueError("Only non-negative integers supported for unsigned binary.")

    bool_list = []
    if value == 0:
        bool_list.append(Bit(False))

    # build the binary representation using modulo and division
    while value > 0:
        bool_list.append(Bit(value % 2))  # True if remainder is 1, False if 0
        value //= 2

    # reverse to get MSB first
    bool_list = bool_list[::-1]

    # pad to requested number of bits
    pad_len = memory_size - len(bool_list)
    if pad_len > 0:
        bool_list = [Bit(False)] * pad_len + bool_list

    return tuple(bool_list)

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