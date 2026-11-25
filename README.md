# Futility

**Theoretically universal. Practically regrettable.**

`"Completely unusable (0/10)." - Google Gemini`

Futility is an esoteric programming language designed to be as impractical as possible without sacrificing Turing completeness. Unlike languages that are merely difficult to write, Futility is designed to be difficult to *compile*, even when the compiler knows exactly what it is doing.

Every instruction requires a context-dependent SHA-512 collision certificate and an exponentially expanding payload of chained SHA-512 hashes. Arithmetic corrupts neighbouring memory cells, control flow depends on prime numbers and perfect squares, and output is subject to unsolicited bitwise manipulation.

Running out of physical memory is a failing of the universe, not the language.

## Hello World

The repository includes a development-mode implementation of the traditional Hello World program.

```sh
python run.py hello.fut --dev
```

```text
Hello World!
```

To estimate the size of the same program under the official language specification:

```sh
python compiler.py hello.asm hello.fut --estimate
```

```text
389 instructions | 1,453,677,448,591,213,781,098,647,615,776,009,068,707,282,721,374,636,120,562,980,398,361,278,576,226,795,846,652,382,101,427,527,131,121,525,043,212,532,354,714,147,698,650,382,344 bytes | profile=(512, 60, 1)
```

This estimate excludes the computational cost of discovering the 389 SHA-512 collisions. It does, however, include the eight-byte file header.

The official binary has not been compiled, obviously. The development binary is approximately 100 kB and prints 13 bytes, including a trailing newline.

## System requirements

- Python 3.8 or newer; no external dependencies.
- A processor, any will do. The first and the latest processors are basically the same at this scale.
- Arbitrary-precision integers.
- A mathematically unbounded supply of memory and storage for unrestricted computation.
- Preferably a larger universe.

For the supplied Hello World implementation in official mode:

| Resource | Approximate requirement |
| --- | ---: |
| Source storage | 1.454 * 10^135 bytes |
| 8 TB drives | 1.817 * 10^122 |
| Writing time at 1 GB/s | 4.606 * 10^118 years |
| Classical collision-search queries | 5.645 * 10^79 |
| Sequential payload hashes | 2.271 * 10^133 |
| Useful output | 13 bytes |

These are estimates for the included program, not proven minimum requirements for Hello World. Hash-search estimates assume an ideal hash function and generic classical birthday search.

## Getting started

Run these commands from the repository directory. Development mode is a deliberately weakened encoding profile, not an official Futility program.

```sh
python compiler.py hello.asm hello.fut --dev
python run.py hello.fut --dev --check
python run.py hello.fut --dev
```

To write your own program, create `test.asm` containing:

```text
+++>++<.
```

```sh
python compiler.py test.asm test.fut --dev
python run.py test.fut --dev | xxd
```

Expected output: `0e`, the ASCII Shift Out control byte. After all that effort, nothing visible is printed.

The decoded virtual machine can also be tested directly with `python futility.py test.asm`. This bypasses the source encoding entirely and is not considered an official Futility execution.

### Compilation profiles

| Parameter | Development default | Official |
| --- | ---: | ---: |
| Collision bits | 16 | 512 |
| Initial block size | 256 bytes | 1 EiB |
| Block growth | Constant | Doubles per instruction |
| Nonce width | 513 bits | 513 bits |
| Payload hash | SHA-512 | SHA-512 |
| Instruction semantics | Identical | Identical |

To experiment with exponential growth on a small program:

```sh
python compiler.py test.asm test.fut --dev --bits 16 --base 8 --growth 1
```

The compiler accepts `--estimate` to calculate the exact binary size without searching for collisions or writing output. It defaults to a 64 MiB output cap and one million hash attempts per instruction. The `--max-bytes` and `--limit` options adjust these caps; zero disables the respective cap. `--progress` controls hash-search progress reports (zero disables reports).

The interpreter requires `--dev` to accept non-official profiles. Its own `--limit` option limits executed instructions, not collision searches. `--check` validates without executing.

## Computational model

Futility uses a doubly infinite tape of signed, arbitrary-precision integers. All cells and both pointers initially equal zero. Unallocated cells implicitly contain zero. There is no arithmetic overflow in the abstract machine.

Let `p` be the data pointer, and `L`, `C`, `R` be the original values of cells `p-1`, `p`, `p+1`. All simultaneous writes use the values before the instruction executes.

| Opcode | Mnemonic | Effect |
| --- | --- | --- |
| `00` | `+` | Increment C; double L and R. |
| `01` | `-` | Decrement C; double L and R. |
| `02` | `>` | Move the data pointer right. |
| `03` | `<` | Move the data pointer left. |
| `04` | `~` | Negate C; swap L and R. |
| `05` | `[` | Skip to after matching `]` if the prime-square condition is false. |
| `06` | `]` | Jump to after matching `[` if the condition is true. |
| `07` | `?k` | Jump to decoded instruction index k if the condition is true. |
| `08` | `.` | Output `(L ^ C ^ R) % 256` as one byte. |
| `09` | `,` | Read a byte into C (or -1 at EOF); negate L and R. |

Whitespace is ignored in decoded assembly; other characters are rejected. Brackets must be balanced. Jump targets are zero-based; the index equal to the instruction count halts execution. Falling off the end also halts. Bitwise XOR on signed integers uses Python's infinite two's-complement semantics.

### The prime-square condition

Let `n = max(0, M[p-1])`, and let `q(j)` be the j-th prime, starting with 2. Compute

$$S(p)=\sum_{j=1}^{n} M_{p+q(j)}.$$

The condition is true exactly when S is a non-negative perfect square. Zero is a square, and an empty sum is zero. The condition is evaluated at the current data pointer every time it is used.

