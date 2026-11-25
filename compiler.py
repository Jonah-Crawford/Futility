import argparse
import os
import sys
import tempfile
from pathlib import Path
from binary import (OFFICIAL, DEVELOPMENT, file_header, block_size,
  instruction_header, write_block)
from hashing import INITIAL_HASH, NONCE_BYTES
from futility import parse


def main():
  p = argparse.ArgumentParser()
  p.add_argument('source', type=Path)
  p.add_argument('output', type=Path)
  p.add_argument('--dev', action='store_true')
  p.add_argument('--bits', type=int)
  p.add_argument('--base', type=int)
  p.add_argument('--growth', type=int)
  p.add_argument('--limit', type=int, default=1000000, help='hash attempts per instruction; 0 for unlimited')
  p.add_argument('--max-bytes', type=int, default=64*1024*1024, help='output safety cap; 0 for unlimited')
  p.add_argument('--progress', type=int, default=100000)
  p.add_argument('--estimate', action='store_true')
  a = p.parse_args()
  tmp = None
  try:
    overrides = (a.bits, a.base, a.growth)
    if not a.dev and any(x is not None for x in overrides):
      raise ValueError('PROFILE_OVERRIDE_REQUIRES_DEV')
    if min(a.limit, a.max_bytes, a.progress) < 0:
      raise ValueError('INVALID_LIMIT')
    profile = tuple(d if x is None else x for x, d in zip(overrides, DEVELOPMENT if a.dev else OFFICIAL))
    header = file_header(profile)
    program = parse(a.source.read_text())
    size = len(header) + sum(block_size(i, len(instruction_header(op, arg)) + 2*NONCE_BYTES, profile) for i, (op, arg) in enumerate(program))
    print(f'{len(program)} instructions | {size:,} bytes | profile={profile}', file=sys.stderr)
    if a.estimate:
      return
    if a.max_bytes and size > a.max_bytes:
      raise RuntimeError('PHYSICAL_LIMITATION: output exceeds safety cap')
    if a.source.resolve() == a.output.resolve():
      raise ValueError('INPUT_OUTPUT_IDENTICAL')
    with tempfile.NamedTemporaryFile(dir=a.output.parent, delete=False) as f:
      tmp = f.name
      f.write(header)
      previous = INITIAL_HASH
      for i, (op, arg) in enumerate(program):
        previous = write_block(f, i, op, arg, previous, profile, a.limit or None, a.progress)
      if f.tell() != size:
        raise RuntimeError('SIZE_MISMATCH')
    os.replace(tmp, a.output)
    tmp = None
  except (OSError, ValueError, SyntaxError, RuntimeError, MemoryError, OverflowError) as e:
    p.exit(1, f'{e or "PHYSICAL_LIMITATION"}\n')
  finally:
    if tmp is not None:
      os.unlink(tmp)


if __name__ == '__main__':
  main()
