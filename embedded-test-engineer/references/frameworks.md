# Framework and Toolchain Selection

Stay neutral; select by existing build system > team language > dependency
weight.

## Pure C

| Tool | Mechanism | Mental model | Watch out |
|---|---|---|---|
| **Unity** | Two headers + one source; rich MCU-friendly assertions (`TEST_ASSERT_EQUAL_HEX32`...) | Plain xUnit | No mocking by itself; small runner to write (or generate) |
| **Ceedling + CMock** | Ruby parses headers, auto-generates mocks + runners + gcov | Expectation-driven: declare expected calls first | Ruby dependency; generated file sprawl confuses IDE indexing |
| **FFF** | Single `fff.h`; macros expand to fake functions with call history (`call_count`, `arg_history`) | Assertion-driven: run, then inspect history; `SET_RETURN_SEQ` for retry paths; `custom_fake` delegates to a real function | Manual macro per function; large HAL APIs get verbose |

Reuse the existing runner first. A few pure-C cases may need only assertions
and small stubs; FFF helps when call history or return sequences are useful.
CMock earns code generation when a justified boundary has many interaction checks;
a large HAL does not imply that it should be mocked wholesale.

## C++

- **CppUTest**: embedded-minded xUnit with memory-leak detection across
  setup/teardown — valuable for long-running stacks; wraps C sources via
  `extern "C"`.
- **GoogleTest/GoogleMock**: industrial standard; parameterized tests,
  filtering. For C dependencies use an appropriate seam; FFF is one option.
  Ensure each test target links exactly one intended definition of each replaced
  symbol; separate targets only when their dependency sets conflict.

## Python (host-side analyzer, not a firmware test framework)

Existing Python tooling, optionally pytest + numpy/scipy, can drive replay analysis: parse recorded
binary streams, compute accuracy/noise/drift metrics, assert tolerance
tables, render comparison reports. Use only dependencies the analysis needs; see `data-replay.md`.

## MDK + CMake Dual Build

Production compiles with Keil MDK; host tests compile a pure-logic subset
with GCC/Clang via CMake:

- Compile the same production logic sources, with explicit host dependencies.
  Verify the host subset against the MDK project and relevant defines/options.
  Use a shared manifest/generator only if both build paths support it and drift
  warrants the extra machinery; an MDK project cannot simply include any CMake list.
- Link only the necessary test doubles in the host target.
- Do not require `-m32` just to mimic pointer width. Native 64-bit tests are useful,
  but fixed-width types do not eliminate ABI, alignment, promotion or FPU differences.
  Retain target cross-build and layout/numeric checks where those matter.
