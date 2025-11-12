from memory import Bit
import gates as g

def decoder2x4(data_0:Bit, data_1:Bit, power:Bit = None) -> tuple[Bit,Bit,Bit,Bit]:
    power = power if power != None else Bit(True)
    d0_not = g.not_gate(data_0, power)
    d1_not = g.not_gate(data_1, power)

    and_0 = g.and_gate(d0_not, d1_not, power)

    and_1 = g.and_gate(data_0, d1_not, power)

    and_2 = g.and_gate(d0_not, data_1, power)

    and_3 = g.and_gate(data_0, data_1, power)

    return (and_0, and_1, and_2, and_3)

def decoder3x8(data_0:Bit, data_1:Bit, data_2:Bit, power:Bit = None) -> tuple[Bit,Bit,Bit,Bit,Bit,Bit,Bit,Bit]:
    power = power if power != None else Bit(True)
    
    d2_not = g.not_gate(data_2, power)

    dec2x4_0_out = decoder2x4(data_0, data_1, d2_not)

    dec2x4_1_out = decoder2x4(data_0, data_1, data_2)

    return dec2x4_0_out + dec2x4_1_out

def encoder8x3(data_0:Bit, data_1:Bit, data_2:Bit, data_3:Bit, data_4:Bit, data_5:Bit, data_6:Bit, data_7:Bit, power:Bit = None) -> tuple[Bit,Bit,Bit]:
    power = power if power != None else Bit(True)

    # data_0 goes to nothing or ground

    or_0_0 = g.or_gate(data_3, data_1, power)
    or_0_1 = g.or_gate(data_5, data_7, power)
    or_0 = g.or_gate(or_0_0, or_0_1, power)

    or_1_0 = g.or_gate(data_2, data_3, power)
    or_1_1 = g.or_gate(data_6, data_7, power)
    or_1 = g.or_gate(or_1_0, or_1_1, power)

    or_2_0 = g.or_gate(data_4, data_5, power)
    or_2_1 = g.or_gate(data_6, data_7, power)
    or_2 = g.or_gate(or_2_0, or_2_1, power)

    return (or_0, or_1, or_2)