For example, with `M[p-1] = 3`, the machine examines the cells at offsets 2, 3 and 5. If their values are 4, 7 and 2, the sum is 13, so the condition is false.

Note that `+-` restores the current cell but quadruples its neighbours. This is intentional.

### Turing completeness

The abstract language can simulate a two-counter Minsky machine. Encode each non-negative counter c as -c at an address x, and initialise a permanent selector of 1 at x-3. Keep all other nearby cells zero. For example, use counter addresses 3 and 11, with selectors at 0 and 8.

- Increment c by executing `-` at x; decrement a positive c using `+`.
- Test c for zero using `?k` at x-2. The selector makes n=1, so the tested sum is -c, which is a perfect square exactly when c=0.
- Unconditional branches are possible at a position with a zero left neighbour (for example, at the counter cell itself).

The arithmetic side effects touch only zero buffer cells; pointer movement and branches preserve the counters and selectors. Finite sequences of pointer movements and jumps therefore implement counter-machine transitions, including halting.

Every such finite instruction sequence admits an official source encoding: each collision exists by the pigeonhole principle, and every instruction block has finite length. Consequently the abstract encoded language is Turing complete, irrespective of the physical resources required by its implementation. This argument assumes unbounded resources and is not a claim that arbitrary programs are feasible to run.

## Binary source format (v1)

The file starts with `46 55 54 01` (`FUT` followed by version 1), then three canonical unsigned LEB128 integers: collision bits, base exponent and growth. Official files use `(512, 60, 1)`.

Each instruction block contains, in order:

| Field | Encoding |
| --- | --- |
| Opcode | One byte |
| Operand | Canonical unsigned LEB128, only for `?` |
| Nonce A | 65 bytes, big-endian, value below 2^513 |
| Nonce B | 65 bytes, big-endian, value below 2^513 |
| Payload | Chained SHA-512 bytes filling the block |

For zero-based instruction index i and header size h (including nonces), the official block size is

$$L(i)=\max(2^{60+i},h).$$

More generally, a profile `(bits, base, growth)` specifies a minimum block length of `2**(base + growth*i)`. When headers fit, an official N-instruction program requires `2**60 * (2**N - 1)` block bytes, plus the file header.

### Collision certificates

Each instruction must supply two distinct nonces A and B whose hashes agree on the required number of leading bits. In official mode, the entire 512-bit digests must match.

The context is the concatenation of the following byte strings:

```text
FUTILITY\x00
previous_digest       (64 bytes; initially all zero)
index                 (ASCII decimal)
\x00
mnemonic              (ASCII, including decimal operand for ?)
\x00
collision_bits        (2 bytes, big-endian)
```

The hash input is the context followed by the 65-byte nonce. There are 2^513 possible nonces but only 2^512 full digests, so a collision is guaranteed to exist in every context. Generic classical search takes order 2^256 queries under ideal-hash assumptions; generic quantum collision search takes order 2^(512/3) queries in an idealised query model. Neither is a proven computational lower bound for SHA-512 itself.

The full digest of nonce A becomes the next instruction's previous digest, including in development mode. Changing an instruction generally invalidates the rest of the chain.

### Payload

Starting with the full digest of nonce A, repeatedly apply SHA-512 and concatenate the resulting digests, truncating the last digest to fill the block exactly. Ordinary compression or sparse zero-filled files do not remove the requirement for these bytes in the raw source format. A compact algorithmic representation remains possible in principle and is not itself valid raw source.

The decoder validates the entire source, including every payload byte, before execution. It regenerates the payload rather than trusting it. The hash chain introduces sequential dependencies in the straightforward generation algorithm; its resistance to shortcuts is an assumption, not a theorem.

Blocks continue until EOF. There is currently no whole-program length or authentication field, so truncation at a block boundary can leave a valid shorter program.

## Repository structure

```text
Futility/
  README.md
  futility.py     # Decoded virtual machine
  hashing.py      # Context construction and certificate verification
  search.py       # Collision search
  validate.py     # Standalone certificate validation
  binary.py       # Binary format and payload handling
  compiler.py     # Assembly-to-binary compiler
  run.py          # Binary validation and execution
  hello.asm       # Hello World, decoded assembly
  hello.fut       # Hello World, development binary
```

To experiment with the collision mechanism independently:

```sh
python search.py '+' --bits 16 > cert.json
python validate.py cert.json --bits 16
```

## Frequently asked questions

**Is Futility actually Turing complete?**  
Yes, in the abstract model with unbounded resources. The counter-machine construction above explains why.

**Is Futility useful?**  
No.

**Can a quantum computer compile it?**  
In principle. Even instantaneous collision generation would leave the exponentially expanding payloads to contend with. Quantum computing support has been added. Performance improvements are negligible.

**Why not optimise the compiler?**  
The implementation can be optimised, and shorter decoded programs can reduce source size dramatically. Neither changes the official per-instruction certificate and payload requirements. The supplied Hello World is not claimed to be optimal.

**Why does my compiler report PHYSICAL_LIMITATION?**  
Your machine, and probably your universe, does not meet the system requirements.

**When will official Hello World be available?**  
No release date has been established.

## Status and contributing

The development compiler, decoder and virtual machine are decently functional. Official collision generation and official-scale payload construction have not been experimentally demonstrated. The current dictionary-based collision search is memory intensive. The Python implementation remains subject to finite host resources.

Contributions to the implementation, specification, mathematical proofs and decoded examples are welcome. Please do not submit full official binaries as pull requests as there isn't enough room on GitHub servers to serve them.

Known issue: insufficient universe. Planned fix: none.

**Craw Systems**
