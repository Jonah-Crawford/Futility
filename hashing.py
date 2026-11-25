import hashlib
import re

HASH_BITS = 512
HASH_BYTES = 64
NONCE_BITS = 513
NONCE_BYTES = 65
INITIAL_HASH = bytes(HASH_BYTES)


def make_context(index, opcode, previous_hash, bits=HASH_BITS):
  if not 1 <= bits <= HASH_BITS:
    raise ValueError('INVALID_HASH_LENGTH')
  if index < 0 or len(previous_hash) != HASH_BYTES:
    raise ValueError('INVALID_CONTEXT')
  if not re.fullmatch(r'[+\-<>~\[\].,]|\?(?:0|[1-9][0-9]*)', opcode):
    raise ValueError('INVALID_OPCODE')
  return (b'FUTILITY\x00' + previous_hash
          + str(index).encode('ascii') + b'\x00'
          + opcode.encode('ascii') + b'\x00'
          + bits.to_bytes(2, 'big'))


def digest(context, nonce):
  if not 0 <= nonce < 2**NONCE_BITS:
    raise ValueError('INVALID_NONCE')
  return hashlib.sha512(context + nonce.to_bytes(NONCE_BYTES, 'big')).digest()


def hash_bits(raw, bits):
  return int.from_bytes(raw, 'big') >> (HASH_BITS - bits)


def validate(index, opcode, previous_hash, a, b, bits=HASH_BITS):
  context = make_context(index, opcode, previous_hash, bits)
  if a == b:
    raise ValueError('IDENTICAL_NONCES')
  ha, hb = digest(context, a), digest(context, b)
  if hash_bits(ha, bits) != hash_bits(hb, bits):
    raise ValueError('COLLISION_NOT_FOUND')
  return ha
