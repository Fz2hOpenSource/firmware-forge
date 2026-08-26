# Persistent Storage and Settings

Read this reference for external SPI/QSPI flash, persisted settings or calibration, retry behavior, concurrent access, and power-loss recovery.

## Ownership and Scheduling

- Give each storage bus and device one transaction owner. Serialize command, address, data, and completion polling as one logical transaction.
- Never call erase/program, blocking status polling, filesystem work, or record validation from an ISR.
- Bound lock acquisition, HAL operations, device-busy waits, and recovery. Record which stage failed and the underlying driver status.
- Do not insert RTOS yielding into an existing blocking flash driver merely to improve responsiveness. First prove the device state machine, chip-select lifetime, bus ownership, timeout basis, and callers remain correct across preemption.

## Record Integrity and Power Loss

- Prefer versioned records with length, object identity, revision/sequence, payload CRC, and header/commit integrity.
- Use A/B slots, append-only records, or another atomic commit scheme so interruption cannot destroy the last known-good value.
- Write payload and provisional metadata before the final commit marker. On startup, scan and select only fully committed valid records.
- Define sequence wrap and tie-breaking explicitly. Do not choose a record only because one raw unsigned sequence value is numerically larger.
- Verify readback when the product risk warrants it; keep retry/readback failure distinct from successful persistence.

## Retry and Recovery

- Retry only failures believed transient, with a small bounded attempt count. CRC corruption, invalid schema, and incompatible version require explicit handling rather than endless rereads.
- Track retry attempts, retry successes, final failures, CRC categories, last object, operation, stage, HAL status, timeout, and bus recovery result.
- A recovery routine must restore peripheral/bus state before retrying and must not reset unrelated users silently.

## Persistence Semantics

- Define which values survive transport disconnect, stream stop/start, profile change, software reset, and power cycle.
- Persist only product settings that must survive power loss; avoid writing transient run state, live counters, or rapidly changing values.
- Use idempotent request identifiers or expected revisions when repeated control messages could otherwise duplicate a create/update operation.
- Separate stored schema version from runtime context revision and migrate or reject old records deterministically.

## Verification

- Test erase/program/read, 1→0 programming rules, page/sector boundaries, full storage, retries, CRC corruption, interrupted program, interrupted metadata commit, restart scan, sequence wrap, and schema migration.
- Stress storage concurrently with maximum-rate acquisition and network/control traffic. Verify bounded latency, no bus ownership conflicts, and no acquisition deadlock.
- Build success is insufficient: use a host/mock fault matrix plus target tests for real HAL timeout and recovery behavior.
