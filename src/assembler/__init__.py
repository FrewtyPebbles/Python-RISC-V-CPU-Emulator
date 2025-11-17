from assembler.assembler import Assembler

def assemble(input_file_path:str, output_file_path:str):
    with open(input_file_path, mode="r") as fp:
        assembler = Assembler(fp.read())
        code_gen = assembler.parse(0x0) # 0x0 is starting PC

    with open(output_file_path, mode="w") as fp:
        fp.write("\n".join(code_gen))
    