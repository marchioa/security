from abc import ABC, abstractmethod

class BlockCipher(ABC):

    block_size: int
    modes = ('ECB', 'CBC', 'OFB', 'CFB')

    @abstractmethod
    def encrypt_block(self, plaintext: bytes) -> bytes:
        pass

    @abstractmethod
    def decrypt_block(self, ciphertext: bytes) -> bytes:
        pass

    def __init__(self, key: bytes, iv: bytes, mode: str = 'ECB'):
        self.key = key
        self.mode = mode
        self.iv = iv
        if mode == 'ECB':
            self._encrypt = self._encrypt_ecb
            self._decrypt = self._decrypt_ecb
        elif mode == 'CBC':
            self._encrypt = self._encrypt_cbc
            self._decrypt = self._decrypt_cbc
        elif mode == 'OFB':
            self._encrypt = self._crypt_ofb
            self._decrypt = self._crypt_ofb
        elif mode == 'CFB':
            self._encrypt = self._encrypt_cfb
            self._decrypt = self._decrypt_cfb
        else:
            raise ValueError(f"Unsupported mode of operation {mode}")

    def pad(self, text: bytes) -> bytes:  # PKCS7 Padding
        length = self.block_size - (len(text) % self.block_size)
        padding = bytes([length] * length)
        return text + padding

    def unpad(self, padded_text: bytes) -> bytes:  # PKCS7 Padding
        if len(padded_text) == 0 or len(padded_text) % self.block_size != 0:
            raise ValueError("Invalid padded data length.")
        length = padded_text[-1]
        if length < 1 \
            or length > self.block_size \
            or padded_text[-length:] != bytes([length] * length):
            raise ValueError(f"Invalid padding length {length}.")
        return padded_text[:-length]

    def split_into_blocks(self, text: bytes) -> tuple[bytes, ...]:
        num_blocks = len(text) // self.block_size
        blocks = tuple(
            text[i*self.block_size:(i+1)*self.block_size]
            for i in range(num_blocks)
        )
        return blocks

    # def split_into_blocks(self, text: bytes) -> Iterator[bytes]:
    #     num_blocks = len(text) // block_size
    #     for i in range(num_blocks):
    #         yield text[i*self.block_size:(i+1)*self.block_size]

    def encrypt(self, plaintext: bytes) -> bytes:
        ciphertext = self._encrypt(self.pad(plaintext))
        return ciphertext

    def decrypt(self, ciphertext: bytes) -> bytes:
        plaintext = self.unpad(self._decrypt(ciphertext))
        return plaintext

    def _encrypt_ecb(self, plaintext: bytes) -> bytes:
        ciphertext = b''
        for block in self.split_into_blocks(plaintext):
            ciphertext += self.encrypt_block(block)
        return ciphertext

    def _decrypt_ecb(self, ciphertext: bytes) -> bytes:
        plaintext = b''
        for block in self.split_into_blocks(ciphertext):
            plaintext += self.decrypt_block(block)
        return plaintext

    def _encrypt_cbc(self, plaintext: bytes) -> bytes:
        ciphertext = b''
        prev = self.iv
        for block in self.split_into_blocks(plaintext):
            tmp = self.xor(block, prev)
            prev = self.encrypt_block(tmp)
            ciphertext += prev
        return ciphertext

    def _decrypt_cbc(self, ciphertext: bytes) -> bytes:
        plaintext = b''
        prev = self.iv
        for block in self.split_into_blocks(ciphertext):
            tmp = self.decrypt_block(block)
            plaintext += self.xor(prev, tmp)
            prev = block
        return plaintext

    def _crypt_ofb(self, plaintext: bytes) -> bytes:
        ciphertext = b''
        prev = self.iv
        for block in self.split_into_blocks(plaintext):
            prev = self.encrypt_block(prev)
            ciphertext += self.xor(block, prev)
        return ciphertext

    def _encrypt_cfb(self, plaintext: bytes) -> bytes:
        ciphertext = b''
        prev = self.iv
        for block in self.split_into_blocks(plaintext):
            tmp = self.encrypt_block(prev)
            prev = self.xor(block, tmp)
            ciphertext += prev
        return ciphertext

    def _decrypt_cfb(self, ciphertext: bytes) -> bytes:
        plaintext = b''
        prev = self.iv
        for block in self.split_into_blocks(ciphertext):
            tmp = self.encrypt_block(prev)
            plaintext += self.xor(block, tmp)
            prev = block
        return plaintext

    @staticmethod
    def xor(x: bytes, y: bytes) -> bytes:
        return bytes([xi ^ yi for xi, yi in zip(x, y)])