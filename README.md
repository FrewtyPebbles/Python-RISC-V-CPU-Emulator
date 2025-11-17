# RISC V 32-Bit CPU Emulator

 - By William Lim, Mathew Barlund, and Adam Kaci

## AI Usage

 - AI was used to generate a portion of the unit tests and for assisting with minor bug fixes.

# Installation

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
python -m pip install dist/something.whl
```

Now the cpu emulator should be installed globally!

# Running the emulator

To run a program with the emulator use the command in the terminal:

```
riskv-sim {input_file.hex or input_file.asm}
```

# Using the assembler

To just assemble an RV32I assembly program use the `--assemble_only` flag:

```
riskv-sim {input_file.asm} --assemble_only -o {outputfile.hex}
```
You should then see the output file saved to the location specified by `-o`.