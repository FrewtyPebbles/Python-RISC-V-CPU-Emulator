from memory import Bit

# This module is where all of the low level bitwise
# gates are implemented.

GROUND = Bit(False)

def pmos(control:Bit, data:Bit) -> Bit:
    if not control:
        return data
    return GROUND

def nmos(control:Bit, data:Bit) -> Bit:
    if control:
        return data
    return GROUND

def not_gate(data:Bit, power:Bit = None) -> Bit:
    power = power if power != None else Bit(True)
    pmos_out:Bit = pmos(data, power)
    grounded:Bit = nmos(data, pmos_out)

    if grounded:
        return GROUND
    return pmos_out

def nand_gate(data_a:Bit, data_b:Bit, power:Bit = None) -> Bit:
    power = power if power != None else Bit(True)
    pmos_out_a = pmos(data_a, power)
    pmos_out_b = pmos(data_b, power)
    pmos_combined = pmos_out_a | pmos_out_b

    nmos_out_a = nmos(data_a, pmos_combined)
    grounded = nmos(data_b, nmos_out_a)

    if grounded:
        return GROUND
    return pmos_combined

def nor_gate(data_a:Bit, data_b:Bit, power:Bit = None) -> Bit:
    power = power if power != None else Bit(True)
    pmos_out_a = pmos(data_a, power)
    pmos_out_b = pmos(data_b, pmos_out_a)

    nmos_out_a = nmos(data_a, pmos_out_b)
    nmos_out_b = nmos(data_b, pmos_out_b)
    grounded = nmos_out_a | nmos_out_b

    if grounded:
        return GROUND
    return pmos_out_b

def and_gate(data_a:Bit, data_b:Bit, power:Bit = None) -> Bit:
    power = power if power != None else Bit(True)
    nand_out = nand_gate(data_a, data_b, power)
    return not_gate(nand_out, power)

def or_gate(data_a:Bit, data_b:Bit, power:Bit = None) -> Bit:
    power = power if power != None else Bit(True)
    nor_out = nor_gate(data_a, data_b, power)
    return not_gate(nor_out, power)

def mux_gate(data_a:Bit, data_b:Bit, control:Bit, power:Bit = None) -> Bit:
    power = power if power != None else Bit(True)
    not_control_out = not_gate(control, power)
    a_and_control_out = and_gate(data_a, not_control_out, power)
    b_and_control_out = and_gate(data_b, control, power)
    
    a_and_control_out_or_b_and_control_out_out = or_gate(a_and_control_out, b_and_control_out, power)
    
    return a_and_control_out_or_b_and_control_out_out

def one_bit_adder(data_a:Bit, data_b:Bit, carry_in:Bit, power:Bit = None) -> Bit:
    power = power if power != None else Bit(True)
    c_and_a = and_gate(carry_in, data_a, power)
    c_and_b = and_gate(carry_in, data_b, power)
    a_and_b = and_gate(data_a, data_b, power)

    c_and_a_or_c_and_b_or_a_and_b = or_gate(or_gate(data_a, data_b, power), carry_in, power)

    return c_and_a_or_c_and_b_or_a_and_b

def xor_gate(data_a: Bit, data_b: Bit, power: Bit = None) -> Bit:
    """
    XOR implemented from primitive gates:
      XOR = (a OR b) AND NOT(a AND b)
    """
    power = power if power is not None else Bit(True)
    a_or_b = or_gate(data_a, data_b, power)
    a_and_b = and_gate(data_a, data_b, power)
    not_a_and_b = not_gate(a_and_b, power)
    return and_gate(a_or_b, not_a_and_b, power)

def xnor_gate(data_a: Bit, data_b: Bit, power: Bit = None) -> Bit:
    """
    XNOR = NOT(XOR)
    """
    power = power if power is not None else Bit(True)
    return not_gate(xor_gate(data_a, data_b, power), power)

def and3_gate(a: Bit, b: Bit, c: Bit, power: Bit = None) -> Bit:
    """
    3-input AND built from 2-input AND.
    """
    power = power if power is not None else Bit(True)
    return and_gate(and_gate(a, b, power), c, power)

def or3_gate(a: Bit, b: Bit, c: Bit, power: Bit = None) -> Bit:
    """
    3-input OR built from 2-input OR.
    """
    power = power if power is not None else Bit(True)
    return or_gate(or_gate(a, b, power), c, power)

def high_level_mux(in_0:tuple[Bit,...], in_1:tuple[Bit,...], control_bit:Bit) -> tuple[Bit,...]:
    if control_bit:
        return in_1
    else:
        return in_0