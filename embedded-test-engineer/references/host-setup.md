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

An MCU address has no valid peripheral meaning in an ordinary host process;
dereferencing it may fault or access unrelated memory. It also bakes target
address assumptions into host code.
Isolate via interface seams instead; if a peripheral model is genuinely
needed, write an explicit byte-exact fake owned by the test.

## Data Model Traps (ILP32 vs LP64/LLP64)

Cortex-M is ILP32 (32-bit long, pointers); Linux/macOS hosts are LP64;
Windows x64 is LLP64. Consequences:

- Use fixed-width types for wire/register/storage widths; use `size_t`, ordinary
+  integers or other types where their semantics fit. Never assume `long` is 32-bit.
- Never store pointers in `uint32_t`; use `uintptr_t` if a generic integer
  holder is unavoidable.
- Struct layout/alignment may differ; do not memcpy raw structs across the
  boundary — serialize field-by-field.
- Endianness matches (little) on typical targets, but do not rely on it.

`volatile` does not give host tests concurrency semantics; simulate
asynchronous producers explicitly (threads or staged test drivers).

Host memory abundance can mask device limits. Exercise fixed-capacity exhaustion
and allocation failure explicitly, including cleanup and retry behavior.

## CMake Minimal Approach

- Compile a documented subset of actual production sources. Verify it and relevant
  defines against MDK; use a shared manifest only if the existing build supports it.
- The host test target links fakes/mocks; production link happens only in
  the cross build.
- Enable relevant warnings and available sanitizers; they may expose undefined
  behavior but do not prove its absence. Also cross-build with the target options.

## Sanity Checklist Before Trusting Host Results

- [ ] No direct register dereference anywhere in the tested subset
- [ ] Interface width, signedness, promotions and overflow assumptions checked
- [ ] Struct comparisons field-wise, not bytewise
- [ ] Any size-dependent logic tested at both 32- and 64-bit host builds when feasible
