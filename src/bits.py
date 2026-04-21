from __future__ import annotations
from enum import Enum
from itertools import zip_longest
from typing import Iterator, Sequence, overload

class Endianness(Enum):
    BIG = 'big'
    LITTLE = 'little'

class Bits:

    def __init__(
            self,
            data: None | Bits | bytes | int | str | list | tuple = None,
            endianness: str | Endianness = 'big',
            length: int | None = None
        ) -> None:
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

    def __len__(self) -> int:
        return len(self.bits)

    def __str__(self) -> str:
        return ''.join(f'{bit:0b}' for bit in self.bits)

    def __repr__(self) -> str:
        return f'Bits("{str(self)}")'

    def __format__(self, format_spec: str) -> str:
        return format(self.__str__(), format_spec)

    def __iter__(self) -> Iterator[bool]:
        return iter(self.bits)

    @overload
    def __getitem__(self, index: int) -> bool: ...
    @overload
    def __getitem__(self, index: slice) -> Bits: ...
    def __getitem__(self, index: int | slice) -> bool | Bits:
        if isinstance(index, slice):
            return Bits(self.bits[index])
        return self.bits[index]

    def __setitem__(
            self,
            index: int | slice,
            value: bool | int | Sequence[bool | int]
        ) -> None:
        if isinstance(index, slice):
            self.bits[index] = [
                self._coerce_bit(b) for b in value]  # type: ignore[union-attr]
        else:
            self.bits[index] = self._coerce_bit(value)  # type: ignore[arg-type]

    def __xor__(self, other: Bits) -> Bits:
        bits = [a ^ b for a, b in zip_longest(self, other, fillvalue=False)]
        return Bits(bits)

    def __and__(self, other: Bits) -> Bits:
        bits = [a and b for a, b in zip_longest(self, other, fillvalue=False)]
        return Bits(bits)

    def __or__(self, other: Bits) -> Bits:
        bits = [a or b for a, b in zip_longest(self, other, fillvalue=False)]
        return Bits(bits)

    def __invert__(self) -> Bits:
        return Bits([not b for b in self.bits])

    def __add__(self, other: Bits) -> Bits:
        """Concatenate two Bits objects."""
        return Bits(self.bits + other.bits)

    def __mul__(self, scalar: int) -> Bits:
        """Replicate the Bits object by a scalar value,
        similar to list multiplication."""
        if not isinstance(scalar, int) or scalar < 0:
            raise ValueError("Multiplier must be a non-negative integer.")
        return Bits(self.bits * scalar)

    __rmul__ = __mul__

    def __eq__(self, other: object) -> bool:
        """Check equality between two Bits objects."""
        if not isinstance(other, Bits):
            return NotImplemented
        return self.bits == other.bits

    def __rshift__(self, scalar: int) -> Bits:
        """Right shift the Bits object by a scalar value."""
        if not isinstance(scalar, int) or scalar < 0:
            raise ValueError("Shift value must be a non-negative integer.")
        return Bits([False] * scalar + self.bits)

    def __lshift__(self, scalar: int) -> Bits:
        """Left shift the Bits object by a scalar value."""
        if not isinstance(scalar, int) or scalar < 0:
            raise ValueError("Shift value must be a non-negative integer.")
        return Bits(self.bits[scalar:])

    def parity_bit(self) -> bool:
        """Compute the parity bit (even parity). """
        return sum(self.bits) % 2 == 1

    def append(self, bit: bool | int) -> None:
        """Append a single bit (boolean or 0/1 integer)."""
        self.bits.append(self._coerce_bit(bit))

    def pop(self, index: int = -1) -> bool:
        """Remove and return a bit at the given index (default: last bit)."""
        if not self.bits:
            raise IndexError("pop from empty Bits")
        return self.bits.pop(index)

    def insert(self, index: int, bit: bool | int) -> None:
        """Insert a single bit (boolean or 0/1 integer) at the given index."""
        self.bits.insert(index, self._coerce_bit(bit))

    @staticmethod
    def _coerce_endianness(endianness: str | Endianness) -> Endianness:
        if isinstance(endianness, Endianness):
            return endianness
        elif endianness in ('big', 'little'):
            return Endianness(endianness)
        else:
            msg = f"Unsupported endianness '{endianness}'."
            msg+= " Use 'big' or 'little'."
            raise ValueError(msg)

    @staticmethod
    def _byte_to_bits(
            byte: int,
            endianness: Endianness = Endianness.BIG
        ) -> list[bool]:
        """ Convert a single byte into a sequence of booleans """
        bits = list(bool(byte & (1 << i)) for i in range(8))
        if endianness == Endianness.BIG:
            bits = bits[::-1]
        return bits

    @classmethod
    def from_bytes(
            cls,
            data: bytes,
            endianness: str | Endianness = 'big'
        ) -> Bits:
        """ Create a Bits object from bytes """
        end = cls._coerce_endianness(endianness)
        bits = list(
            bit for byte in data
            for bit in cls._byte_to_bits(byte, endianness=end)
        )
        return cls(bits)

    def to_bytes(self, endianness: str | Endianness = 'big') -> bytes:
        """Convert Bits to a bytes string."""
        end = self._coerce_endianness(endianness)
        bytes_list = []
        for i in range(1 + (len(self.bits) - 1) // 8):
            byte = list(self.bits[8*i:8*(i+1)])  # select 8 bits at a time
            byte += [False] * (8 - len(byte))  # zero padding
            if end == Endianness.BIG:
                byte = byte[::-1]  # invert bit order
            # turn 8 bits into a byte
            byte = sum(bit * 2**i for i, bit in enumerate(byte))
            bytes_list.append(byte)  # append byte to the list of bytes
        return bytes(bytes_list)  # turn list of bytes into a bytes object

    @classmethod
    def from_int(
            cls,
            value: int,
            length: int | None = None,
            endianness: str | Endianness = 'big'
        ) -> Bits:
        """ Create a Bits object from an integer """
        end = cls._coerce_endianness(endianness)
        if length is None:
            length = max(value.bit_length(), 1)
        bits = list(bool((value >> i) & 1)
                    for i in range(max(length, value.bit_length())))
        if end == Endianness.BIG:
            bits = bits[::-1]
        return cls(bits[:length])

    def to_int(self, endianness: str | Endianness = 'big') -> int:
        """Convert Bits to an integer."""
        end = self._coerce_endianness(endianness)
        integer = sum(bit << (i if end == Endianness.LITTLE
                              else len(self.bits) - 1 - i)
                              for i, bit in enumerate(self.bits))
        return integer

    @classmethod
    def from_sparse(
            cls,
            sparse: set[int] | list[int],
            length: int | None = None
        ) -> Bits:
        """ Create a Bits object from a set of indexes of non-zero bits """
        sparse = set(sparse)
        if length is None:
            length = max(sparse) + 1 if sparse else 0
        bits = [i in sparse for i in range(length)]
        return cls(bits)

    def to_sparse(self) -> set[int]:
        """Convert Bits to set of indexes of non-zero bits."""
        sparse = set(i for i, bit in enumerate(self.bits) if bit)
        return sparse

    @classmethod
    def from_str(cls, value: str) -> Bits:
        """ Create a Bits object from a string """
        bits = list(bool(int(bit)) for bit in value)
        return cls(bits)

    def copy(self) -> Bits:
        return Bits(self.bits[:])

    @staticmethod
    def _coerce_bit(bit: bool | int) -> bool:
        """Convert a bit value to bool, accepting booleans and 0/1 integers."""
        if isinstance(bit, bool):
            return bit
        if isinstance(bit, int):
            return bool(bit)
        raise ValueError("Bits must be booleans or 0/1 integers.")