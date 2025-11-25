from memory import Bit, Bitx5, Bitx8, Bitx23, Bitx24, Bitx32, Bitx48, bin_to_dec, dec_to_bin_signed
from alu import ALU

class FPU32:
    alu = ALU()
    
    # 127, in a 32-bit binary string
    BIAS_BITS = (0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0, 0,1,1,1,1,1,1,1)

    ONE_32 = (0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,1)
    ZERO_32 = (0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0)

    EXP_ALL_ONES  = (1, 1, 1, 1, 1, 1, 1, 1)
    EXP_ALL_ZEROS = (0, 0, 0, 0, 0, 0, 0, 0)

    def update(self):
        pass

    def f_add(self, operand_1:Bitx32, operand_2:Bitx32) -> Bitx32: 
        sign_1 = operand_1[0] #0 for pos, 1 for neg
        sign_2 = operand_2[0]

        stored_exp_1 = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0] + operand_1[1:8] #value of exponent as stored, converted to 32-bit
        stored_exp_2 = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0] + operand_2[1:8]

        mantissa_1 = [0,0,0,0,0,0,0,1] + operand_1[9:31] #normalized value of mantissa in 32-bits, including implied '1' bit
        mantissa_2 = [0,0,0,0,0,0,0,1] + operand_2[9:31]

        true_exp_1 = bin_to_dec(self.alu.op_sub(stored_exp_1, self.BIAS_BITS)[1]) #remove bias and calculate true value of exponent 
        true_exp_2 = bin_to_dec(self.alu.op_sub(stored_exp_2, self.BIAS_BITS)[1])

        delta_e = abs(true_exp_1 - true_exp_2) #difference between exponents

        res_exp

        if true_exp_1 > true_exp_2: #shift the mantissa of the smaller exponent value delta_e times
            res_exp = true_exp_1
            mantissa_2 = self.alu.op_sra(mantissa_2, dec_to_bin_signed(delta_e))[1]
        else:
            res_exp = true_exp_2
            mantissa_1 = self.alu.op_sra(mantissa_1, dec_to_bin_signed(delta_e))[1]
                
        res_mantissa

        if sign_1 == sign_2:
            res_mantissa = self.alu.op_add(mantissa_1, mantissa_2)[1]
        else:
            res_mantissa = self.alu.op_sub(mantissa_1, mantissa_2)[1]
        
        res_mantissa, res_exp = self.normalize(res_mantissa, res_exp) #normalize result to 1.F format
        #next, we need to round and check for exceptions, updating freg if we find exceptions



    def f_mul(self, operand_1:Bitx32, operand_2:Bitx32) -> Bitx32: 
        pass

    def normalize(self, operand:Bitx32, exponent) -> {Bitx32, int}: 
        implied_bit = operand[8]
        if implied_bit:
            operand = self.alu.op_sra(operand, self.ONE_32)
            exponent += 1
        else:
            while not implied_bit:
                exponent -= 1
                operand = self.alu.op_sll(operand, self.ONE_32)
        
        return {operand, exponent}
    
    def round_to_nearest_ties_to_even(self, to_be_rounded:Bitx48) -> Bitx23:
        g_bit = to_be_rounded[24]
        r_bit = to_be_rounded[25]
        s_bits = to_be_rounded[26:]

        s_bit
        for _ in range(len(s_bits)):
            s_bit = s_bit or s_bits[_]

        if not g_bit:

        elif g_bit and (r_bit or s_bit):

        else:
            if to_be_rounded[23]:
                return self.alu.op_add([0,0,0,0,0,0,0,0] + to_be_rounded[:24], self.ONE_32)[1]
            else:
                return to_be_rounded[0:23]