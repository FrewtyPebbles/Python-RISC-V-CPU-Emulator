from memory import Bit, Bitx12, Bitx32, Bitx4, bin_to_dec, dec_to_bin

import alu_control as ac
import gates as g

class ALU:
    def __init__(self):
        pass
    
    def update(self, operation:Bitx4, read_data_1:Bitx32, read_data_2:Bitx32) -> tuple[Bit, Bitx32]:
        """
        Returns Zero bit signal and 32-bit alu result.
        """
        match operation:
            case ac.CTRL_ALU_ADD:
                return self.op_add(read_data_1, read_data_2)
            case ac.CTRL_ALU_SUB:
                return self.op_sub(read_data_1, read_data_2)
            case ac.CTRL_ALU_AND:
                return self.op_and(read_data_1, read_data_2)
            case ac.CTRL_ALU_OR:
                return self.op_or(read_data_1, read_data_2)
            case ac.CTRL_ALU_XOR:
                return self.op_xor(read_data_1, read_data_2)
            case ac.CTRL_ALU_SLL:
                return self.op_sll(read_data_1, read_data_2)
            case ac.CTRL_ALU_SRL:
                return self.op_srl(read_data_1, read_data_2)
            case ac.CTRL_ALU_SRA:
                return self.op_sra(read_data_1, read_data_2)
            case ac.CTRL_ALU_SLT:
                return self.op_slt(read_data_1, read_data_2)
            case ac.CTRL_ALU_SLTU:
                return self.op_sltu(read_data_1, read_data_2)
            case _:
                raise RuntimeError(f"ALU Operation not supported {operation}")
            
    @staticmethod
    def compute_zero(res: Bitx32) -> Bit:
        return int(all(b == 0 for b in res))

    @staticmethod
    def op_add(read_data_1:Bitx32, read_data_2:Bitx32) -> tuple[Bit, Bitx32]:
        res_list = [0] * 32
        carry:Bit = 0
        for b_n in range(32):
            bit, carry = g.one_bit_adder(read_data_1[b_n], read_data_2[b_n], carry)
            res_list[b_n] = bit

        res = tuple(res_list)
        zero = ALU.compute_zero(res)
        return zero, res


    @classmethod
    def op_sub(cls, read_data_1:Bitx32, read_data_2:Bitx32):
        # Get read_data_2 NOT
        rd2_not_list = [0] * 32
        for n, bit_rd2 in enumerate(read_data_2):
            rd2_not_list[n] = int(not bit_rd2)
        rd2_not = tuple(rd2_not_list)

        # Now add 1 to it:
        _, rd2_2s_comp = cls.op_add(rd2_not, dec_to_bin(1,32))
        
        return cls.op_add(read_data_1, rd2_2s_comp)

        
    
    @staticmethod
    def op_and(read_data_1:Bitx32, read_data_2:Bitx32):
        res_list = [0] * 32
        for b_n in range(32):
            res_list[b_n] = g.and_gate(read_data_1[b_n], read_data_2[b_n])

        res = tuple(res_list)
        zero = ALU.compute_zero(res)
        return zero, res
    
    @staticmethod
    def op_or(read_data_1:Bitx32, read_data_2:Bitx32):
        res_list = [0] * 32
        for b_n in range(32):
            res_list[b_n] = g.or_gate(read_data_1[b_n], read_data_2[b_n])

        res = tuple(res_list)
        zero = ALU.compute_zero(res)
        return zero, res

    @staticmethod
    def op_xor(read_data_1:Bitx32, read_data_2:Bitx32):
        res_list = [0] * 32
        for b_n in range(32):
            res_list[b_n] = g.xor_gate(read_data_1[b_n], read_data_2[b_n])

        res = tuple(res_list)
        zero = ALU.compute_zero(res)
        return zero, res

    @staticmethod
    def op_sll(read_data_1:Bitx32, read_data_2:Bitx32):
        shift = min(bin_to_dec(read_data_2[0:5]), 32)
        res = read_data_1[shift:] + tuple(0 for _ in range(shift))
        zero = ALU.compute_zero(res)
        return zero, res

    @staticmethod
    def op_srl(read_data_1:Bitx32, read_data_2:Bitx32):
        shift = min(bin_to_dec(read_data_2[0:5]), 32)
        res = tuple(0 for _ in range(shift)) + read_data_1[:32 - shift]
        zero = ALU.compute_zero(res)
        return zero, res

    @staticmethod
    def op_sra(read_data_1:Bitx32, read_data_2:Bitx32):
        shift = min(bin_to_dec(read_data_2[0:5]), 32)
        sign_bit = read_data_1[31]
        res = tuple(sign_bit for _ in range(shift)) + read_data_1[:32 - shift]
        zero = ALU.compute_zero(res)
        return zero, res

    @staticmethod
    def op_slt(read_data_1:Bitx32, read_data_2:Bitx32):
        def bits_to_signed(bits: Bitx32) -> int:
            val = bin_to_dec(bits)
            if bits[31] == 1:
                val -= 2**32
            return val

        result = 1 if bits_to_signed(read_data_1) < bits_to_signed(read_data_2) else 0
        res = (result,) + (0,) * 31
        zero = ALU.compute_zero(res)
        return zero, res

    @staticmethod
    def op_sltu(read_data_1:Bitx32, read_data_2:Bitx32):
        val_a = bin_to_dec(read_data_1)
        val_b = bin_to_dec(read_data_2)
        result = 1 if val_a < val_b else 0
        res = (result,) + (0,) * 31
        zero = ALU.compute_zero(res)
        return zero, res