from memory import Bit, Bitx32, Bitx5, bin_to_dec, dec_to_bin, hex_to_bin, sign_extend
from alu import ALU

import fpu_control as fc
import gates as g

EXP_MAX = (1,1,1,1,1,1,1,1)
EXP_ZERO = (0,0,0,0,0,0,0,0)
MANT_ZERO = (0,) * 23
ZERO_32 = (0,) * 32

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
            # TODO:
            case fc.CTRL_FPU_DIV:
                return self.op_div(read_data_1, read_data_2)
            case fc.CTRL_FPU_SQRT:
                return self.op_sqrt(read_data_1)
            case fc.CTRL_FPU_MIN:
                return self.op_min(read_data_1, read_data_2)
            case fc.CTRL_FPU_MAX:
                return self.op_max(read_data_1, read_data_2)
            case fc.CTRL_FPU_EQ:
                return self.op_eq(read_data_1, read_data_2)
            case fc.CTRL_FPU_LT:
                return self.op_lt(read_data_1, read_data_2)
            case fc.CTRL_FPU_LE:
                return self.op_le(read_data_1, read_data_2)
            case _:
                raise RuntimeError(f"FPU Operation not supported {operation}")
    
    @staticmethod
    def compute_zero(res: Bitx32) -> Bit:
        return int(all(b == 0 for b in res))
    
    @classmethod
    def op_add(cls, read_data_1: Bitx32, read_data_2: Bitx32) -> tuple[Bit, Bitx32]:
        # Get components
        rd1 = read_data_1
        rd2 = read_data_2

        sign_rd1 = rd1[31]
        exp_rd1 = rd1[23:31]
        mant_rd1 = rd1[0:23]

        sign_rd2 = rd2[31]
        exp_rd2 = rd2[23:31]
        mant_rd2 = rd2[0:23]

        # Zero
        if exp_rd1 == 0 and cls.compute_zero(mant_rd1):
            return cls.compute_zero(rd2), rd2
        if exp_rd2 == 0 and cls.compute_zero(mant_rd2):
            return cls.compute_zero(rd1), rd1

        # Infinity
        if exp_rd1 == EXP_MAX:
            return cls.compute_zero(rd1), rd1
        if exp_rd2 == EXP_MAX:
            return cls.compute_zero(rd2), rd2
        
        # Add leading 1 for normalized nums
        mant_rd1_full = (1,) + mant_rd1 if exp_rd1 != EXP_ZERO else (0,) + mant_rd1
        mant_rd2_full = (1,) + mant_rd2 if exp_rd2 != EXP_ZERO else (0,) + mant_rd2

        # Adjust exponents if denormalized
        if exp_rd1 == EXP_ZERO:
            exp_rd1 = (1,0,0,0,0,0,0,0)
        if exp_rd2 == EXP_ZERO:
            exp_rd2 = (1,0,0,0,0,0,0,0)

        # Align mantissas by shifting the smaller exponent
        if g.high_level_min(exp_rd1, exp_rd2) == exp_rd2:
            shift = ALU.op_sub(sign_extend(exp_rd1, 32), sign_extend(exp_rd2, 32))[1]
            shift_dec = bin_to_dec(shift, True)
            if shift_dec < 24:
                mant_rd2_full = (0,) * shift_dec + mant_rd2_full
                mant_rd2_full = mant_rd2_full[:24]
            else:
                mant_rd2_full = (0,) * 24
            exp_result = exp_rd1
        elif g.high_level_min(exp_rd1, exp_rd2) == exp_rd1:
            shift = ALU.op_sub(sign_extend(exp_rd2, 32), sign_extend(exp_rd1, 32))[1]
            shift_dec = bin_to_dec(shift, True)
            if shift_dec < 24:
                mant_rd1_full = (0,) * shift_dec + mant_rd1_full
                mant_rd1_full = mant_rd1_full[:24]
            else:
                mant_rd1_full = (0,) * 24
            exp_result = exp_rd2
        else:
            exp_result = exp_rd1

        # add / subtract
        if sign_rd1 == sign_rd2:
            mant_result = ALU.op_add(sign_extend(mant_rd1_full), sign_extend(mant_rd2_full))[1][:24]
            sign_result = sign_rd1
        else:
            # Different signs
            if g.high_level_min(mant_rd1_full, mant_rd2_full) == mant_rd2_full or mant_rd1_full == mant_rd2_full:
                mant_result = ALU.op_sub(sign_extend(mant_rd1_full), sign_extend(mant_rd2_full))[1][:24]
                sign_result = sign_rd1
            else:
                mant_result = ALU.op_sub(sign_extend(mant_rd2_full), sign_extend(mant_rd1_full))[1][:24]
                sign_result = sign_rd2

        # Handle zero
        if mant_result == MANT_ZERO:
            return ZERO_32
        
        bit_pos = len(mant_result) - 1

        if bit_pos > 23:
            # overflow
            shift_dec = bit_pos - 23
            mant_result = ALU.op_srl(sign_extend(mant_result), dec_to_bin(shift_dec, 32))[1][:24]
            exp_result = ALU.op_add(sign_extend(exp_result), dec_to_bin(shift_dec, 32))[1][:8]
        elif bit_pos < 23:
            # normalize
            shift_dec = 23 - bit_pos
            shift = dec_to_bin(shift_dec, 8)
            if g.high_level_min(exp_result, shift) == shift:
                mant_result = ALU.op_sll(sign_extend(mant_result), sign_extend(shift))[1][:24]
                exp_result = ALU.op_sub(sign_extend(exp_result), sign_extend(shift))[1][:8]
            else:
                # denormalize
                mant_result = ALU.op_sll(sign_extend(mant_result), ALU.op_sub(sign_extend(exp_result), dec_to_bin(1, 32))[1])[1][:24]
                exp_result = EXP_ZERO

        # Overflow check
        if g.high_level_min(exp_result, EXP_MAX) == EXP_MAX or exp_result == EXP_MAX:
            exp_result = EXP_MAX
            mant_result = MANT_ZERO

        # Remove leading 1 when normalized
        if exp_result != EXP_ZERO:
            mant_result = ALU.op_and(sign_extend(mant_result), hex_to_bin("7FFFFF", 32))[1][:23]

        # pack the result back into IEEE754
        result = mant_result + exp_result + (sign_result,)

        return cls.compute_zero(result), result
        

    @classmethod
    def op_sub(cls, read_data_1: Bitx32, read_data_2: Bitx32) -> Bitx32:
        rd2_negated = read_data_2[:31] + (1 - read_data_2[31],)
        # rd1 + (-rd2)
        result = cls.op_add(read_data_1, rd2_negated)
        return cls.compute_zero(result), result
    
    @classmethod
    def op_mul(cls, read_data_1: Bitx32, read_data_2: Bitx32) -> Bitx32:
        # Extract components from a
        rd1 = read_data_1
        rd2 = read_data_2

        sign_rd1 = rd1[31]
        exp_rd1 = rd1[23:31]
        mant_rd1 = rd1[0:23]
        
        # Extract components from b
        sign_rd2 = rd2[31]
        exp_rd2 = rd2[23:31]
        mant_rd2 = rd2[0:23]

        sign_result = g.xor_gate(sign_rd1, sign_rd2)

        if (exp_rd1 == EXP_ZERO and mant_rd1 == MANT_ZERO) or \
           (exp_rd2 == EXP_ZERO and mant_rd2 == MANT_ZERO):
            return (0,) * 31 + (sign_result,)
        
        if exp_rd1 == EXP_MAX or exp_rd2 == EXP_MAX:
            result_mant = (0,) * 23
            return result_mant + EXP_MAX + (sign_result,)
        
        if exp_rd1 != EXP_ZERO:
            mant_rd1_full = (1,) + mant_rd1
        else:
            mant_rd1_full = (0,) + mant_rd1

        if exp_rd2 != EXP_ZERO:
            mant_rd2_full = (1,) + mant_rd2
        else:
            mant_rd2_full = (0,) + mant_rd2

        if exp_rd1 == EXP_ZERO:
            exp_rd1 = (1,0,0,0,0,0,0,0)
        if exp_rd2 == EXP_ZERO:
            exp_rd2 = (1,0,0,0,0,0,0,0)

        mant_result = (0,) * 48
        for i in range(24):
            if mant_rd2_full[i] == 1:
                # Shift mant_a_full left by i positions and add to result
                shifted_rd1 = (0,) * i + mant_rd1_full + (0,) * (48 - 24 - i)
                mant_result = ALU.op_add(sign_extend(mant_result, 32), sign_extend(shifted_rd1[:32], 32))[1][:32]
                if len(shifted_rd1) > 32:
                    # Handle upper bits
                    upper_shifted = shifted_rd1[32:48]
                    upper_result = mant_result[32:48] if len(mant_result) >= 48 else (0,) * 16
                    upper_sum = ALU.op_add(sign_extend(upper_result + (0,) * 16, 32), sign_extend(upper_shifted + (0,) * 16, 32))[1][:16]
                    mant_result = mant_result[:32] + upper_sum

        exp_bias = (1,1,1,1,1,1,1,0)  # 127 in 8-bit
        exp_sum = ALU.op_add(sign_extend(exp_rd1, 32), sign_extend(exp_rd2, 32))[1][:8]
        exp_result = ALU.op_sub(sign_extend(exp_sum, 32), sign_extend(exp_bias, 32))[1][:8]

        if len(mant_result) >= 48 and mant_result[47] == 1:
            # Shift right by 24
            mant_result = ALU.op_srl(sign_extend(mant_result[:32], 32), dec_to_bin(24, 32))[1][:23]
            # Add 1 to exponent
            exp_result = ALU.op_add(sign_extend(exp_result, 32), dec_to_bin(1, 32))[1][:8]
        else:
            # Shift right by 23
            mant_result = ALU.op_srl(sign_extend(mant_result[:32], 32), dec_to_bin(23, 32))[1][:23]

        if g.high_level_min(exp_result, EXP_MAX) == EXP_MAX or exp_result == EXP_MAX:
            exp_result = EXP_MAX
            mant_result = MANT_ZERO
        else:
            # underflow
            exp_check = ALU.op_sub(sign_extend(exp_result, 32), ZERO_32)[1]
            if exp_check[31] == 1:  # Negative result means exp_result < 0
                # Check if exp_result < -23
                neg_23 = dec_to_bin(-23, 32)
                if g.high_level_min(sign_extend(exp_result, 32), neg_23) == sign_extend(exp_result, 32):
                    # Underflow to zero
                    return ZERO_32[:31] + (sign_result,)
                else:
                    # Denormalized number: shift = 1 - exp_result
                    shift_amount = ALU.op_sub(dec_to_bin(1, 32), sign_extend(exp_result, 32))[1]
                    mant_result = ALU.op_srl(sign_extend(mant_result, 32), shift_amount)[1][:23]
                    exp_result = EXP_ZERO

        if exp_result != EXP_ZERO:
            mant_result = ALU.op_and(sign_extend(mant_result, 32), hex_to_bin("7FFFFF", 32))[1][:23]
        
        # Pack result
        result = mant_result + exp_result + (sign_result,)
        
        return cls.compute_zero(result), result