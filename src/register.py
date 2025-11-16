from typing import Literal
from memory import Memory, Byte, Bit, bin_to_dec

class Register(Memory):
    """
    Base Register class for shared methods
    """
    

class Register8bit(Register):
    def __init__(self, memory:list[Byte] = None):
        super().__init__(8, memory)

class Register16bit(Register):
    def __init__(self, memory:list[Byte] = None):
        super().__init__(16, memory)

class Register32bit(Register):
    def __init__(self, memory:list[Byte] = None):
        super().__init__(32, memory)

class FloatRegister32bit(Register32bit):
    EXPONENT_BIAS:Literal[127] = 127

    def __init__(self, memory:list[Byte] = None):
        super().__init__(32, memory)


    @property
    def sign_bit(self) -> Bit:
        return self[0]
    
    @property
    def exponent_bits(self) -> list[Bit]:
        return [self[i] for i in range(1, 8)]
    
    @property
    def mantissa_bits(self) -> list[Bit]:
        return [self[i] for i in range(8, 32)]
    
    @property
    def fraction(self) -> float:
        fraction_bits:list[Bit] = self.mantissa_bits
        sum:float = 0
        for i in range(23):
            sum += float(fraction_bits[i]) * pow(2, -(i + 1))

        return sum
    
    def __float__(self):
        exponent:float = float(bin_to_dec(self.exponent_bits, True))
        fraction:float = self.fraction
        return (-1.0 if self.sign_bit else 1.0) * (1.0 + fraction) * pow(2.0, exponent - self.EXPONENT_BIAS)

