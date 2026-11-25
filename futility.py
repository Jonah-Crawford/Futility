
import sys
from math import isqrt


class Futility:
  def __init__(self, source):
    self.program = self.parse(source)
    self.brackets = self.match_brackets()
    self.memory = {}
    self.p = 0
    self.ip = 0
    self.primes = [2]
    self.cycles = 0

  def parse(self, source):
    program = []
    i = 0

    while i < len(source):
      c = source[i]

      if c.isspace():
        i += 1
        continue

      if c == "?":
        i += 1
        start = i

        while i < len(source) and source[i] in "0123456789":
          i += 1

        if start == i:
          raise SyntaxError("MISPLACED_AMBITION")

        program.append(("?", int(source[start:i])))
        continue

      if c not in "+-<>~[].,":
        raise SyntaxError(f"UNKNOWN_FUTILITY: {c!r}")

      program.append((c, None))
      i += 1

    for op, arg in program:
      if op == "?" and not 0 <= arg <= len(program):
        raise SyntaxError("MISPLACED_AMBITION")

    return program

  def match_brackets(self):
    stack = []
    pairs = {}

    for i, (op, _) in enumerate(self.program):
      if op == "[":
        stack.append(i)

      elif op == "]":
        if not stack:
          raise SyntaxError("UNREQUITED_BRACKET")

        start = stack.pop()
        pairs[start] = i
        pairs[i] = start

    if stack:
      raise SyntaxError("UNREQUITED_BRACKET")

    return pairs

  def get(self, address):
    return self.memory.get(address, 0)

  def set(self, address, value):
    if value == 0:
      self.memory.pop(address, None)
    else:
      self.memory[address] = value

  def prime(self, index):
    while len(self.primes) <= index:
      candidate = self.primes[-1] + 1

      while True:
        limit = isqrt(candidate)

        if all(
          candidate % q != 0
          for q in self.primes
          if q <= limit
        ):
          self.primes.append(candidate)
          break

        candidate += 1

    return self.primes[index]

  def condition(self):
    n = max(0, self.get(self.p - 1))
    total = 0

    for i in range(n):
      total += self.get(self.p + self.prime(i))

    return total >= 0 and isqrt(total) ** 2 == total

  def step(self):
    if self.ip >= len(self.program):
      return False

    op, arg = self.program[self.ip]

    p = self.p
    l = self.get(p - 1)
    c = self.get(p)
    r = self.get(p + 1)

    next_ip = self.ip + 1

    if op == "+":
      self.set(p, c + 1)
      self.set(p - 1, l * 2)
      self.set(p + 1, r * 2)

    elif op == "-":
      self.set(p, c - 1)
      self.set(p - 1, l * 2)
      self.set(p + 1, r * 2)

    elif op == ">":
      self.p += 1

    elif op == "<":
      self.p -= 1

    elif op == "~":
      self.set(p, -c)
      self.set(p - 1, r)
      self.set(p + 1, l)

    elif op == "[":
      if not self.condition():
        next_ip = self.brackets[self.ip] + 1

    elif op == "]":
      if self.condition():
        next_ip = self.brackets[self.ip] + 1

    elif op == "?":
      if self.condition():
        next_ip = arg

    elif op == ".":
      byte = (l ^ c ^ r) % 256
      sys.stdout.buffer.write(bytes([byte]))
      sys.stdout.buffer.flush()

    elif op == ",":
      byte = sys.stdin.buffer.read(1)
      self.set(p, byte[0] if byte else -1)
      self.set(p - 1, -l)
      self.set(p + 1, -r)

    self.ip = next_ip
    self.cycles += 1

    return True

  def run(self, limit=None):
    while self.ip < len(self.program):
      if limit is not None and self.cycles >= limit:
        raise RuntimeError("CIVILISATION_TIMEOUT")

      self.step()


if __name__ == "__main__":
  if len(sys.argv) != 2:
    print("Usage: python futility.py <source>")
    sys.exit(1)

  with open(sys.argv[1], "r") as f:
    source = f.read()

  vm = Futility(source)
  vm.run()
