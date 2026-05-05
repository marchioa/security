import numpy as np
from itertools import product
from typing import Iterator

from scipy.linalg import circulant

class AES:
    block_size = 16
    key_sizes = (16, 24, 32)
    _num_rounds = (10, 12, 14)

    SBOX = bytes.fromhex(
        # 0 1 2 3 4 5 6 7 8 9 a b c d e f
        '637c777bf26b6fc53001672bfed7ab76' # 0
        'ca82c97dfa5947f0add4a2af9ca472c0' # 1
        'b7fd9326363ff7cc34a5e5f171d83115' # 2
        '04c723c31896059a071280e2eb27b275' # 3
        '09832c1a1b6e5aa0523bd6b329e32f84' # 4
        '53d100ed20fcb15b6acbbe394a4c58cf' # 5
        'd0efaafb434d338545f9027f503c9fa8' # 6
        '51a3408f929d38f5bcb6da2110fff3d2' # 7
        'cd0c13ec5f974417c4a77e3d645d1973' # 8
        '60814fdc222a908846eeb814de5e0bdb' # 9
        'e0323a0a4906245cc2d3ac629195e479' # a
        'e7c8376d8dd54ea96c56f4ea657aae08' # b
        'ba78252e1ca6b4c6e8dd741f4bbd8b8a' # c
        '703eb5664803f60e613557b986c11d9e' # d
        'e1f8981169d98e949b1e87e9ce5528df' # e
        '8ca1890dbfe6426841992d0fb054bb16' # f
    )

    ROUND_CONSTS = (
        b'\x01\x00\x00\x00', b'\x02\x00\x00\x00',
        b'\x04\x00\x00\x00', b'\x08\x00\x00\x00',
        b'\x10\x00\x00\x00', b'\x20\x00\x00\x00',
        b'\x40\x00\x00\x00', b'\x80\x00\x00\x00',
        b'\x1b\x00\x00\x00', b'\x36\x00\x00\x00',
    )

    def __init__(self, key):
        if not isinstance(key, bytes):
            raise ValueError(f'Unsupported type {type(key).__name__} for key')
        key_size = len(key)
        if not (key_size in self.key_sizes):
            msg = f'Unsupported key length {key_size}B ({8*key_size}bit)'
            raise ValueError(msg)

        self.key_size = key_size
        self.key = key
        self.num_rounds = self._num_rounds[self.key_sizes.index(key_size)]

    @staticmethod
    def add_round_key(state: bytes, round_key: bytes) -> bytes:
        return bytes(s ^ k for s, k in zip(state, round_key))

    @staticmethod
    def byte_substitution(state: bytes) -> bytes:
        return bytes(AES.SBOX[byte] for byte in state)

    @staticmethod
    def inverse_byte_substitution(state: bytes) -> bytes:
        return bytes(AES.SBOX.index(byte) for byte in state)

    @staticmethod
    def shift_rows(state: bytes) -> bytes:
        mat = np.array(list(state), dtype=np.ubyte).reshape(-1, 4).T
        mat = np.vstack([np.roll(row, -i) for i, row in enumerate(mat)])
        return bytes(byte for byte in mat.T.flatten())

    @staticmethod
    def inverse_shift_rows(state: bytes) -> bytes:
        mat = np.array(list(state), dtype=np.ubyte).reshape(-1, 4).T
        mat = np.vstack([np.roll(row, i) for i, row in enumerate(mat)])
        return bytes(byte for byte in mat.T.flatten())

    @staticmethod
    def mul_by_x(byte: int) -> int:
        tmp = byte << 1
        if ((byte >> 7) & 0x01) > 0:
            tmp^= 0x1b  # computes mod P(x)
        return tmp

    @staticmethod
    def multiply(x, y):
        ''' Multiply-and-Sum Algorithm for multiplication '''
        z = 0
        for i in list(range(int(y).bit_length()))[::-1]:
            z = AES.mul_by_x(z)
            if bool((y >> i) & 0x01):
                z ^= x
        return z

    @staticmethod
    def dot_product(vec1, vec2):
        product = 0
        for e1, e2 in zip(vec1, vec2):
            product^= AES.multiply(e1, e2)
        return product

    @staticmethod
    def matrix_product(mat1, mat2):
        if len(mat1.shape) != 2 or len(mat2.shape) != 2 or \
            mat1.shape[1] != mat2.shape[0]:
            msg = f'Incompatible matrix sizes {mat1.shape} and {mat2.shape}'
            raise ValueError(msg)
        (n, k), (k, m) = mat1.shape, mat2.shape
        mat = np.zeros((n, m), np.ubyte)
        for i, row in enumerate(mat1):
            for j, col in enumerate(mat2.T):
                mat[i, j] = AES.dot_product(row, col)
        return mat

    @staticmethod
    def _mix_column(state, col):
        n = len(col)
        mat = circulant(col)
        X = np.array(list(state), dtype=np.ubyte).reshape(-1, n).T
        Y = AES.matrix_product(mat, X)
        return bytes(byte for byte in Y.T.flatten())

    @staticmethod
    def mix_column(state):
        col = np.array([0x02, 0x01, 0x01, 0x03], dtype=np.ubyte)
        return AES._mix_column(state, col)

    @staticmethod
    def inverse_mix_column(state):
        # first row of MixColumn matrix
        col = np.array([0x0e, 0x09, 0x0d, 0x0b], dtype=np.ubyte)
        return AES._mix_column(state, col)

    # @staticmethod
    # def mix_column(state):
    #     # first row of MixColumn matrix
    #     row = np.array([0x02, 0x03, 0x01, 0x01])
    #     n = len(row)
    #     X = np.array(list(state), dtype=np.ubyte).reshape(-1, n).T
    #     Y = np.zeros(X.shape, np.ubyte)
    #     for i, j in product(range(n), range(X.shape[-1])):
    #         for k, (q, x) in enumerate(zip(np.roll(row, i), X[:, j])):
    #             if q == 0x01:
    #                 Y[i, j]^= x
    #             elif q == 0x02:
    #                 Y[i, j]^= AES.mul_by_x(x)
    #             elif q == 0x03:
    #                 Y[i, j]^= x ^ AES.mul_by_x(x)
    #             else:
    #                 raise ValueError(f'Unexpected value {q}')
    #     return bytes(byte for byte in Y.T.flatten())

    @staticmethod
    def round(state: bytes , round_key: bytes) -> bytes:
        state = AES.byte_substitution(state)
        state = AES.shift_rows(state)
        state = AES.mix_column(state)
        state = AES.add_round_key(state, round_key)
        return state

    @staticmethod
    def final_round(state: bytes , round_key: bytes) -> bytes:
        state = AES.byte_substitution(state)
        state = AES.shift_rows(state)
        state = AES.add_round_key(state, round_key)
        return state

    @staticmethod
    def inverse_round(state: bytes , round_key: bytes) -> bytes:
        state = AES.add_round_key(state, round_key)
        state = AES.inverse_mix_column(state)
        state = AES.inverse_shift_rows(state)
        state = AES.inverse_byte_substitution(state)
        return state

    @staticmethod
    def inverse_final_round(state: bytes , round_key: bytes) -> bytes:
        state = AES.add_round_key(state, round_key)
        state = AES.inverse_shift_rows(state)
        state = AES.inverse_byte_substitution(state)
        return state

    @staticmethod
    def substitution_word(word: bytes) -> bytes:
        return bytes([AES.SBOX[byte] for byte in word])

    @staticmethod
    def rotate_word(word: bytes) -> bytes:
        return bytes(list(word)[1:] + list(word[:1]))

    @staticmethod
    def xor_words(x: bytes, y: bytes) -> bytes:
        return bytes([a ^ b for a, b in zip(x, y)])

    def key_schedule(self) -> Iterator[bytes]:

        num_words = self.key_size // 4
        total_words = 4 * (1 + self.num_rounds)

        words = []
        for i in range(num_words):
            words.append(bytes(byte for byte in self.key[4*i:4*(i+1)]))

        for j in range(num_words, total_words):
            word = words[j - 1]
            if j % num_words == 0:
                word = self.rotate_word(word)
                word = self.substitution_word(word)
                round_const = self.ROUND_CONSTS[j // num_words - 1]
                word = self.xor_words(word, round_const)
            elif (num_words == 8) and (j % 4 == 0):
                word = self.substitution_word(word)
            word = self.xor_words(word, words[j - num_words])
            words.append(word)

        for i in range(1 + self.num_rounds):
            yield b''.join(words[4*i:4*(i+1)])

    def key_expansion(self) -> tuple[bytes, ...]:
        return tuple(self.key_schedule())

    def encrypt_block(self, plaintext: bytes) -> bytes:
        round_keys = list(self.key_schedule())
        state = self.add_round_key(plaintext, round_keys[0])
        for round_key in round_keys[1:-1]:
            state = self.round(state, round_key)
        ciphertext = self.final_round(state, round_keys[-1])
        return ciphertext

    def decrypt_block(self, ciphertext: bytes) -> bytes:
        round_keys = list(self.key_schedule())[::-1]
        state = self.inverse_final_round(ciphertext, round_keys[0])
        for round_key in round_keys[1:-1]:
            state = self.inverse_round(state, round_key)
        plaintext = self.add_round_key(state, round_keys[-1])
        return plaintext