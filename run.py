import argparse
from binary import decode
from futility import Futility


def main():
  p = argparse.ArgumentParser()
  p.add_argument('source')
  p.add_argument('--dev', action='store_true')
  p.add_argument('--limit', type=int)
  p.add_argument('--check', action='store_true')
  a = p.parse_args()
  try:
    with open(a.source, 'rb') as f:
      vm = Futility(decode(f, a.dev))
    if a.check:
      print(f'VALID: {len(vm.program)} instructions')
    else:
      vm.run(a.limit)
  except (OSError, ValueError, SyntaxError, RuntimeError, MemoryError, OverflowError) as e:
    p.exit(1, f'{e or "PHYSICAL_LIMITATION"}\n')


if __name__ == '__main__':
  main()
