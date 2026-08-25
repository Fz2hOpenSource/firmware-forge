# STM32 F7

## Family Notes

- Cortex-M7 cache behavior applies on many F7 parts.
- Memory placement and alignment matter more than on F4/L4.
- DMA, Ethernet, LCD, and camera paths need explicit buffer ownership.

## Practical Guidance

- Use aligned buffers and cache maintenance helpers for DMA paths.
- Prefer explicit memory sections for DMA-heavy data.
- Verify priority grouping and interrupt priorities early, especially with FreeRTOS.
- Separate display/network bulk transfers from high-priority acquisition work.

## Verification Points

- Test with D-cache enabled.
- Check map-file placement for DMA buffers.
- Measure ISR interval and task wake latency at the highest supported rate.
