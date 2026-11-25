import sys
from math import isqrt

if hasattr(sys, 'set_int_max_str_digits'):
  sys.set_int_max_str_digits(0)


def parse(source):
  program = []
  i = 0
  while i < len(source):
    c = source[i]
    i += 1
    if c.isspace():
      continue
    if c == '?':
      start = i
      while i < len(source) and source[i] in '0123456789':
        i += 1
      if start == i:
        raise SyntaxError('MISPLACED_AMBITION')
      program.append((c, int(source[start:i])))
    elif c in '+-<>~[].,':
      program.append((c, None))
    else:
      raise SyntaxError(f'UNKNOWN_FUTILITY: {c!r}')
  check_program(program)
  return program


def check_program(program):
  stack, pairs = [], {}
  for i, (op, arg) in enumerate(program):
    if op == '[':
      stack.append(i)
    elif op == ']':
      if not stack:
        raise SyntaxError('UNREQUITED_BRACKET')
      start = stack.pop()
      pairs[start], pairs[i] = i, start
    elif op == '?' and not 0 <= arg <= len(program):
      raise SyntaxError('MISPLACED_AMBITION')
  if stack:
    raise SyntaxError('UNREQUITED_BRACKET')
  return pairs


class Futility:
  def __init__(self, source, stdin=None, stdout=None):
    self.program = parse(source) if isinstance(source, str) else list(source)
    self.brackets = check_program(self.program)
    self.memory = {}
    self.p = self.ip = self.cycles = 0
    self.primes = [2]
    self.stdin = sys.stdin.buffer if stdin is None else stdin
    self.stdout = sys.stdout.buffer if stdout is None else stdout

  def get(self, address):
    return self.memory.get(address, 0)

  def set(self, address, value):
    if value:
      self.memory[address] = value
    else:
      self.memory.pop(address, None)

  def prime(self, index):
    while len(self.primes) <= index:
      candidate = self.primes[-1] + 1
      while not all(candidate % q for q in self.primes if q <= isqrt(candidate)):
        candidate += 1
      self.primes.append(candidate)
    return self.primes[index]

  def condition(self):
    n = max(0, self.get(self.p - 1))
    total = sum(self.get(self.p + self.prime(i)) for i in range(n))
    return total >= 0 and isqrt(total) ** 2 == total

  def step(self):
    if self.ip >= len(self.program):
      return False
    op, arg = self.program[self.ip]
    p = self.p
    l, c, r = (self.get(p + i) for i in (-1, 0, 1))
    nxt = self.ip + 1
    if op in '+-':
      self.set(p, c + (1 if op == '+' else -1))
      self.set(p - 1, l * 2)
      self.set(p + 1, r * 2)
    elif op == '>':
      self.p += 1
    elif op == '<':
      self.p -= 1
    elif op == '~':
      self.set(p, -c)
      self.set(p - 1, r)
      self.set(p + 1, l)
    elif op == '[' and not self.condition():
      nxt = self.brackets[self.ip] + 1
    elif op == ']' and self.condition():
      nxt = self.brackets[self.ip] + 1
    elif op == '?' and self.condition():
      nxt = arg
    elif op == '.':
      self.stdout.write(bytes([(l ^ c ^ r) % 256]))
      self.stdout.flush()
    elif op == ',':
      byte = self.stdin.read(1)
      self.set(p, byte[0] if byte else -1)
      self.set(p - 1, -l)
      self.set(p + 1, -r)
    self.ip = nxt
    self.cycles += 1
    return True

  def run(self, limit=None):
    while self.ip < len(self.program):
      if limit is not None and self.cycles >= limit:
        raise RuntimeError('CIVILISATION_TIMEOUT')
      self.step()


if __name__ == '__main__':
  if len(sys.argv) != 2:
    sys.exit('Usage: python futility.py <assembly>')
  with open(sys.argv[1]) as f:
    Futility(f.read()).run()
