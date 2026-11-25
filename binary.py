import hashlib
from hashing import INITIAL_HASH, NONCE_BYTES, validate, make_context
from search import find_collision

OPS = '+-><~[]?.,'
MAGIC = b'FUT\x01'
OFFICIAL = (512, 60, 1)
DEVELOPMENT = (16, 8, 0)


def uleb(n):
  if n < 0:
    raise ValueError('INVALID_OPERAND')
  out = bytearray()
  while n >= 128:
    out.append((n & 127) | 128)
    n >>= 7
  out.append(n)
  return bytes(out)


def exact(f, n):
  data = f.read(n)
  if len(data) != n:
    raise ValueError('INSUFFICIENT_SOURCE')
  return data


def read_uleb(f):
  n = shift = count = 0
  while True:
    b = exact(f, 1)[0]
    n |= (b & 127) << shift
    count += 1
    if b < 128:
      if count > 1 and b == 0:
        raise ValueError('NONCANONICAL_OPERAND')
      return n, count
    shift += 7


def profile_check(profile):
  bits, base, growth = profile
  if not 1 <= bits <= 512 or base < 8 or growth < 0:
    raise ValueError('INVALID_PROFILE')


def file_header(profile):
  profile_check(profile)
  return MAGIC + b''.join(uleb(x) for x in profile)


def read_header(f):
  if exact(f, len(MAGIC)) != MAGIC:
    raise ValueError('INVALID_MAGIC')
  profile = tuple(read_uleb(f)[0] for _ in range(3))
  profile_check(profile)
  return profile


def opcode_text(op, arg):
  return '?' + str(arg) if op == '?' else op


def instruction_header(op, arg):
  return bytes([OPS.index(op)]) + (uleb(arg) if op == '?' else b'')


def block_size(index, header_size, profile):
  _, base, growth = profile
  return max(1 << (base + growth * index), header_size)


def payload(seed, length):
  h = seed
  while length:
    chunk = bytearray()
    while length and len(chunk) < 65536:
      h = hashlib.sha512(h).digest()
      part = h[:min(64, length)]
      chunk.extend(part)
      length -= len(part)
    yield bytes(chunk)


def write_block(f, index, op, arg, previous, profile, limit=None, progress=100000):
  bits, _, _ = profile
  header = instruction_header(op, arg)
  text = opcode_text(op, arg)
  context = make_context(index, text, previous, bits)
  a, b = find_collision(context, bits, limit, progress)
  seed = validate(index, text, previous, a, b, bits)
  header += a.to_bytes(NONCE_BYTES, 'big') + b.to_bytes(NONCE_BYTES, 'big')
  f.write(header)
  for chunk in payload(seed, block_size(index, len(header), profile) - len(header)):
    f.write(chunk)
  return seed


def decode(f, allow_dev=False):
  profile = read_header(f)
  if profile != OFFICIAL and not allow_dev:
    raise ValueError('DEVELOPMENT_SOURCE_REJECTED')
  previous = INITIAL_HASH
  program = []
  while True:
    raw = f.read(1)
    if not raw:
      break
    if raw[0] >= len(OPS):
      raise ValueError('INVALID_OPCODE')
    op = OPS[raw[0]]
    arg, operand_size = read_uleb(f) if op == '?' else (None, 0)
    a = int.from_bytes(exact(f, NONCE_BYTES), 'big')
    b = int.from_bytes(exact(f, NONCE_BYTES), 'big')
    index = len(program)
    previous = validate(index, opcode_text(op, arg), previous, a, b, profile[0])
    header_size = 1 + operand_size + 2 * NONCE_BYTES
    length = block_size(index, header_size, profile) - header_size
    for chunk in payload(previous, length):
      if exact(f, len(chunk)) != chunk:
        raise ValueError(f'PAYLOAD_CORRUPTION at instruction {index}')
    program.append((op, arg))
  return program
