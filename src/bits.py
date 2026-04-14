from itertools import zip_longest

class Bits:

    def __init__(self, data=None, endianness='big', length=None):
        """ Initialize the Bits object from bytes, an integer, or a list of
        booleans."""
        if data is None:
            self.bits: list[bool] = []
        elif isinstance(data, Bits):
            self.bits = list(data.bits)
        elif isinstance(data, bytes):
            self.bits = Bits.from_bytes(data, endianness=endianness).bits
        elif isinstance(data, int):
            self.bits = Bits.from_int(data, length, endianness).bits
        elif isinstance(data, str) and all(bit in ('0', '1') for bit in data):
            self.bits = Bits.from_str(data).bits
        elif isinstance(data, (list, tuple)):
            if (len(data) == 0) or all(isinstance(bit, bool) for bit in data):
                self.bits = list(data)
            elif all(isinstance(bit, int) for bit in data):
                self.bits = [bool(bit) for bit in data]
            else:
                types = {type(b) for b in data}
                msg = "Unsupported data type as a sequence of "
                if len(types) > 1:
                    msg+= f"mixed types."
                else:
                    msg+= f"{list(types)[0].__name__}."
                raise ValueError(msg)

        else:
            _str = f"Unsupported data type {type(data).__name__}. "
            _str+= "Use bytes, int, or a list of booleans."
            raise ValueError(_str)
        if length is not None:
            self.bits = self.bits[:length]

    def __len__(self):
        return len(self.bits)

    def __str__(self):
        return ''.join(f'{bit:0b}' for bit in self.bits)

    def __repr__(self):
        return f'Bits("{str(self)}")'

    def __format__(self, format_spec):
        return format(self.__str__(), format_spec)

    def __iter__(self):
        return iter(self.bits)

    def __getitem__(self, index):
        bits = self.bits[index]
        return Bits(bits) if isinstance(index, slice) else bits

    def __setitem__(self, index, value):
        if isinstance(index, slice):
            self.bits[index] = [self._coerce_bit(b) for b in value]
        else:
            self.bits[index] = self._coerce_bit(value)

    def __xor__(self, other):
        self._check_operand(other)
        bits = [a ^ b for a, b in zip_longest(self, other, fillvalue=False)]
        return Bits(bits)

    def __and__(self, other):
        self._check_operand(other)
        bits = [a and b for a, b in zip_longest(self, other, fillvalue=False)]
        return Bits(bits)

    def __or__(self, other):
        self._check_operand(other)
        bits = [a or b for a, b in zip_longest(self, other, fillvalue=False)]
        return Bits(bits)

    def __invert__(self):
        return Bits([not b for b in self.bits])

    def __add__(self, other):
        """Concatenate two Bits objects."""
        self._check_operand(other)
        return Bits(self.bits + other.bits)

    def __mul__(self, scalar):
        """Replicate the Bits object by a scalar value,
        similar to list multiplication."""
        if not isinstance(scalar, int) or scalar < 0:
            raise ValueError("Multiplier must be a non-negative integer.")
        return Bits(self.bits * scalar)

    __rmul__ = __mul__

    def __eq__(self, other):
        """Check equality between two Bits objects."""
        if not isinstance(other, Bits):
            return NotImplemented
        return self.bits == other.bits

    def __rshift__(self, scalar):
        """Right shift the Bits object by a scalar value."""
        if not isinstance(scalar, int) or scalar < 0:
            raise ValueError("Shift value must be a non-negative integer.")
        return Bits([False] * scalar + self.bits)

    def __lshift__(self, scalar):
        """Left shift the Bits object by a scalar value."""
        if not isinstance(scalar, int) or scalar < 0:
            raise ValueError("Shift value must be a non-negative integer.")
        return Bits(self.bits[scalar:])

    def parity_bit(self):
        """Compute the parity bit (even parity). """
        return sum(self.bits) % 2 == 1

    def append(self, bit):
        """Append a single bit (boolean or 0/1 integer)."""
        self.bits.append(self._coerce_bit(bit))

    def pop(self, index=-1):
        """Remove and return a bit at the given index (default is the last bit)."""
        if not self.bits:
            raise IndexError("pop from empty Bits")
        return self.bits.pop(index)

    @staticmethod
    def _byte_to_bits(byte, endianness='big'):
        """ Convert a single byte into a sequence of booleans """
        Bits._check_endianness(endianness)
        bits = list(bool(byte & (1 << i)) for i in range(8))
        if endianness == 'big':
            bits = bits[::-1]
        return bits

    @classmethod
    def from_bytes(cls, data, endianness='big'):
        """ Create a Bits object from bytes """
        cls._check_endianness(endianness)
        bits = list(
            bit for byte in data
            for bit in cls._byte_to_bits(byte, endianness=endianness)
        )
        return cls(bits)

    def to_bytes(self, endianness='big'):
        """Convert Bits to a bytes string."""
        self._check_endianness(endianness)
        bytes_list = []
        for i in range(1 + (len(self.bits) - 1) // 8):
            byte = list(self.bits[8*i:8*(i+1)])  # select 8 bits at a time
            byte += [False] * (8 - len(byte))  # zero padding
            if endianness == 'big':
                byte = byte[::-1]  # invert bit order
            # turn 8 bits into a byte
            byte = sum(bit * 2**i for i, bit in enumerate(byte))
            bytes_list.append(byte)  # append byte to the list of bytes
        return bytes(bytes_list)  # turn list of bytes into a bytes object

    @classmethod
    def from_int(cls, value, length=None, endianness='big'):
        """ Create a Bits object from an integer """
        cls._check_endianness(endianness)
        if length is None:
            length = max(value.bit_length(), 1)
        bits = list(bool((value >> i) & 1)
                    for i in range(max(length, value.bit_length())))
        if endianness == 'big':
            bits = bits[::-1]
        return cls(bits[:length])

    def to_int(self, endianness='big'):
        """Convert Bits to an integer."""
        self._check_endianness(endianness)
        integer = sum(bit << (i if endianness == 'little'
                              else len(self.bits) - 1 - i)
                              for i, bit in enumerate(self.bits))
        return integer

    @classmethod
    def from_sparse(cls, sparse, length=None):
        """ Create a Bits object from a set of indexes of non-zero bits """
        sparse = set(sparse)
        if length is None:
            length = max(sparse) + 1 if sparse else 0
        bits = [i in sparse for i in range(length)]
        return cls(bits)

    def to_sparse(self):
        """Convert Bits to set of indexes of non-zero bits."""
        sparse = set(i for i, bit in enumerate(self.bits) if bit)
        return sparse

    @classmethod
    def from_str(cls, value):
        """ Create a Bits object from a string """
        bits = list(bool(int(bit)) for bit in value)
        return cls(bits)

    def copy(self):
        return Bits(self.bits[:])

    @staticmethod
    def _check_endianness(endianness):
        if not (endianness in ('big', 'little')):
            _str = f"Unsupported {endianness} endianness."
            _str+= "Use 'big' or 'little'."
            raise ValueError(_str)

    @staticmethod
    def _coerce_bit(bit) -> bool:
        """Convert a bit value to bool, accepting booleans and 0/1 integers."""
        if isinstance(bit, bool):
            return bit
        if isinstance(bit, int):
            return bool(bit)
        raise ValueError("Bits must be booleans or 0/1 integers.")

    @staticmethod
    def _check_operand(other):
        if not isinstance(other, Bits):
            raise ValueError("Operand must be a Bits instance.")

