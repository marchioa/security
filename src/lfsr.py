from itertools import islice
from bits import Bits

primitive_polynomials = {
    2: ({0, 1, 2}, ),
    3: ({0, 1, 3}, ),
    4: ({0, 1, 4}, ),
    5: ({0, 2, 5}, {0, 1, 2, 3, 5}, ),
    6: ({0, 1, 6}, {0, 1, 4, 5, 6}, ),
    7: ({0, 1, 7}, {0, 2, 3, 4, 7}, {0, 1, 2, 3, 4, 5, 7}, ),
    8: ({0, 1, 2, 7, 8}, {0, 2, 4, 5, 6, 7, 8}, ),
    9: ({0, 4, 9}, {0, 3, 5, 6, 9}, {0, 2, 3, 6, 7, 8, 9}, ),
    10: ({0, 3, 10}, {0, 2, 3, 8, 10}, {0, 1, 2, 5, 6, 7, 10}, ),
    11: ({0, 2, 11}, {0, 1, 8, 10, 11}, {0, 1, 2, 5, 7, 9, 11}, ),
    12: ({0, 1, 2, 10, 12}, {0, 2, 6, 8, 9, 10, 12}, ),
    13: ({0, 3, 5, 8, 13}, {0, 1, 2, 5, 10, 12, 13}, ),
    14: ({0, 1, 11, 12, 14}, {0, 1, 3, 4, 5, 11, 14}, ),
    15: ({0, 1, 15}, {0, 3, 4, 12, 15}, {0, 5, 6, 7, 8, 13, 15}, ),
    16: ({0, 10, 12, 15, 16}, {0, 2, 9, 12, 13, 14, 16}, ),
    17: ({0, 3, 17}, {0, 4, 12, 16, 17}, {0, 2, 5, 6, 8, 13, 17}, ),
    18: ({0, 7, 18}, {0, 4, 11, 16, 18}, {0, 1, 4, 7, 8, 10, 18}, ),
    19: ({0, 3, 9, 10, 19}, {0, 6, 12, 13, 16, 18, 19}, ),
    20: ({0, 3, 20}, {0, 2, 7, 13, 20}, {0, 1, 10, 14, 16, 18, 20}, ),
    21: ({0, 2, 21}, {0, 3, 4, 9, 21}, {0, 6, 8, 14, 18, 19, 21}, ),
    22: ({0, 1, 22}, {0, 3, 7, 12, 22}, {0, 2, 4, 9, 14, 21, 22}, ),
    23: ({0, 5, 23}, {0, 4, 8, 15, 23}, {0, 5, 11, 12, 13, 17, 23}, ),
    24: ({0, 2, 5, 11, 24}, {0, 3, 6, 7, 16, 23, 24}, ),
    25: ({0, 3, 25}, {0, 7, 12, 13, 25}, {0, 7, 10, 13, 15, 23, 25}, ),
    26: ({0, 13, 15, 23, 26}, {0, 1, 6, 15, 17, 24, 26}, ),
    27: ({0, 17, 22, 23, 27}, {0, 6, 11, 17, 18, 19, 27}, ),
    28: ({0, 3, 28}, {0, 5, 8, 24, 28}, {0, 5, 11, 21, 24, 27, 28}, ),
    29: ({0, 2, 29}, {0, 2, 6, 16, 29}, {0, 3, 11, 15, 16, 22, 29}, ),
    30: ({0, 9, 10, 27, 30}, {0, 11, 12, 24, 28, 29, 30}, ),
    31: ({0, 3, 31}, {0, 8, 23, 25, 31}, {0, 1, 8, 10, 14, 16, 31}, ),
    32: ({0, 2, 7, 16, 32}, {0, 1, 3, 12, 17, 30, 32}, ),
    33: ({0, 13, 33}, {0, 11, 16, 26, 33}, {0, 1, 8, 17, 19, 32, 33}, ),
    34: ({0, 8, 12, 17, 34}, {0, 4, 7, 14, 20, 31, 34}, ),
    35: ({0, 2, 35}, {0, 9, 17, 27, 35}, {0, 2, 21, 23, 31, 32, 35}, ),
    36: ({0, 11, 36}, {0, 7, 12, 33, 36}, {0, 6, 17, 25, 26, 28, 36}, ),
    37: ({0, 2, 14, 22, 37}, {0, 3, 21, 30, 31, 33, 37}, ),
    38: ({0, 5, 6, 27, 38}, {0, 6, 9, 11, 20, 36, 38}, ),
    39: ({0, 4, 39}, {0, 16, 23, 35, 39}, {0, 2, 13, 15, 36, 38, 39}, ),
    40: ({0, 23, 27, 29, 40}, {0, 6, 7, 18, 28, 36, 40}, ),
    41: ({0, 3, 41}, {0, 27, 31, 32, 41}, {0, 11, 12, 20, 32, 40, 41}, ),
    42: ({0, 30, 31, 34, 42}, {0, 1, 8, 14, 24, 27, 42}, ),
    43: ({0, 5, 22, 27, 43}, {0, 8, 25, 30, 32, 35, 43}, ),
    44: ({0, 18, 35, 39, 44}, {0, 5, 16, 25, 40, 43, 44}, ),
    45: ({0, 4, 28, 39, 45}, {0, 14, 15, 23, 27, 33, 45}, ),
    46: ({0, 18, 31, 40, 46}, {0, 21, 23, 24, 40, 44, 46}, ),
    47: ({0, 5, 47}, {0, 11, 24, 32, 47}, {0, 5, 17, 19, 32, 42, 47}, ),
    48: ({0, 1, 9, 19, 48}, {0, 5, 12, 27, 29, 43, 48}, ),
    49: ({0, 9, 49}, {0, 16, 18, 24, 49}, {0, 8, 39, 41, 42, 45, 49}, ),
    50: ({0, 17, 31, 34, 50}, {0, 5, 6, 16, 21, 36, 50}, ),
    51: ({0, 15, 24, 46, 51}, {0, 12, 15, 22, 24, 25, 51}, ),
}

