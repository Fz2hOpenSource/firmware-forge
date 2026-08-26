# STM32 H7

## Family Notes

- D-cache, memory domains, and DMA access rules are critical.
- Verify the exact H7 subfamily and reference manual. DMA accessibility differs by memory region and DMA engine.
- Many DMA engines cannot use every RAM region. Do not assume DTCM, AXI SRAM, SRAM1/2/3/4, and external RAM are equivalent.
- Ethernet MAC DMA needs descriptors and buffers in DMA-accessible memory with cache coherency handled explicitly.

## Practical Guidance

- Treat linker placement, MPU attributes, and DMA routing as part of the driver design.
- Put high-rate DMA buffers and Ethernet descriptors in named sections when placement matters.
- Use 32-byte alignment for cacheable DMA buffers and descriptors.
- For RX DMA buffers, ensure target cache lines are not dirty before starting DMA.
  Use non-cacheable MPU regions, dedicated aligned RX buffers, or explicit cache
  maintenance before arming DMA. After hardware writes, invalidate before CPU parsing.
- Do not share a cache line between DMA-owned data and unrelated CPU-owned data.
- On STM32H7, also verify the selected DMA engine can access the chosen RAM
  region; DTCM and AXI/SRAM domains are not interchangeable.
- For TX DMA buffers, clean before hardware reads.
- For LwIP, respect pbuf lifetime. Do not free or reuse a TX buffer until the stack/driver is done with it.
- Keep LwIP/socket work in a network task; acquisition ISR/task should push complete frames into a ring or queue.
- Add counters for DMA errors, cache-related packet/sample validation failures, RX/TX drops, and ring overflow.
- Treat external SPI flash and other long peripheral transactions as scheduled shared resources: define transaction ownership, timeout/recovery, and whether busy polling may block acquisition or networking. Do not add RTOS yielding inside an established blocking driver without validating its state machine and chip timing.
- Publish multiword measurement snapshots atomically, for example with a sequence guard or slot handoff. `volatile` does not make a concurrently updated struct coherent.

## Verification Points

- Confirm MPU/cache attributes at runtime or from startup/linker files.
- Confirm descriptors and buffers are in the expected memory section from the map file.
- Run tests with D-cache enabled before trusting timing or data integrity.
- Stress network upload while measuring acquisition interval min/max and dropped frames.
- Verify externally visible snapshots never mix fields from different generations under concurrent ISR/task updates.
