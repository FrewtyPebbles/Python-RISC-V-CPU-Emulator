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

        stored_exp_1 = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0] + operand_1[1:9] #value of exponent as stored, converted to 32-bit
        stored_exp_2 = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0] + operand_2[1:9]

        mantissa_1 = [0,0,0,0,0,0,0,1] + operand_1[9:32] #normalized value of mantissa in 32-bits, including implied '1' bit
        mantissa_2 = [0,0,0,0,0,0,0,1] + operand_2[9:32]

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
        
        res_mantissa, res_exp = self.normalize_add(res_mantissa, res_exp) #normalize result to 1.F format
        res_mantissa = self.round_to_nearest_ties_to_even([0,0,0,0,0,0,0,0] + res_mantissa)
        
        val_mantissa_1 = bin_to_dec(mantissa_1)
        val_mantissa_2 = bin_to_dec(mantissa_2)
        
        res_sign = sign_2 if val_mantissa_2>val_mantissa_1 and sign_1 != sign_2 else sign_1 #determining sign

        res:Bitx32 = res_sign + res_exp + res_mantissa #assembling result to be returned
        return res


    def f_mul(self, operand_1:Bitx32, operand_2:Bitx32) -> Bitx32: 
        sign_1 = operand_1[0] #0 for pos, 1 for neg
        sign_2 = operand_2[0]
        res_sign_bit = 0 if sign_1 == sign_2 else 1

        stored_exp_1 = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0] + operand_1[1:9] #value of exponent as stored, converted to 32-bit
        stored_exp_2 = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0] + operand_2[1:9]

        mantissa_1 = [0,0,0,0,0,0,0,1] + operand_1[9:32] #normalized value of mantissa in 32-bits, including implied '1' bit
        mantissa_2 = [0,0,0,0,0,0,0,1] + operand_2[9:32]

        true_exp_1 = bin_to_dec(self.alu.op_sub(stored_exp_1, self.BIAS_BITS)[1]) #remove bias and calculate true value of exponent 
        true_exp_2 = bin_to_dec(self.alu.op_sub(stored_exp_2, self.BIAS_BITS)[1])
        true_res_exp = true_exp_1 + true_exp_2

        raw_res_mantissa:Bitx48 = binary_mul(mantissa_1, mantissa_2)
        {raw_res_mantissa, true_res_exp} = self.normalize_mul(raw_res_mantissa, stored_res_exp)
        res_mantissa:Bitx23 = self.round_to_nearest_ties_to_even(raw_res_mantissa)
        stored_res_exp = self.alu.op_add(dec_to_bin_signed(true_res_exp), self.BIAS_BITS)[1][-8:]
        
        res:Bitx32 = [res_sign_bit] + stored_res_exp + res_mantissa
        return res
    

    def normalize_add(self, operand:Bitx32, exponent) -> {Bitx32, int}: 
        implied_bit = operand[8]
        if implied_bit:
            operand = self.alu.op_sra(operand, self.ONE_32)
            exponent += 1
        else:
            while not implied_bit:
                exponent -= 1
                operand = self.alu.op_sll(operand, self.ONE_32)
        
        return {operand, exponent}
    
    def normalize_mul(self, operand:Bitx48, exponent) -> {Bitx32, int}:
        implied_bit = operand[8]
        while not implied_bit:
            operand = self.alu.op_sra(operand, self.ONE_32)
            exponent += 1
        return {operand, exponent}
    
    def binary_mul(self, operand_1: Bitx23, operand_2: Bitx23) -> Bitx48:
        res:Bitx48
        operand_1 = [1] + operand_1
        operand_2 = [1] + operand_2 #adding implied bit

        partial_products:list
        for bit in range(24): #for every bit in operand_2
            if operand_2[bit]:
                partial_product = operand_1
                for _ in bit:
                    partial_product += [0]
                partial_products.append(partial_product) #if partial product is significant (not zero), store it

        for item in partial_products:
            res = self.alu.op_add(res[-32:], item) #adding up partial products

        return res
    
    def round_to_nearest_ties_to_even(self, to_be_rounded:Bitx48) -> Bitx23:
        g_bit = to_be_rounded[24]
        r_bit = to_be_rounded[25]
        s_bits = to_be_rounded[26:]

        s_bit
        for _ in range(len(s_bits)):
            s_bit = s_bit or s_bits[_]

        if not g_bit:
            return to_be_rounded[0:22] 

        elif g_bit and (r_bit or s_bit):
            to_be_rounded = self.alu.op_add([0,0,0,0,0,0,0,0] + to_be_rounded[:24], self.ONE_32)[1]
            return to_be_rounded[0:22]
        else:
            if to_be_rounded[23]:
                return self.alu.op_add([0,0,0,0,0,0,0,0] + to_be_rounded[:24], self.ONE_32)[1][0:22]
            else:
                return to_be_rounded[0:22]