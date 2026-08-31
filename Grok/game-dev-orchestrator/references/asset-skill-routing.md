# Asset Skill Routing

Read before spawning `[asset-artist]`. Instruct the worker to **read and follow** these skills; do not paste their bodies into the prompt.

Always load `game-asset-core`. Add the specialist for the Asset Manifest `kind`:

| kind | Specialist |
|------|------------|
| `style-lock`, `sprite`, `vfx` (still) | `game-asset-core` only (plus `imagine` when calling image tools) |
| `character` | `game-character-consistency` |
| `animation` | `game-animation-frames` |
| `tileset` | `game-tilesets` |
| `ui`, `icon` | `game-ui-icons` |

If one asset is a character *and* it animates, load **both** `game-character-consistency` and `game-animation-frames`.

Style-lock is a dependency of every character/tile/UI set. Do not spawn those artists until the lock file exists (unless architecture marked the milestone greybox-only).

Shared sheets/atlases are `shared` — one writer at a time.

Audio is not covered by these skills. Stub + flag unless architecture named a generator and format.
