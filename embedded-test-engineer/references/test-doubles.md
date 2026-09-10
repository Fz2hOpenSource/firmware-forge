# Seams and Test Doubles

## Test Double Selection

| Double | Use when | Embedded example |
|---|---|---|
| **Stub** | Only an input value or state trigger is needed | ADC read stub returning a below-threshold value to trip low-battery cutoff |
| **Fake** | A simplified working model suffices | RAM-array Flash driver so a filesystem can mount/read/write on host |
| **Mock** | Call order, count, or argument details matter | I2C sensor init sequence: enable-before-configure ordering asserted |

Hard rules:

- Do not mock everything. Prefer real implementations when behavior is
  simple or integration is cheap.
- Delete mocks whose maintenance cost exceeds their protective value.
- A test needs an observable outcome from the code under test that can fail when
  it is wrong. Depending on canned stub inputs is normal; asserting only the
  double's own behavior does not validate the production logic.

## Seams in C/C++

A seam is a place where behavior can change without editing source.

### Linker seam (`--wrap=symbol`)
GNU ld rewrites undefined references to `symbol` as `__wrap_symbol`, and
`__real_symbol` to the original. Calls resolved inside a translation unit are not
wrapped. Confirm the linker supports this option and that the optimized test
binary actually calls the replacement. See [GNU ld --wrap](https://sourceware.org/binutils/docs/ld/Options.html#index-_002d_002dwrap_003dsymbol).

### Function-pointer seam
HAL calls go through stored pointers; tests repoint them at runtime.
Portable to every compiler (MSVC/IAR included). Cost: indirection in
production code and weaker readability.

### Weak-symbol seam
A supported weak external definition can be overridden by a strong test definition.
Do not assume this replaces every same-file call: static linkage, inlining, LTO,
archive selection and compiler/linker rules matter. Verify the final symbol/call
path with the real build options; use an explicit seam when resolution is uncertain.

### Object seam (C++)
Pure-virtual interface injected by constructor/setter; native GMock support.
Useful when the project already benefits from an injected C++ interface; it is not
+a reason to migrate a small C module or add virtual dispatch solely for testing.

## Anti-Patterns

- **Mock chains**: mock calling mock until test logic exceeds business
  logic complexity. Redesign the boundary instead.
- **Testing the mock**: assertions live inside double logic, disconnected
  from the code under test.
- **Brittle assertions**: dead-verification of irrelevant arguments so any
  harmless refactor collapses the suite. Assert observable outcomes and
  safety-relevant ordering only.
- **Coverage theater**: mocked-to-death modules at 100% coverage whose
  integration fails immediately on hardware.

## Real-Over-Mock Heuristics

Choose the real implementation when:

- The dependency is deterministic and fast (pure math, ring buffers).
- A fake would need to reimplement most of the real behavior.
- Mock maintenance after refactors costs more than running the real thing
  on target occasionally.
