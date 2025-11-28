from memory import Bit, Bitx32, Bitx5, bin_to_dec, dec_to_bin, hex_to_bin, sign_extend
from rv32i_alu import RV32IALU

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
        # Get components (LSB-first)
        rd1 = read_data_1
        rd2 = read_data_2

        sign_rd1 = rd1[31]
        exp_rd1 = rd1[23:31]
        mant_rd1 = rd1[0:23]

        sign_rd2 = rd2[31]
        exp_rd2 = rd2[23:31]
        mant_rd2 = rd2[0:23]

        # Zero
        if exp_rd1 == EXP_ZERO and mant_rd1 == MANT_ZERO:
            return cls.compute_zero(rd2), rd2
        if exp_rd2 == EXP_ZERO and mant_rd2 == MANT_ZERO:
            return cls.compute_zero(rd1), rd1

        # Infinity
        if exp_rd1 == EXP_MAX:
            return cls.compute_zero(rd1), rd1
        if exp_rd2 == EXP_MAX:
            return cls.compute_zero(rd2), rd2
        
        # Add leading 1 for normalized nums
        mant_rd1_full = mant_rd1 + (1,) if exp_rd1 != EXP_ZERO else mant_rd1 + (0,)
        mant_rd2_full = mant_rd2 + (1,) if exp_rd2 != EXP_ZERO else mant_rd2 + (0,)

        # Adjust exponents if denormalized
        exp_rd1_working = exp_rd1 if exp_rd1 != EXP_ZERO else (1,0,0,0,0,0,0,0)
        exp_rd2_working = exp_rd2 if exp_rd2 != EXP_ZERO else (1,0,0,0,0,0,0,0)

        # Align mantissas, shift smaller exponent
        # keep lower bits and drop upper bits
        if g.high_level_min(exp_rd1_working, exp_rd2_working) == exp_rd2_working:
            # exp_rd1 > exp_rd2, need to shift mant_rd2 right
            shift = RV32IALU.op_sub(sign_extend(exp_rd1_working, 32), sign_extend(exp_rd2_working, 32))[1]
            shift_dec = bin_to_dec(shift, False)
            if shift_dec < 24:
                # Right shift in LSB-first: drop lower bits, pad zeros at top
                mant_rd2_full = mant_rd2_full[shift_dec:] + (0,) * shift_dec
                if len(mant_rd2_full) > 24:
                    mant_rd2_full = mant_rd2_full[:24]
                elif len(mant_rd2_full) < 24:
                    mant_rd2_full = mant_rd2_full + (0,) * (24 - len(mant_rd2_full))
            else:
                mant_rd2_full = (0,) * 24
            exp_result = exp_rd1_working
        elif g.high_level_min(exp_rd1_working, exp_rd2_working) == exp_rd1_working:
            # exp_rd2 > exp_rd1, need to shift mant_rd1 right
            shift = RV32IALU.op_sub(sign_extend(exp_rd2_working, 32), sign_extend(exp_rd1_working, 32))[1]
            shift_dec = bin_to_dec(shift, False)
            if shift_dec < 24:
                mant_rd1_full = mant_rd1_full[shift_dec:] + (0,) * shift_dec
                if len(mant_rd1_full) > 24:
                    mant_rd1_full = mant_rd1_full[:24]
                elif len(mant_rd1_full) < 24:
                    mant_rd1_full = mant_rd1_full + (0,) * (24 - len(mant_rd1_full))
            else:
                mant_rd1_full = (0,) * 24
            exp_result = exp_rd2_working
        else:
            exp_result = exp_rd1_working

        # Ensure both mantissas are exactly 24 bits
        while len(mant_rd1_full) < 24:
            mant_rd1_full = mant_rd1_full + (0,)
        while len(mant_rd2_full) < 24:
            mant_rd2_full = mant_rd2_full + (0,)
        mant_rd1_full = mant_rd1_full[:24]
        mant_rd2_full = mant_rd2_full[:24]

        # add / subtract
        if sign_rd1 == sign_rd2:
            mant_result = RV32IALU.op_add(sign_extend(mant_rd1_full, 32), sign_extend(mant_rd2_full, 32))[1][:25]
            sign_result = sign_rd1
        else:
            # Different signs
            # Compare magnitudes
            mant1_ge_mant2 = True
            for i in range(23, -1, -1):
                if mant_rd1_full[i] > mant_rd2_full[i]:
                    mant1_ge_mant2 = True
                    break
                elif mant_rd1_full[i] < mant_rd2_full[i]:
                    mant1_ge_mant2 = False
                    break
            
            if mant1_ge_mant2:
                mant_result = RV32IALU.op_sub(sign_extend(mant_rd1_full, 32), sign_extend(mant_rd2_full, 32))[1][:25]
                sign_result = sign_rd1
            else:
                mant_result = RV32IALU.op_sub(sign_extend(mant_rd2_full, 32), sign_extend(mant_rd1_full, 32))[1][:25]
                sign_result = sign_rd2

        # Handle result of zero
        if all(b == 0 for b in mant_result):
            return 1, ZERO_32
        
        # Find the leading 1 position
        leading_one_pos = -1
        for i in range(len(mant_result) - 1, -1, -1):
            if mant_result[i] == 1:
                leading_one_pos = i
                break
        
        if leading_one_pos == -1:
            return 1, ZERO_32

        # Normalize mantissa
        if leading_one_pos > 23:
            # Overflow: need to shift right
            shift_dec = leading_one_pos - 23
            mant_result = RV32IALU.op_srl(sign_extend(mant_result, 32), dec_to_bin(shift_dec, 32))[1][:24]
            exp_result = RV32IALU.op_add(sign_extend(exp_result, 32), dec_to_bin(shift_dec, 32))[1][:8]
        elif leading_one_pos < 23:
            # Need to shift left to normalize
            shift_dec = 23 - leading_one_pos
            shift_bits = dec_to_bin(shift_dec, 32)
            
            # Check if we can shift without underflowing exponent
            exp_cmp = RV32IALU.op_sub(sign_extend(exp_result, 32), shift_bits)[1]
            if exp_cmp[31] == 0:  # Result is non-negative
                # Can normalize
                mant_result = RV32IALU.op_sll(sign_extend(mant_result, 32), shift_bits)[1][:24]
                exp_result = exp_cmp[:8]
            else:
                # create denormalized number
                shift_available = RV32IALU.op_sub(sign_extend(exp_result, 32), dec_to_bin(1, 32))[1]
                if shift_available[31] == 0:  # Still have some room
                    mant_result = RV32IALU.op_sll(sign_extend(mant_result, 32), shift_available)[1][:24]
                exp_result = EXP_ZERO
        else:
            # Already at position 23
            mant_result = mant_result[:24]

        # Overflow check
        if all(exp_result[i] == EXP_MAX[i] for i in range(8)):
            exp_result = EXP_MAX
            mant_result = MANT_ZERO + (0,)
            result = mant_result[:23] + exp_result + (sign_result,)
            return cls.compute_zero(result), result

        # Check for exponent overflow during normalization
        exp_overflow = False
        for i in range(8):
            if exp_result[i] != EXP_MAX[i]:
                if exp_result[i] < EXP_MAX[i]:
                    exp_overflow = False
                else:
                    exp_overflow = True
                break
        
        if exp_overflow or all(exp_result[i] == EXP_MAX[i] for i in range(8)):
            exp_result = EXP_MAX
            mant_result = (0,) * 24
            result = mant_result[:23] + exp_result + (sign_result,)
            return cls.compute_zero(result), result

        # Remove leading 1 when normalized (bit 23)
        if exp_result != EXP_ZERO:
            mant_result = mant_result[:23]
        else:
            mant_result = mant_result[:23]

        # Pack the result back into IEEE754 (LSB-first)
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
                mant_result = RV32IALU.op_add(sign_extend(mant_result, 32), sign_extend(shifted_rd1[:32], 32))[1][:32]
                if len(shifted_rd1) > 32:
                    # Handle upper bits
                    upper_shifted = shifted_rd1[32:48]
                    upper_result = mant_result[32:48] if len(mant_result) >= 48 else (0,) * 16
                    upper_sum = RV32IALU.op_add(sign_extend(upper_result + (0,) * 16, 32), sign_extend(upper_shifted + (0,) * 16, 32))[1][:16]
                    mant_result = mant_result[:32] + upper_sum

        exp_bias = (1,1,1,1,1,1,1,0)  # 127 in 8-bit
        exp_sum = RV32IALU.op_add(sign_extend(exp_rd1, 32), sign_extend(exp_rd2, 32))[1][:8]
        exp_result = RV32IALU.op_sub(sign_extend(exp_sum, 32), sign_extend(exp_bias, 32))[1][:8]

        if len(mant_result) >= 48 and mant_result[47] == 1:
            # Shift right by 24
            mant_result = RV32IALU.op_srl(sign_extend(mant_result[:32], 32), dec_to_bin(24, 32))[1][:23]
            # Add 1 to exponent
            exp_result = RV32IALU.op_add(sign_extend(exp_result, 32), dec_to_bin(1, 32))[1][:8]
        else:
            # Shift right by 23
            mant_result = RV32IALU.op_srl(sign_extend(mant_result[:32], 32), dec_to_bin(23, 32))[1][:23]

        if g.high_level_min(exp_result, EXP_MAX) == EXP_MAX or exp_result == EXP_MAX:
            exp_result = EXP_MAX
            mant_result = MANT_ZERO
        else:
            # underflow
            exp_check = RV32IALU.op_sub(sign_extend(exp_result, 32), ZERO_32)[1]
            if exp_check[31] == 1:  # Negative result means exp_result < 0
                # Check if exp_result < -23
                neg_23 = dec_to_bin(-23, 32)
                if g.high_level_min(sign_extend(exp_result, 32), neg_23) == sign_extend(exp_result, 32):
                    # Underflow to zero
                    return ZERO_32[:31] + (sign_result,)
                else:
                    # Denormalized number: shift = 1 - exp_result
                    shift_amount = RV32IALU.op_sub(dec_to_bin(1, 32), sign_extend(exp_result, 32))[1]
                    mant_result = RV32IALU.op_srl(sign_extend(mant_result, 32), shift_amount)[1][:23]
                    exp_result = EXP_ZERO

        if exp_result != EXP_ZERO:
            mant_result = RV32IALU.op_and(sign_extend(mant_result, 32), hex_to_bin("7FFFFF", 32))[1][:23]
        
        # Pack result
        result = mant_result + exp_result + (sign_result,)
        
        return cls.compute_zero(result), result