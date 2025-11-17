from memory import Bitx32, dec_to_bin, bin_to_dec, hex_to_bin, hex_endian_swap


class PC:
    value:Bitx32

    def __init__(self, initial_value:int|Bitx32):
        self.value = dec_to_bin(initial_value) if isinstance(initial_value, int) else initial_value
    
    def update(self, new_address:Bitx32):
        self.value = new_address
        return new_address

class InstructionMemory:

    memory:list[Bitx32]

    def __init__(self):
        self.memory = []

    def load(self, hex_data:str):
        self.memory = []
        for i_n, instr_hex in enumerate(hex_data.splitlines()):
            instr_hex = hex_endian_swap(instr_hex)
            self.memory.append(hex_to_bin(i_n))
            

    def get_instruction(self, address:Bitx32) -> Bitx32:
        dec_addr = bin_to_dec(address)
        
        return self.memory[dec_addr]