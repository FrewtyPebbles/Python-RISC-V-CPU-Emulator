from typing import Iterable
from memory import Bit


def binary_to_integer(memory: Iterable[Bit], signed_value:bool = True):
    sum:int = 0
    for i in range(len(memory)):
        sum += memory[i] * pow(2, len(memory) - 1 - i)

    if signed_value and memory[0]: # Check if signed
        max_value:int = pow(2, len(memory))
        sum -= max_value
    
    return sum