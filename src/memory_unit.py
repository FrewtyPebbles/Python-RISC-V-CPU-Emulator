"""
The memory for the system.
"""
from memory import Bit, Bitx4, Bitx7, Bitx32, bits_to_10_tup, Memory, Byte, bin_to_dec

import os

class MemoryUnit:
    def __init__(self, memory_in_megabytes:int = 1):
        # Store pages of memory in a dict so we dont have to create a couple of gb of actual memory
        self.memory:dict[int, Byte] = {}
        self.max_address:int = memory_in_megabytes * 1_000_000
        
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

    def __repr__(self):
        term_size:os.terminal_size = os.get_terminal_size()

        # Has a 3 byte threshold in both directions from a written bit

        display_bytes: list[tuple[tuple[int,Byte], ...]] = []

        last_address:int | None = None
        tup_addr_byte_buffer:list[tuple[int,Byte]] = []
        for addr_byte in sorted(self.memory.items(), key=lambda k:k[0]):
            addr = addr_byte[0]

            if last_address == None:
                tup_addr_byte_buffer.append(addr_byte)
            else:
                if addr > last_address + 3:
                    # append tup buffer to display bytes
                    display_bytes.append(tuple(tup_addr_byte_buffer))
                    tup_addr_byte_buffer = []
                else:
                    for between_addr in range(last_address+1, addr):
                        tup_addr_byte_buffer.append((between_addr, Byte()))
                
                tup_addr_byte_buffer.append(addr_byte)
            last_address = addr

        if len(tup_addr_byte_buffer):
            display_bytes.append(tuple(tup_addr_byte_buffer))

        lines = []
        address_line_buffer = ""
        bytes_line_buffer = ""

        def append_byte_data(address_byte:tuple[int, Byte]|str|None = None):
            nonlocal lines, address_line_buffer, bytes_line_buffer

            if address_byte == None:
                lines.append(address_line_buffer)
                lines.append(bytes_line_buffer)
                address_line_buffer = ""
                bytes_line_buffer = ""
                return

            if isinstance(address_byte, str):
                addr_str = f"  {' '*len(address_byte)}  "
                if len(bytes_line_buffer) + len(addr_str) > term_size.columns:
                    lines.append(address_line_buffer)
                    lines.append(bytes_line_buffer)
                    address_line_buffer = ""
                    bytes_line_buffer = ""
                
                address_line_buffer += addr_str
                bytes_line_buffer += f"  {address_byte}  "
            else:
                address = f"0x{hex(address_byte[0])[2:]:0>8}"
                addr_str = f"  {address}"
                if len(bytes_line_buffer) + len(addr_str) > term_size.columns:
                    lines.append(address_line_buffer)
                    lines.append(bytes_line_buffer)
                    address_line_buffer = ""
                    bytes_line_buffer = ""

                    
            
                
                byte = repr(address_byte[1])

                address_line_buffer += addr_str
                bytes_line_buffer += f"  {byte}  "
        
        for addresses_and_bytes in display_bytes:
            if addresses_and_bytes[0][0] > 0:
                append_byte_data("...")
            for address_byte in addresses_and_bytes:
                
                append_byte_data(address_byte)

            if addresses_and_bytes[-1][0] < self.max_address:
                append_byte_data("...")
        
        append_byte_data()

        return "\n".join(lines)

    