# Persistent Storage and Settings

Read this reference for external SPI/QSPI flash, persisted settings or calibration, retry behavior, concurrent access, and power-loss recovery.

## Ownership and Scheduling

- Give each storage device a logical operation owner and each shared bus an arbitration policy. Keep command/address/data and chip-select lifetime intact. Device-busy time need not reserve the whole bus: release it between complete status polls only when the device/protocol permits, while retaining device-operation ownership and the total deadline. Bound the impact on other bus users.
- Never call erase/program, blocking status polling, filesystem work, or record validation from an ISR.
- Bound lock acquisition, HAL operations, device-busy waits, and recovery. Record which stage failed and the underlying driver status.
- Do not insert RTOS yielding into an existing blocking flash driver merely to improve responsiveness. First prove the device state machine, chip-select lifetime, bus ownership, timeout basis, and callers remain correct across preemption.

## Record Integrity and Power Loss

- Prefer versioned records with length, object identity, revision/sequence, payload CRC, and header/commit integrity.
- When requirements demand survival of interrupted writes, use A/B slots, append-only records or another justified commit scheme that preserves a valid previous record. Verify media erase/program granularity and commit-marker behavior under power loss; two logical slots in the same erased sector are not independent protection.
- Write payload and provisional metadata before the final commit marker. On startup, scan and select only fully committed valid records.
- Define sequence wrap and tie-breaking explicitly. Do not choose a record only because one raw unsigned sequence value is numerically larger.
- Verify readback when the product risk warrants it; keep retry/readback failure distinct from successful persistence.

## Retry and Recovery

- Retry only failures believed transient, with a small bounded attempt count. CRC corruption, invalid schema, and incompatible version require explicit handling rather than endless rereads.
- Track retry attempts, retry successes, final failures, CRC categories, last object, operation, stage, HAL status, timeout, and bus recovery result.
- Bus recovery does not establish whether the previous write/erase took effect. Query/read back or reconcile first when possible; replay only when the effect contract permits. A recovery routine must restore a known peripheral/bus state without silently resetting unrelated users, and stop with explicit uncertainty when verification fails.

## Persistence Semantics

- Define which values survive transport disconnect, stream stop/start, profile change, software reset, and power cycle.
- Persist only product settings that must survive power loss; avoid writing transient run state, live counters, or rapidly changing values.
- Use idempotent request identifiers or expected revisions when repeated control messages could otherwise duplicate a create/update operation.
- Separate stored schema version from runtime context revision and migrate or reject old records deterministically.

For settings that also affect live measurement, distinguish three facts:
persisted record, applied runtime configuration, and fresh valid results produced
under that configuration. For example, saving revision B may succeed while the
FPGA apply step fails: the stored record can be B while runtime remains at verified
A (or is uncertain). Report those outcomes separately under the product contract;
do not mark B active or stamp cached A results as B. After a successful apply, data
may still be warming up. A hardware rollback alone does not validate the new
logical context. Use existing status/revision mechanisms where sufficient, not a
mandatory transaction engine.

## Verification

- Test erase/program/read, 1→0 programming rules, page/sector boundaries, full storage, retries, CRC corruption, interrupted program, interrupted metadata commit, restart scan, sequence wrap, and schema migration.
- Stress storage concurrently with maximum-rate acquisition and network/control traffic. Verify bounded latency, no bus ownership conflicts, and no acquisition deadlock.
- Build success is insufficient: use a host/mock fault matrix plus target tests for real HAL timeout and recovery behavior.
