from assembler.instructions import LabelToken, DirectiveToken, InstructionToken, Token
from memory import dec_to_bin

class Assembler:

    asm:str

    def __init__(self, asm:str):
        self.asm:str = asm

    def parse_labels(self, start_address:int = 0x0) -> dict[str, LabelToken]:
        pc = start_address
        label_table:dict[str, LabelToken] = {}

        for line in self.asm.splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue  # skip empty lines/comments
            
            if any([line.startswith(prefix) for prefix in [
                ".globl", ".section", ".text", ".data", ".bss"
            ]]):
                continue
            
            # Detect label (ends with ':')
            if line.endswith(':'):
                label = line[:-1]
                label_table[label] = LabelToken(label, pc)
                # Do not increment PC for label itself
            else:
                # Assume every instruction is 4 bytes
                pc += 4

        return label_table
    
    def parse(self, start_address:int = 0x0) -> list[str]:
        """
        Returns a list of 32 bit hex values
        """
        pc = start_address
        label_table = self.parse_labels(start_address)

        tokens:list[Token] = []

        for line in self.asm.splitlines():
            line = line.split('#', 1)[0].strip()
            if not line or line.startswith('#') or line.endswith(":"):
                continue  # skip empty lines/comments
            
            if line.startswith("."):
                tokens.append(self.parse_directive(line))
                if any([line.startswith(prefix) for prefix in [
                    ".globl", ".section", ".text", ".data", ".bss"
                ]]):
                    continue
                else:
                    pc += 4
                    continue

            # Parse instruction
            tokens.append(self.parse_instruction(line, pc))
            pc += 4

        gen_code:list[str] = []

        for token in tokens:
            if token.does_codegen():
                gen_code.append(token.to_hex(label_table))

        return gen_code



    def parse_directive(self, line: str) -> DirectiveToken:
        line = line.strip()
        
        parts = line.split(maxsplit=1)
        directive_name = parts[0]
        args_str = parts[1] if len(parts) > 1 else ""
        
        args = [arg.strip() for arg in args_str.split(',')] if args_str else []
        
        return DirectiveToken(directive_name, *args)

    def parse_instruction(self, line: str, pc:int) -> InstructionToken:
        # TODO
        # Split instruction name and arguments
        parts = line.split(maxsplit=1)
        instruction = parts[0]  # e.g., "addi"
        args_str = parts[1] if len(parts) > 1 else ""
        
        # Split arguments by comma and strip whitespace
        args = [arg.strip() for arg in args_str.split(',')] if args_str else []
        
        return InstructionToken(pc, instruction, *args)
