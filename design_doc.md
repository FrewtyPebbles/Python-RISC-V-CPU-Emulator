# Supported Instruction Set

## RV32I Supported Instruction Set

### R-Type
 * add
 * sub
 * and
 * or
 * xor
 * sll
 * srl
 * sra

### I-Type
 * addi
 * lw
 * jalr

### B-Type
 * beq
 * bne

### U-Type
 * lui
 * auipc

### S-Type
 * sw

### J-Type
 * jal

## RV32F Supported Instruction Set

### R-Type
 * fadd.s
 * fsub.s
 * fmul.s

### I-Type
 * flw

### S-Type
 * fsw

## Testing

This project uses the pytest testing framework to perform unit tests to test specific components of the cpu. We opted to use pytest for its convenience and its ease of use. 

## Architecture

![Diagram for Reference](rv32i_datapath.png)

This was the diagram upon which we based our designs. We used this image to help us identify which components need to be connected where as well as how to process each bit in the instructions. 

The layout of the datapath is as follows- instructions are fetched from the memory unit, which are then interpreted by the control unit. Next, the control unit sends signals to the appropriate components so the instruction can be executed. The registers are then queried for the data stored in a relevant register and the data is manipulated in the ALU, saving results to the appropraite register when specified. 

## Additional Features

This project also contains code to perform operations at the gate-level, the logic for which is stored in gates.py, which allows us to demonstrate more clearly what is taking place in the inside of a CPU. 
