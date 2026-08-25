# STM32 F4

## Family Notes

- Strong fit for Cortex-M4-style driver and DSP work.
- Typical F4 parts do not have D-cache coherency problems.
- FPU availability depends on the exact part and compiler settings.
- CubeMX + HAL/LL is a common baseline, but generated code should stay separate from reusable drivers.

## Practical Guidance

- Use CMSIS-DSP or `float` on F4F when measured CPU load is acceptable.
- Avoid `double` for high-rate pipelines unless there is a measured need.
- Use DMA for continuous ADC/SPI/UART streams when it reduces jitter.
- Keep board pin glue in BSP-style code and protocol logic in driver code.
- Use TIM or DWT-based microsecond timestamps when validating DRDY/sample timing.

## Verification Points

- Confirm actual SPI/ADC/timer clocks after Cube configuration.
- Measure DRDY interval min/max instead of relying only on configured rates.
- Check stack use for filter and packet buffers.