class LFSR:

    def __init__(self, poly, state=None):
        self.length = max(poly)
        self.poly = poly
        self.state = state

    def __str__(self):
        return f'poly: {self.poly}, state: {self.state}, output: {self.output}'

    def __repr__(self):
        return f'LFSR(poly={self.poly}, state={self.state})'

    def __len__(self):
        return self.length
        
    def __iter__(self):
        return self

    def __next__(self):
        self.state.append(self.feedback)
        _ = self.state.pop(0)
        return self.output

    @property
    def state(self):
        return self._state
        
    @state.setter
    def state(self, state):
        if state is None:
            state = (1 << len(self)) - 1
        if not isinstance(state, Bits):
            state = Bits(state, length=len(self))
        self._state = state[:len(self)]

    @property
    def poly(self):
        return (self._poly + Bits(1))[::-1].to_sparse()
        
    @poly.setter
    def poly(self, poly):
        self._poly = Bits.from_sparse(poly)[1:][::-1]  # remove bit at index 0

    @property
    def feedback(self):
        return (self._state & self._poly).parity_bit()
    
    @feedback.setter
    def feedback(self, bit):
        raise AttributeError("Setting feedback is not allowed")

    @property
    def output(self):
        return self.state[0]
    
    @output.setter
    def output(self, bit):
        raise AttributeError("Setting output is not allowed")
    
    def run_steps(self, N=1):
        return Bits([bit for bit in islice(self, N)])
            
    def cycle(self, state=None):
        if state is not None:
            self.state = state
        state = self.state.copy()
        bits = Bits([next(self)])
        while self.state != state:
            bits.append(next(self))
        return bits
    

def berlekamp_massey(bits):
    '''
    Find the shortest LFSR for a given binary sequence.
    
    Parameters
    ----------
    bits: Bits or list of bool or bytes or str of 1/0 or int,
        stream of bits.
        
    Return
    ------
    set of int,
        linear feedback polynomial expressed as set of the degree of the 
        non-zero coefficients
    '''

    if not isinstance(bits, Bits):
        bits = Bits(bits)
    
    # variables initialization
    P, m = Bits(1), 0
    Q, r = Bits(1), 1
    
    for t in range(len(bits)):
        discrepancy = (P[:m+1] & bits[t-m:t+1][::-1][:len(P)]).parity_bit()
        if discrepancy:
            tmp = P
            P = P ^ (Q >> r)
            if 2*m <= t:  # branch A
                Q = tmp
                m = t + 1 - m
                r = 0
        r += 1
    
    return P.to_sparse()


