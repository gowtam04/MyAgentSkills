# Systems And Interfaces

Map GDD systems to code modules. Do not restate GDD rules here — link `gdd_refs` and define contracts.

## Module Map
| Module | GDD system | In slice? | Path | Depends on |
|---|---|---|---|---|
| | | | | |

## Module: {Name}
- **gdd_refs:**
- **Owns:**
- **Exposes:** (signals, functions, types)
- **Depends on:**
- **Does not own:**

### Contract
Signatures, event payloads, error/invalid cases. High detail at multi-worker seams.

(Repeat per in-slice module. Out-of-slice: one-line deferral only.)

## Shared Kernel
Input, time, audio bus, RNG, debug overlay — each with a single owner file.
