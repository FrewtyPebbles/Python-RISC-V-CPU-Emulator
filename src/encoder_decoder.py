from memory import Bit, Bitx32
import gates as g

def decoder2x4(data_0:Bit, data_1:Bit, power:Bit = None) -> tuple[Bit,Bit,Bit,Bit]:
    power = power if power is not None else Bit(True)

    d0_not = g.not_gate(data_0, power)
    d1_not = g.not_gate(data_1, power)

    out0 = g.and_gate(d1_not, d0_not, power)  # 00
    out1 = g.and_gate(d1_not, data_0, power)  # 01
    out2 = g.and_gate(data_1, d0_not, power)  # 10
    out3 = g.and_gate(data_1, data_0, power)  # 11

    return (out0, out1, out2, out3)


def decoder3x8(data_0: Bit, data_1: Bit, data_2: Bit, power: Bit = None) -> tuple[Bit, ...]:
    power = power if power is not None else Bit(True)

    d2_not = g.not_gate(data_2, Bit(True))  # invert data_2 only, not power
    dec2x4_0_out = decoder2x4(data_0, data_1, d2_not)
    dec2x4_1_out = decoder2x4(data_0, data_1, data_2)

    # AND with global power
    dec2x4_0_out = tuple(g.and_gate(bit, power) for bit in dec2x4_0_out)
    dec2x4_1_out = tuple(g.and_gate(bit, power) for bit in dec2x4_1_out)

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

def decoder4x16(data_0: Bit, data_1: Bit, data_2: Bit, data_3: Bit, power: Bit = None) -> tuple[Bit, ...]:
    power = power if power is not None else Bit(True)

    # first 8 outputs enabled only if data_3 == 0
    dec3x8_0_out = decoder3x8(data_0, data_1, data_2)
    dec3x8_0_out = tuple(g.and_gate(bit, g.not_gate(data_3, Bit(True))) for bit in dec3x8_0_out)

    # last 8 outputs enabled only if data_3 == 1
    dec3x8_1_out = decoder3x8(data_0, data_1, data_2)
    dec3x8_1_out = tuple(g.and_gate(bit, data_3) for bit in dec3x8_1_out)

    # AND global power
    dec3x8_0_out = tuple(g.and_gate(bit, power) for bit in dec3x8_0_out)
    dec3x8_1_out = tuple(g.and_gate(bit, power) for bit in dec3x8_1_out)

    return dec3x8_0_out + dec3x8_1_out



def decoder5x32(data_0: Bit, data_1: Bit, data_2: Bit, data_3: Bit, data_4: Bit, power: Bit = None) -> Bitx32:
    power = power if power is not None else Bit(True)

    dec4x16_0_out = decoder4x16(data_0, data_1, data_2, data_3)
    dec4x16_0_out = tuple(g.and_gate(bit, g.not_gate(data_4, Bit(True))) for bit in dec4x16_0_out)

    dec4x16_1_out = decoder4x16(data_0, data_1, data_2, data_3)
    dec4x16_1_out = tuple(g.and_gate(bit, data_4) for bit in dec4x16_1_out)

    dec4x16_0_out = tuple(g.and_gate(bit, power) for bit in dec4x16_0_out)
    dec4x16_1_out = tuple(g.and_gate(bit, power) for bit in dec4x16_1_out)

    return dec4x16_0_out + dec4x16_1_out



def one_hot_to_decimal(one_hot:tuple[Bit,...]) -> int:
    for b_n, bit in enumerate(one_hot, 1):
        if bit:
            return b_n
        
    return 0