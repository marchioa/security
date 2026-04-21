from bits import Bits
from lfsr import LFSR



class AlternatingStep:

    def __init__(self, seed=None, polyC=None, poly0=None, poly1=None):

        if polyC is None:
            polyC = {5, 2, 0}
        if poly0 is None:
            poly0 = {3, 1, 0}
        if poly1 is None:
            poly1 = {4, 1, 0}

        max_length = max(polyC) + max(poly0) + max(poly1)
        if seed is None:
            seed = Bits(2**max_length - 1)
        if not isinstance(seed, Bits):
            seed = Bits(seed, length=max_length)

        self.lfsrC = LFSR(polyC, state=seed[:max(polyC)])
        self.lfsr0 = LFSR(poly0, state=seed[max(polyC):max(polyC) + max(poly0)])
        self.lfsr1 = LFSR(poly1, state=seed[max(polyC) + max(poly0):])

    def __iter__(self):
        return self

    def __next__(self):
        bitC = next(self.lfsrC)
        if bitC:
            next(self.lfsr1)
        else:
            next(self.lfsr0)
        return self.output

    @property
    def output(self):
        return self.lfsr0.output ^ self.lfsr1.output

    def __str__(self):
        lfsrs = (self.lfsrC, self.lfsr0, self.lfsr1)
        return '('+ ', '. join([f'{lfsr.state}' for lfsr in lfsrs]) + ')'

    def __repr__(self):
        seed = self.lfsrC.state + self.lfsr0.state + self.lfsr1.state
        kwargs_str = ', '.join([
            f"seed=Bits('{seed}')",
            f'polyC={self.lfsrC.poly}',
            f'poly0={self.lfsr0.poly}',
            f'poly1={self.lfsr1.poly}',
        ])
        return f'{type(self).__name__}({kwargs_str})'



class ShrinkingGenerator:

    def __init__(self, seed=None, polyA=None, polyS=None):

        if polyA is None:
            polyA = {5, 2, 0}
        if polyS is None:
            polyS = {3, 1, 0}

        max_length = max(polyA) + max(polyS)
        if seed is None:
            seed = Bits(2**max_length - 1)
        if not isinstance(seed, Bits):
            seed = Bits(seed, length=max_length)

        self.lfsrA = LFSR(polyA, state=seed[:max(polyA)])
        self.lfsrS = LFSR(polyS, state=seed[-max(polyS):])
        self.output = None

    def __iter__(self):
        return self

    def __next__(self):
        s = False
        while not s:
            a = next(self.lfsrA)
            s = next(self.lfsrS)
        self.output = a
        return self.output

    def __str__(self):
        lfsrs = (self.lfsrA, self.lfsrS)
        return '('+ ', '. join([f'{lfsr.state}' for lfsr in lfsrs]) + ')'

    def __repr__(self):
        kwargs_str = ', '.join([
            f"seed=Bits('{self.lfsrA.state + self.lfsrS.state}')",
            f'polyA={self.lfsrA.poly}',
            'polyS={self.lfsrS.poly}',
        ])
        return f'{type(self).__name__}({kwargs_str})'