# Runtime And Scenes

## Loop And Time
Tick/delta, fixed step if any, pause, hitstop, time scale. Who owns the clock.

## Scene Map
| Scene / level | Purpose | Owner module | Entry / exit |
|---|---|---|---|
| Boot | | | |
| Title | | | |
| Play | | | |
| Results | | | |

## Autoloads / Singletons
| Name | Owns | Must not own |
|---|---|---|
| | | |

## Camera
Projection, follow rules, shake/zoom ownership, what it must not lie about (alignment, scale).

## Entity Model
How a playable thing is represented (node + script, entity + components, …). Spawning and pooling if relevant.

## Pause, Focus, Interrupt
App backgrounding, overlay menus, "pause on interrupt" if the GDD requires it.
