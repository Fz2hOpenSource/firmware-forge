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
- **A test that only validates mocks is invalid.** If removing the mock's
  canned answers makes the test meaningless, restructure the test.

## Seams in C/C++

A seam is a place where behavior can change without editing source.

### Linker seam (`--wrap=symbol`)
GCC resolves references to `symbol` as `__wrap_symbol`; `__real_symbol`
reaches the original. Strongest pure-C tool; no source edits.
Pitfall: only works across translation units — same-file calls never reach
the linker.

### Function-pointer seam
HAL calls go through stored pointers; tests repoint them at runtime.
Portable to every compiler (MSVC/IAR included). Cost: indirection in
production code and weaker readability.

### Weak-symbol seam
Production defines `__attribute__((weak))` implementations; strong test
definitions override them. Solves same-file replacement. Pitfall: symbol
resolution confusion in large trees; not supported by every toolchain.

### Object seam (C++)
Pure-virtual interface injected by constructor/setter; native GMock support.
Cleanest architecture; C++ only, small vtable cost.

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
