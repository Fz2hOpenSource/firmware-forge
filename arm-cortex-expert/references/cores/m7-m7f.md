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
- Use barriers for their specific architectural purpose; do not treat them as interchangeable or as cache-maintenance operations:
  - `__DMB()` orders explicit memory accesses before and after the barrier but does not require every earlier access to have completed. Use it when publishing ownership/data to another observer after the data writes are complete.
  - `__DSB()` waits for prior explicit memory accesses to complete before subsequent execution. Use it where the architecture or vendor sequence requires completion before enabling hardware, changing memory-system state, sleeping, or continuing after cache/MPU maintenance.
  - `__ISB()` flushes the instruction pipeline so subsequent instructions observe changed execution context. Use it after MPU/cache/control-register changes when required by the ARM or vendor sequence; it does not order DMA payload data by itself.
- Use the CMSIS cache helper that matches ownership direction: clean before a DMA/peripheral reads CPU-written cacheable memory, invalidate before the CPU consumes DMA-written memory, and clean+invalidate only when both writeback and discard are intentionally required. Align the complete start/end range to cache-line boundaries and keep unrelated objects out of those lines.
- Inspect the target project's CMSIS helper implementation before adding barriers around `SCB_CleanDCache_by_Addr`, `SCB_InvalidateDCache_by_Addr`, or related helpers; many implementations already contain required `DSB`/`ISB` operations. Add only barriers required by the ownership or register sequence, and never use `DMB`/`DSB` as a substitute for clean/invalidate.
- Consider MPU non-cacheable regions for Ethernet descriptors or high-churn DMA buffers.
- Keep DMA completion callbacks short and hand completed buffers to tasks through queues/rings.

## Common Risks

- Stale samples or packets from missing invalidate/clean.
- DMA buffers placed in memory not visible to the DMA engine.
- Cache maintenance on unaligned address ranges that misses part of a buffer.
- Timing bugs hidden by debug prints, breakpoints, or disabled caches.
- Calling RTOS APIs from interrupts with invalid priority.

Barrier meanings: [CMSIS CPU intrinsics](https://arm-software.github.io/CMSIS_6/main/Core/group__intrinsic__CPU__gr.html).
Use the actual project's CMSIS implementation and vendor sequence for placement.
