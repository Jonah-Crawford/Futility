import argparse
import json
import math
import sys
import time
from hashing import *


def find_collision(context, bits=HASH_BITS, limit=None, progress=100000):
  seen = {}
  start = time.monotonic()
  bound = 2**bits + 1
  if limit is not None:
    bound = min(bound, limit)
  for nonce in range(bound):
    h = hash_bits(digest(context, nonce), bits)
    if h in seen:
      return seen[h], nonce
    seen[h] = nonce
    if progress and (nonce + 1) % progress == 0:
      elapsed = max(time.monotonic() - start, 1e-9)
      print(f'{nonce + 1:,} hashes | {(nonce + 1)/elapsed:,.0f} H/s', file=sys.stderr)
  raise RuntimeError('CIVILISATION_TIMEOUT')


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('opcode')
  parser.add_argument('--index', type=int, default=0)
  parser.add_argument('--previous', default=INITIAL_HASH.hex())
  parser.add_argument('--bits', type=int, default=HASH_BITS)
  parser.add_argument('--limit', type=int)
  parser.add_argument('--progress', type=int, default=100000)
  args = parser.parse_args()
  try:
    previous = bytes.fromhex(args.previous)
    context = make_context(args.index, args.opcode, previous, args.bits)
    if args.limit is not None and args.limit < 1 or args.progress < 0:
      raise ValueError('INVALID_SEARCH_LIMIT')
    print(f'Expected hashes: {math.sqrt(math.pi/2)*2**(args.bits/2):.3e}', file=sys.stderr)
    a, b = find_collision(context, args.bits, args.limit, args.progress)
    h = validate(args.index, args.opcode, previous, a, b, args.bits)
    print(json.dumps({'index': args.index, 'opcode': args.opcode,
      'bits': args.bits, 'previous': previous.hex(), 'a': hex(a),
      'b': hex(b), 'next_hash': h.hex()}, indent=2))
  except (ValueError, RuntimeError, MemoryError) as e:
    parser.exit(1, f'{str(e) or "PHYSICAL_LIMITATION"}\n')
  except KeyboardInterrupt:
    parser.exit(130, 'SEARCH_INTERRUPTED\n')


if __name__ == '__main__':
  main()
