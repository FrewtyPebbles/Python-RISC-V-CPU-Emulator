import argparse
from assembler import assemble, Assembler

from datapath import DataPath

def main():
    parser = argparse.ArgumentParser(
        description="An RV32I CPU Emulator with FPU extension.  It will attempt to assemble and run the provided RV32I assembly source file on the RV32I emulator.",
        usage="riscv-sim {program file path}\n  use --help for more information"
    )
    parser.add_argument("source", help="Path to input assembly or hex file.")
    parser.add_argument("--assemble_only", action="store_true", help="Flag to assemble a file without running it.")
    parser.add_argument("--dont_show_steps", action="store_true", help="Flag to not show every instruction step the emulator takes.")
    parser.add_argument("--show_memory", action="store_true", help="Flag to show all the in use memory in the Memory Unit.")
    parser.add_argument("--show_reads", action="store_true", help="Flag to show whenever the Memory Unit is read from.")
    parser.add_argument("--show_writes", action="store_true", help="Flag to show whenever the Memory Unit is written to.")
    parser.add_argument("--show_immediate_values", action="store_true", help="Flag to show all possible immediate values by type after every step.")
    parser.add_argument("--show_registers", action="store_true", help="Flag to show all registers after every step.")
    parser.add_argument("-o", "--output", help="Path to output hex file.  This only works when the '--assemble_only' argument flag is included")
    args = parser.parse_args()

    if args.assemble_only:
        assemble(args.source, args.output)
        print(f"File written to {args.output}")
    else:
        ## Run the program

        source:str = args.source
        show_steps:bool = not args.dont_show_steps
        show_memory:bool = args.show_memory
        show_reads:bool = args.show_reads
        show_writes:bool = args.show_writes
        show_immediate_values:bool = args.show_immediate_values
        show_registers:bool = args.show_registers
        dp = DataPath(
            show_immediate_values,
            show_registers,
            show_steps,
            show_memory,
            show_reads,
            show_writes
        )
        code_gen:list[str] = []
        
        
        with open(source, mode="r") as fp:
            if source.endswith(".asm"):
                assembler = Assembler(fp.read())
                code_gen = assembler.parse(0x0)
            else:
                code_gen = fp.readlines()
        
        dp.load_program(code_gen)
        dp.run()




if __name__ == "__main__":
    main()