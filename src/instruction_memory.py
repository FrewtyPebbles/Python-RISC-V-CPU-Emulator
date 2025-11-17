from memory import Bitx32, dec_to_bin, bin_to_dec


class PC:
    value:Bitx32

    def __init__(self, initial_value:int|Bitx32):
        self.value = dec_to_bin(initial_value) if isinstance(initial_value, int) else initial_value
    
    def update(self, new_address:Bitx32):
        self.value = new_address
        return new_address

class InstructionMemory:

    memory:list[Bitx32]

    def __init__(self, memory:list[Bitx32]):
        self.memory = memory

    def get_instruction(self, address:Bitx32):
        dec_addr = bin_to_dec(address)
        
        return self.memory[dec_addr]