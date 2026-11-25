import argparse
import json
import sys
from hashing import *


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('certificate', help='JSON certificate or - for stdin')
  parser.add_argument('--bits', type=int, default=HASH_BITS)
  parser.add_argument('--index', type=int, default=0)
  parser.add_argument('--previous', default=INITIAL_HASH.hex())
  parser.add_argument('--opcode')
  args = parser.parse_args()
  try:
    if args.certificate == '-':
      cert = json.load(sys.stdin)
    else:
      with open(args.certificate) as f:
        cert = json.load(f)
    previous = bytes.fromhex(args.previous)
    if (cert['bits'] != args.bits or cert['index'] != args.index
        or bytes.fromhex(cert['previous']) != previous
        or (args.opcode is not None and cert['opcode'] != args.opcode)):
      raise ValueError('CONTEXT_MISMATCH')
    h = validate(args.index, cert['opcode'], previous,
      int(cert['a'], 16), int(cert['b'], 16), args.bits)
    if h != bytes.fromhex(cert['next_hash']):
      raise ValueError('INVALID_NEXT_HASH')
    print('VALID' if args.bits == HASH_BITS else 'VALID (DEVELOPMENT ONLY)')
    print(h.hex())
  except (ValueError, KeyError, TypeError, OSError) as e:
    parser.exit(1, f'INVALID: {e}\n')


if __name__ == '__main__':
  main()
