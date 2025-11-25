from memory import Bit, Bitx5, Bitx8, Bitx23, Bitx24, Bitx32, Bitx48, bin_to_dec, dec_to_bin_signed
from alu import ALU

class FPU32:
    alu = ALU()
    
    # 127, in a 32-bit binary string
    BIAS_BITS = (0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0, 0,1,1,1,1,1,1,1)

    EXP_ALL_ONES  = (1, 1, 1, 1, 1, 1, 1, 1)
    EXP_ALL_ZEROS = (0, 0, 0, 0, 0, 0, 0, 0)

    def update(self):
        pass

    def f_add(self, operand_1:Bitx32, operand_2:Bitx32): 
        sign_1 = operand_1[0] #0 for pos, 1 for neg
        sign_2 = operand_2[0]

        stored_exp_1 = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0] + operand_1[1, 8] #value of exponent as stored, converted to 32-bit
        stored_exp_2 = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0] + operand_2[1, 8]

        mantissa_1 = operand_1[9, 31] #normalized value of mantissa
        mantissa_2 = operand_2[9, 31]

        true_exp_1 = bin_to_dec(self.alu.op_sub(stored_exp_1, self.BIAS_BITS)[1]) #remove bias and calculate true value of exponent 
        true_exp_2 = bin_to_dec(self.alu.op_sub(stored_exp_2, self.BIAS_BITS)[1])


        delta_e = abs(true_exp_1 - true_exp_2) #difference between exponents

        if true_exp_1 > true_exp_2:
            pass
        else:
            pass

    def f_mul(self, operand_1:Bitx32, operand_2:Bitx32): 
        pass
    
    def round_to_nearest_ties_to_even(self, to_be_rounded:Bitx48):
        pass

