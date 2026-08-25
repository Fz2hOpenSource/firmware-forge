# M4 and M4F

## Key Constraints

- Cortex-M4 may or may not include an FPU. Confirm the exact part and compiler FPU ABI.
- Typical STM32F4-class parts do not have D-cache coherency issues like M7-class parts.
- CMSIS-DSP is often useful for filters, statistics, FFTs, and vector math.
- ISR latency and stack size are still important for high-rate sampling.

## Recommended Patterns

- Use DMA for ADC, SPI, I2S, UART, or timer capture paths when it reduces jitter or CPU load.
- Use `float` on M4F when existing code uses it and measured CPU load is safe.
- Use `q15_t`, `q31_t`, or integer paths when the part lacks FPU, the wire format is fixed-point, or deterministic CPU budget matters.
- Keep filter, decimation, packetization, and hardware driver stages separate.
- Use timer or DWT-based timestamps when validating sample timing.

## Common Risks

- Accidentally compiling for soft-float or using `double` on a single-precision FPU target.
- Doing too much work in DRDY/DMA callbacks.
- Allocating large buffers on task stacks.
- Changing sample rate without resetting or reconfiguring filters and decimators.
