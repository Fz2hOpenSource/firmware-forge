# Framework and Toolchain Selection

Stay neutral; select by existing build system > team language > dependency
weight.

## Pure C

| Tool | Mechanism | Mental model | Watch out |
|---|---|---|---|
| **Unity** | Two headers + one source; rich MCU-friendly assertions (`TEST_ASSERT_EQUAL_HEX32`...) | Plain xUnit | No mocking by itself; small runner to write (or generate) |
| **Ceedling + CMock** | Ruby parses headers, auto-generates mocks + runners + gcov | Expectation-driven: declare expected calls first | Ruby dependency; generated file sprawl confuses IDE indexing |
| **FFF** | Single `fff.h`; macros expand to fake functions with call history (`call_count`, `arg_history`) | Assertion-driven: run, then inspect history; `SET_RETURN_SEQ` for retry paths; `custom_fake` delegates to a real function | Manual macro per function; large HAL APIs get verbose |

Selection: project already on Ceedling → stay there. Pure C with no Ruby and
a CMake build → FFF. Huge HAL surface to mock wholesale → CMock earns its
codegen.

## C++

- **CppUTest**: embedded-minded xUnit with memory-leak detection across
  setup/teardown — valuable for long-running stacks; wraps C sources via
  `extern "C"`.
- **GoogleTest/GoogleMock**: industrial standard; parameterized tests,
  filtering. Mixed C caveats: free functions need wrappers; combining FFF
  inside GTest fixtures is the standard cure for mocking C dependencies.
  One mega-binary linking real C symbols and FFF fakes causes symbol
  collisions — split into micro-builds.

## Python (host-side analyzer, not a firmware test framework)

pytest + numpy/scipy drive measurement replay analysis: parse recorded
binary streams, compute accuracy/noise/drift metrics, assert tolerance
tables, render comparison reports. This is the natural engine behind
`data-replay.md`.

## MDK + CMake Dual Build

Production compiles with Keil MDK; host tests compile a pure-logic subset
with GCC/Clang via CMake:

- Keep one shared source-list file included by both build systems.
- The CMake test tree links fakes/mocks; production sources stay unmodified.
- Do not require `-m32` on Windows hosts (32-bit toolchain/runtime pain);
  fixed-width integer discipline (see `host-setup.md`) makes 64-bit host
  builds safe. Linux native_sim users may optionally use ILP32.
