"""
The memory for the system.
"""

from memory import Bit, Bitx4, Bitx7, Bitx32, bits_to_10_tup, Memory, Byte, bin_to_dec

"""
The memory for the system.
"""
from memory import Bit, Bitx4, Bitx7, Bitx32, bits_to_10_tup, Memory, Byte, bin_to_dec

class MemoryUnit:
    def __init__(self, memory_in_megabytes:int = 1):
        # Store pages of memory in a dict so we dont have to create a couple of gb of actual memory
        self.memory = {}
        self.max_address = memory_in_megabytes * 1_000_000
        
    def _get_byte(self, address: int) -> Byte:
        """Get a byte at the given address, create it if it doesn't exist."""
        if address not in self.memory:
            self.memory[address] = Byte()  # Create on first access
        return self.memory[address]
    
    def __getitem__(self, index: int) -> Bitx32:
        if index < 0 or index + 4 > self.max_address:
            raise RuntimeError(f"Memory address out of bounds: {hex(index)} to {hex(index+4)}")
        
        res_list = []
        # Read 4 bytes
        for byte_offset in range(4):
            byte = self._get_byte(index + byte_offset)
            for bit in byte:
                res_list.append(bit)
        return tuple(res_list)
    
    def __setitem__(self, index: int, value: Bitx32):
        if index < 0 or index + 4 > self.max_address:
            raise RuntimeError(f"Memory address out of bounds: {hex(index)}")
        
        # Write 32 bits across 4 bytes
        for b_i, bit in enumerate(value):
            byte_addr = index + (b_i // 8)
            bit_offset = b_i % 8
            
            # Get or create the byte at this address
            byte = self._get_byte(byte_addr)
            byte[bit_offset] = bit
    
    def read(self, address: Bitx32) -> Bitx32:
        return self[bin_to_dec(address)]
    
    def write(self, address: Bitx32, value: Bitx32):
        self[bin_to_dec(address)] = value
    