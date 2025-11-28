from memory import Bit, Bits, Bitx32, Bitx5, bin_to_dec, dec_to_bin, hex_to_bin, shift_left, shift_right, sign_extend
from rv32i_alu import RV32IALU

import fpu_control as fc
import gates as g


BIAS = 127
MANTISSA_BITS = 23
EXP_BITS = 8
SIGN_BIT = 1

class FPU:
    def __init__(self):
        pass
    
    def update(self, operation: Bitx5, read_data_1: Bitx32, read_data_2: Bitx32) -> tuple[Bit, Bitx32]:
        """
        Returns Zero bit signal and 32-bit FPU result.
        Zero bit is 1 for comparison operations that are true.
        """
        match operation:
            case fc.CTRL_FPU_ADD:
                return self.op_add(read_data_1, read_data_2)
            case fc.CTRL_FPU_SUB:
                return self.op_sub(read_data_1, read_data_2)
            case fc.CTRL_FPU_MUL:
                return self.op_mul(read_data_1, read_data_2)
            case _:
                raise RuntimeError(f"FPU Operation not supported {operation}")
    
    @staticmethod
    def compute_zero(res: Bitx32) -> Bit:
        return int(all(b == 0 for b in res))

    @classmethod
    def extract_fields(cls, bits: Bitx32) -> tuple[int, int, int]:
        
        sign = bits[31]
        exp_bits = bits[23:31]
        mantissa_bits = bits[0:23]
        
        exponent = bin_to_dec(exp_bits, signed=False)
        mantissa = bin_to_dec(mantissa_bits, signed=False)
        
        return sign, exponent, mantissa
    
    @classmethod
    def pack_fields(cls, sign: int, exponent: int, mantissa: int) -> Bitx32:
        # Clamp values
        sign = 1 if sign else 0
        exponent = max(0, min(255, exponent))
        mantissa = mantissa & 0x7FFFFF  # mask and keep only 23 bits
        
        # Build 32-bit representation
        mantissa_bits = dec_to_bin(mantissa, 23)
        exp_bits = dec_to_bin(exponent, 8)
        sign_bit = (sign,)
        
        result = mantissa_bits + exp_bits + sign_bit
        return result

    @classmethod
    def op_add(cls, read_data_1: Bitx32, read_data_2: Bitx32) -> tuple[Bit, Bitx32]:
        sign1, exp1, mant1 = cls.extract_fields(read_data_1)
        sign2, exp2, mant2 = cls.extract_fields(read_data_2)
        
        # Handle special cases: zero, infinity, NaN
        if exp1 == 0 and mant1 == 0:
            return cls.compute_zero(read_data_2), read_data_2
        if exp2 == 0 and mant2 == 0:
            return cls.compute_zero(read_data_1), read_data_1
        if exp1 == 255 or exp2 == 255:
            if exp1 == 255:
                return cls.compute_zero(read_data_1), read_data_1
            else:
                return cls.compute_zero(read_data_2), read_data_2
        
        # Implicit 1
        if exp1 == 0:
            sig1 = mant1  # Denormalized
            exp1 = 1
        else:
            sig1 = mant1 | (1 << 23)  # Add implicit 1
        
        if exp2 == 0:
            sig2 = mant2  # Denormalized
            exp2 = 1
        else:
            sig2 = mant2 | (1 << 23)  # Add implicit 1
        
        # Align exponents
        if exp1 > exp2:
            shift = exp1 - exp2
            sig2 = sig2 >> min(shift, 32)  # Shift right until exp match
            exp_result = exp1
        elif exp2 > exp1:
            shift = exp2 - exp1
            sig1 = sig1 >> min(shift, 32)
            exp_result = exp2
        else:
            exp_result = exp1
        
        # Compute
        if sign1 == sign2:
            # Same sign: add
            sig_result = sig1 + sig2
            sign_result = sign1
        else:
            # subtract
            if sig1 >= sig2:
                sig_result = sig1 - sig2
                sign_result = sign1
            else:
                sig_result = sig2 - sig1
                sign_result = sign2
        
        # Handle zero
        if sig_result == 0:
            result = cls.pack_fields(0, 0, 0)
            return cls.compute_zero(result), result
        
        # Normalize: shift left until bit 23 is set
        while sig_result < (1 << 23) and exp_result > 0:
            sig_result <<= 1
            exp_result -= 1
        
        # Shift right if overflow
        while sig_result >= (1 << 24):
            sig_result >>= 1
            exp_result += 1
        
        # Check for overflow
        if exp_result >= 255:
            result = cls.pack_fields(sign_result, 255, 0)  # Infinity
            return cls.compute_zero(result), result
        
        # Check for underflow
        if exp_result <= 0:
            result = cls.pack_fields(sign_result, 0, 0)  # Zero
            return cls.compute_zero(result), result
        
        # Remove implicit 1 and pack
        mant_result = sig_result & 0x7FFFFF
        result = cls.pack_fields(sign_result, exp_result, mant_result)
        return cls.compute_zero(result), result
        
    @classmethod
    def op_sub(cls, read_data_1: Bitx32, read_data_2: Bitx32) -> tuple[Bit, Bitx32]:
        # Flip the sign of the second operand
        sign2, exp2, mant2 = cls.extract_fields(read_data_2)
        flipped = cls.pack_fields(1 - sign2, exp2, mant2)
        return cls.op_add(read_data_1, flipped)
    
    @classmethod
    def op_mul(cls, read_data_1: Bitx32, read_data_2: Bitx32) -> tuple[Bit, Bitx32]:
        sign1, exp1, mant1 = cls.extract_fields(read_data_1)
        sign2, exp2, mant2 = cls.extract_fields(read_data_2)
        
        sign_result = sign1 ^ sign2
        
        # Special cases
        if (exp1 == 0 and mant1 == 0) or (exp2 == 0 and mant2 == 0):
            # Zero
            result = cls.pack_fields(sign_result, 0, 0)
            return cls.compute_zero(result), result
        
        if exp1 == 255 or exp2 == 255:
            # Infinity or NaN
            result = cls.pack_fields(sign_result, 255, 0)
            return cls.compute_zero(result), result
        
        # Implicit 1 for normalized numbers
        if exp1 == 0:
            sig1 = mant1  # Denormalized
            exp1 = 1
        else:
            sig1 = mant1 | (1 << 23)  # Implicit 1
        
        if exp2 == 0:
            sig2 = mant2  # Denormalized
            exp2 = 1
        else:
            sig2 = mant2 | (1 << 23)  # Implicit 1
        
        # Multiply significands
        sig_result = sig1 * sig2
        
        # Add exponents and subtract bias
        exp_result = exp1 + exp2 - BIAS
        
        # Normalize
        if sig_result >= (1 << 47):
            # Shift right by 24 to get 24-bit significand
            sig_result >>= 24
            exp_result += 1
        else:
            # Result < 2.0, shift right by 23
            sig_result >>= 23
        
        # Check for overflow
        if exp_result >= 255:
            result = cls.pack_fields(sign_result, 255, 0)  # Infinity
            return cls.compute_zero(result), result
        
        # Check for underflow
        if exp_result <= 0:
            result = cls.pack_fields(sign_result, 0, 0) # Zero
            return cls.compute_zero(result), result
        
        # Remove implicit 1 and pack result
        mant_result = sig_result & 0x7FFFFF
        result = cls.pack_fields(sign_result, exp_result, mant_result)
        return cls.compute_zero(result), result