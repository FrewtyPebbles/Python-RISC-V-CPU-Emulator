import gates as g
from memory import Bit

class SRLatch:

    def __init__(self):
        self.Q:Bit = Bit(False)
        self.Q_bar:Bit = Bit(True)

    def update(self, S:Bit, R:Bit, power:Bit = None) -> tuple[Bit, Bit]:
        """
        Returns Q, Q_bar
        """
        power = power if power != None else Bit(True)
        Q_next = g.nor_gate(R, self.Q_bar, power)
        Q_bar_next = g.nor_gate(S, Q_next, power)
        self.Q, self.Q_bar = Q_next, Q_bar_next
        return (self.Q, self.Q_bar)
    
class DLatch(SRLatch):
    def update(self, D:Bit, C:Bit, power:Bit = None) -> tuple[Bit, Bit]:
        """
        Returns Q, Q_bar
        """
        power = power if power != None else Bit(True)
        D_not = g.not_gate(D, power)
        S = g.and_gate(C, D_not, power)
        R = g.and_gate(C, D, power)
        return super().update(S, R, power)
    
class DFlipFlop:
    
    def __init__(self):
        self.d_latch_0 = DLatch()
        self.d_latch_1 = DLatch()

    def update(self, D:Bit, C:Bit, power:Bit = None) -> tuple[Bit, Bit]:
        """
        Returns Q, Q_bar
        """
        power = power if power != None else Bit(True)
        
        d_latch_0_out = self.d_latch_0.update(D, C, power)

        C_not = g.not_gate(C, power)

        d_latch_1_out = self.d_latch_1.update(d_latch_0_out[0], C_not, power)
        
        return d_latch_1_out

