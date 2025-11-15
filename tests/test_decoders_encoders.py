from memory import Bit
import pytest

from encoder_decoder import (
    decoder2x4, decoder3x8, decoder4x16, decoder5x32,
    encoder8x3, one_hot_to_decimal
)

# Unit Tests created with assistance from AI to ensure correctness.

# Utility: convert integer → tuple of Bits
def int_to_bits(n, width):
    return tuple(Bit(bool((n >> i) & 1)) for i in range(width))

# Utility: convert tuple[Bit] one-hot → integer index
def one_hot_index(bits):
    for i, b in enumerate(bits):
        if b.value:  # Bit(True)
            return i
    return None


##############################################
# 2 → 4 DECODER
##############################################

def test_decoder2x4_exhaustive():
    for i in range(4):
        b0, b1 = int_to_bits(i, 2)
        out = decoder2x4(b0, b1)

        assert len(out) == 4
        assert sum(bit.value for bit in out) == 1, f"Not one-hot: {out}"

        expected = i
        actual = one_hot_index(out)
        assert actual == expected, f"decoder2x4({i}) gave {actual}, expected {expected}"


##############################################
# 3 → 8 DECODER
##############################################

def test_decoder3x8_exhaustive():
    for i in range(8):
        b0, b1, b2 = int_to_bits(i, 3)
        out = decoder3x8(b0, b1, b2)

        assert len(out) == 8
        assert sum(bit.value for bit in out) == 1

        expected = i
        actual = one_hot_index(out)
        assert actual == expected


##############################################
# 4 → 16 DECODER
##############################################

def test_decoder4x16_exhaustive():
    for i in range(16):
        b0, b1, b2, b3 = int_to_bits(i, 4)
        out = decoder4x16(b0, b1, b2, b3)

        assert len(out) == 16
        assert sum(bit.value for bit in out) == 1

        expected = i
        actual = one_hot_index(out)
        assert actual == expected


##############################################
# 5 → 32 DECODER
##############################################

def test_decoder5x32_exhaustive():
    for i in range(32):
        b0, b1, b2, b3, b4 = int_to_bits(i, 5)
        out = decoder5x32(b0, b1, b2, b3, b4)

        assert len(out) == 32
        assert sum(bit.value for bit in out) == 1

        expected = i
        actual = one_hot_index(out)
        assert actual == expected


##############################################
# 8 → 3 ENCODER
##############################################

def test_encoder8x3_exhaustive_one_hot():
    """
    For each one-hot input, verify encoder output matches log2(index).
    """
    for i in range(8):
        # Create one-hot inputs
        inputs = [Bit(False)] * 8
        inputs[i] = Bit(True)

        out = encoder8x3(*inputs)

        assert len(out) == 3

        # Convert encoder output (3 Bits) into an integer
        encoded = (out[0].value << 0) | (out[1].value << 1) | (out[2].value << 2)
        assert encoded == i, f"encoder8x3({i}) → {encoded}, expected {i}"


##############################################
# DECODER / ENCODER CONSISTENCY
##############################################

def test_decoder3x8_encoder8x3_round_trip():
    """
    decoder3x8 → encoder8x3 should give original value (except input 0,
    because encoder treats data_0 as ground).
    """
    for i in range(1, 8):
        b0, b1, b2 = int_to_bits(i, 3)
        dec = decoder3x8(b0, b1, b2)

        # Feed decoder output back into encoder
        enc = encoder8x3(*dec)

        encoded = (enc[0].value << 0) | (enc[1].value << 1) | (enc[2].value << 2)
        assert encoded == i


##############################################
# POWER SIGNAL TESTING
##############################################

def test_power_signal_variations():
    """
    Ensure that power=True or custom Bit(True) does not break behavior.
    """
    for i in range(4):
        b0, b1 = int_to_bits(i, 2)
        out = decoder2x4(b0, b1, Bit(True))

        assert sum(bit.value for bit in out) == 1
        assert one_hot_index(out) == i
