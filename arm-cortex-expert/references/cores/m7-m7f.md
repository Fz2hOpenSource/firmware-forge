# M7 and M7F

## Key Constraints

- Data cache and instruction cache are common and must be considered in DMA designs.
- DMA buffers must be in memory accessible by the selected DMA engine.
- Cache maintenance address ranges must cover complete cache lines.
- Memory ordering around MMIO and DMA setup matters.

## Recommended Patterns

- Align DMA buffers and descriptors to the cache line size, commonly 32 bytes.
- Round cache-maintenance start/end addresses to cache-line boundaries.
- For peripheral-to-memory RX DMA using cacheable memory, ensure target cache
  lines are not dirty before starting DMA. Use non-cacheable MPU regions,
  dedicated aligned RX buffers, or explicit cache maintenance before arming DMA.
- After RX DMA completes, invalidate the completed buffer range before CPU reads it.
- Do not share a cache line between DMA-owned data and unrelated CPU-owned data.
- For memory-to-peripheral DMA: clean before enabling DMA or handing the buffer to hardware.
- Use `__DMB()` or `__DSB()` around register sequences and cache maintenance when ordering is required.
- Consider MPU non-cacheable regions for Ethernet descriptors or high-churn DMA buffers.
- Keep DMA completion callbacks short and hand completed buffers to tasks through queues/rings.

## Common Risks

- Stale samples or packets from missing invalidate/clean.
- DMA buffers placed in memory not visible to the DMA engine.
- Cache maintenance on unaligned address ranges that misses part of a buffer.
- Timing bugs hidden by debug prints, breakpoints, or disabled caches.
- Calling RTOS APIs from interrupts with invalid priority.
