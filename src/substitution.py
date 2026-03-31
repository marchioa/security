
import string
from typing import Optional
from math import gcd

import matplotlib.pyplot as plt
from matplotlib.axes._axes import Axes

import numpy as np


def caesar_encrypt(plaintext: str, shift: int = 0) -> str:
    ''' Encrypt `plaintext` (str) as a caesar cipher with a given `shift` (int)
        and return the `ciphertext` (str) '''
    # define plaintext alphabet
    plain_alphabet = string.ascii_lowercase
    # define ciphertext alphabet
    cipher_alphabet = plain_alphabet[shift:] + plain_alphabet[:shift]
    # build a mapping that trasforms a plaintext letter into a ciphertext letter
    mapping = dict(zip(plain_alphabet, cipher_alphabet))
    # apply the transformation to the plaintext
    ciphertext = ''.join(mapping.get(char, char) for char in plaintext)
    return ciphertext


def caesar_decrypt(ciphertext: str, shift: int = 0) -> str:
    ''' Decrypt `ciphertext` (str) as a caesar cipher with a given `shift` (int)
        and return the `plaintext` (str) '''
    # define plaintext alphabet
    plain_alphabet = string.ascii_lowercase
    # define ciphertext alphabet
    cipher_alphabet = plain_alphabet[shift:] + plain_alphabet[:shift]
    # build a mapping that trasform a plaintext letter into a ciphertext letter
    mapping = dict(zip(cipher_alphabet, plain_alphabet))
    # apply the transformation to the plaintext
    plaintext = ''.join(mapping.get(char, char) for char in ciphertext)
    return plaintext


def simple_encrypt(plaintext: str, mapping: dict[str, str]) -> str:
    ''' Encrypt `plaintext` (str) as a simple substitution cipher with a given
       `mapping` (dict) from plaintext letters to ciphertext letters '''
    ciphertext = ''.join(mapping.get(char, char) for char in plaintext)
    return ciphertext


def simple_decrypt(ciphertext: str, mapping: dict[str, str]) -> str:
    ''' Decrypt `ciphertext` (str) as a simple substitution cipher with a given
       `mapping` (dict) from plaintext letters to ciphertext letters '''
    inv_mapping = dict(zip(mapping.values(), mapping.keys()))
    plaintext = ''.join(inv_mapping.get(char, char) for char in ciphertext)
    return plaintext


def letter_distribution(text: str) -> dict[str, float]:
    ''' Return the `distribution` (dict) of the letters in `text` (str) '''
    alphabet = string.ascii_lowercase
    hist = np.empty(len(alphabet), dtype=int)
    for i, letter in enumerate(alphabet):
        hist[i] = text.lower().count(letter)
    hist = map(float, hist / np.sum(hist))
    distribution = dict(zip(alphabet, hist))
    return distribution


def plot_distribution(
        distribution: dict[str, float],
        ax: Optional[Axes] = None,
        title: Optional[str] = None,
    ) -> None:
    ''' plot a letter distribution'''
    if ax is None:
        fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(np.arange(len(distribution)), list(distribution.values()), 1)
    ax.set(xticks=np.arange(len(distribution)), xticklabels=distribution.keys())
    ax.set(xlabel='letter', ylabel='probability', title=title)
    ax.grid()


def vigenere_encrypt(plaintext: str, key: str) -> str:
    ''' Encrypt `plaintext` (str) as a Vigenere cipher with a given `key` (str)
       and return the corresponding ciphertext (str)'''
    ciphertext = ''
    alphabet = string.ascii_lowercase
    k = 0  # key index
    for char in plaintext:
        if char in alphabet:
            shift = alphabet.index(key[k])
            k = (k + 1) % len(key)
            idx = (alphabet.index(char) + shift) % len(alphabet)
            ciphertext += alphabet[idx]
        else:
            ciphertext += char
    return ciphertext


def vigenere_decrypt(ciphertext: str, key: str) -> str:
    ''' Decrypt `ciphertext` (str) as a Vigenere cipher with a given `key` (str)
       and return the corresponding plaintext (str)'''
    plaintext = ''
    alphabet = string.ascii_lowercase
    k = 0  # key index
    for char in ciphertext:
        if char in alphabet:
            shift = alphabet.index(key[k])
            k = (k + 1) % len(key)
            idx = (alphabet.index(char) - shift) % len(alphabet)
            plaintext += alphabet[idx]
        else:
            plaintext += char
    return plaintext


def affine_encrypt(plaintext: str, a: int, b: int) -> str:
    ''' Encrypt `plaintext` (str) as an Affine cipher with a given `key` made
    of two values `a` (int) and `b` (int) and return the corresponding
    ciphertext (str) '''
    alphabet = string.ascii_lowercase
    # 'a' must be coprime with 26 to ensure the existence the inverse of 'a'
    if gcd(a, len(alphabet)) != 1:
        raise ValueError(f"'a' must have an inverse w.r.t. {len(alphabet)}")
    mapping = {
        letter: alphabet[(a * alphabet.index(letter) + b) % len(alphabet)]
        for letter in alphabet
    }
    ciphertext = ''.join(mapping.get(char, char) for char in plaintext)
    return ciphertext


def affine_decrypt(ciphertext: str, a: int, b: int) -> str:
    ''' Decrypt `ciphertext` (str) as an Affine cipher with a given `key` made
    of two values `a` (int) and `b` (int) and return the corresponding
    plaintext (str)'''
    alphabet = string.ascii_lowercase
    if gcd(a, len(alphabet)) != 1:
        raise ValueError(f"'a' must have an inverse w.r.t. {len(alphabet)}")
    inv_mapping = {
        alphabet[(a * alphabet.index(letter) + b) % len(alphabet)]: letter
        for letter in alphabet
    }
    plaintext = ''.join([inv_mapping.get(char, char) for char in ciphertext])
    return plaintext