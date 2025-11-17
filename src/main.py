import argparse
from assembler import assemble

def main():
    parser = argparse.ArgumentParser(
        description="An RV32I CPU Emulator with FPU extension.  It will attempt to assemble and run the provided RV32I assembly source file on the RV32I emulator.",
        usage="riscv-sim {program file path}\n  use --help for more information"
    )
    parser.add_argument("source", help="Path to input assembly or hex file.")
    parser.add_argument("--assemble_only", action="store_true", help="Flag to assemble a file without running it.")
    parser.add_argument("-o", "--output", help="Path to output hex file.  This only works when the '--assemble_only' argument flag is included")
    args = parser.parse_args()

    if args.assemble_only:
        assemble(args.source, args.output)
        print(f"File written to {args.output}")
    else:
        ## Run the program
        print("TODO")

if __name__ == "__main__":
    main()