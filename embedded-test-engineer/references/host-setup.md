# Host Build Setup and Portability Traps

## What Can Run on Host

Pure logic compiles on host: algorithms, parsers, state machines,
calibration math, ring buffers behind seams. Anything touching registers
cannot — unless the access sits behind an interface seam
(`test-doubles.md`). Legacy modules that violate this are still verifiable:
start with characterization tests at their current boundary and introduce
seams incrementally rather than blocking all verification.

## Red Line: Never Map MCU Addresses on Host

```c
/* FORBIDDEN in host tests */
#define GPIOA ((GPIO_TypeDef*)0x40020000)
```

On a hosted OS that address is unmapped or protected: instant segfault.
Worse, it silently bakes ILP32 pointer assumptions into LP64/LLP64 code.
Isolate via interface seams instead; if a peripheral model is genuinely
needed, write an explicit byte-exact fake owned by the test.

## Data Model Traps (ILP32 vs LP64/LLP64)

Cortex-M is ILP32 (32-bit long, pointers); Linux/macOS hosts are LP64;
Windows x64 is LLP64. Consequences:

- Use `<stdint.h>` fixed-width types everywhere; never assume `long` is 32-bit.
- Never store pointers in `uint32_t`; use `uintptr_t` if a generic integer
  holder is unavoidable.
- Struct layout/alignment may differ; do not memcpy raw structs across the
  boundary — serialize field-by-field.
- Endianness matches (little) on typical targets, but do not rely on it.

`volatile` does not give host tests concurrency semantics; simulate
asynchronous producers explicitly (threads or staged test drivers).

Host memory is effectively infinite; buffer-exhaustion paths need explicit
tests with constrained sizes, not hope.

## CMake Minimal Approach

- One shared source-list file included by both the MDK project and the
  CMake tree; production sources stay untouched.
- The host test target links fakes/mocks; production link happens only in
  the cross build.
- Keep compiler warning levels equal or stricter than the production build;
  host GCC catches UB the MDK build silences.

## Sanity Checklist Before Trusting Host Results

- [ ] No direct register dereference anywhere in the tested subset
- [ ] Fixed-width types verified (`grep` for `long`, bare `int` in interfaces)
- [ ] Struct comparisons field-wise, not bytewise
- [ ] Any size-dependent logic tested at both 32- and 64-bit host builds when feasible
