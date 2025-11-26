

# RISC V 32-Bit CPU Emulator

 - By William Lim and Matthew Barlund

This CPU emulator emulates at the bit level with many low level gates emulated.

## AI Usage

 - ChatGPT was used to generate a portion of the unit tests, for generating `.asm` assembly files, and to help understand the bit manipulation in generating the immediate values in the assembler. Gemini was used to help with minor bug fixes and syntax correction. 

## Installation

First CD into the project directory and make sure pip and build and wheel are up to date:

```
python -m pip install --upgrade pip
python -m pip install --upgrade build wheel
```

Then build the package:

```
python -m build
```

Then install the `.whl` file in the `dist/` directory that was just created.

```
python -m pip install ./dist/something.whl
```

Now the cpu emulator should be installed globally!
You can also do this in a venv if you want.

## Running the emulator

To run a program with the emulator use the command in the terminal:

```
riskv-sim {input_file.hex or input_file.asm}
```

To see what flags you can include do:

```
riscv-sim --help
```

These flags show different debug information after each step. Here is the help command output for your convenience:

```
usage: riscv-sim {program file path}
  use --help for more information

An RV32I CPU Emulator with FPU extension. It will attempt to assemble and run the provided RV32I assembly source file on the RV32I emulator.

positional arguments:
  source                Path to input assembly or hex file.

options:
  -h, --help            show this help message and exit
  --assemble_only       Flag to assemble a file without running it.
  --dont_show_steps     Flag to not show every instruction step the emulator takes.
  --show_memory         Flag to show all the in use memory in the Memory Unit.
  --show_reads          Flag to show whenever the Memory Unit is read from.
  --show_writes         Flag to show whenever the Memory Unit is written to.
  --show_immediate_values
                        Flag to show all possible immediate values by type after every step.
  --show_registers      Flag to show all registers after every step.
  -o OUTPUT, --output OUTPUT
                        Path to output hex file. This only works when the '--assemble_only' argument flag is included
```

## Using the assembler

To just assemble an RV32I assembly program use the `--assemble_only` flag:

```
riskv-sim {input_file.asm} --assemble_only -o {outputfile.hex}
```
You should then see the output file saved to the location specified by `-o`.

