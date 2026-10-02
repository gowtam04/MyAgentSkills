# Tower Drop — Systems

## Drop
Status: locked.
- The crane swings horizontally with period `swing_period_s` (level data, default 2.0 s).
- A tap releases the block; it falls straight down and lands on the top of the tower.
- Overlap = the horizontal intersection of the falling block and the top block. The overhang is
  trimmed; the new top block has the overlap's width.
- If the overlap is under 4 px, the drop is a miss: no block is added and the player loses a life.
- A drop within 3 px of perfect alignment is a **perfect drop**: the block keeps its full width.

## Scoring
Status: locked.
- Each landed block scores 10 points.
- Each consecutive perfect drop adds a combo bonus of 5 × combo length (the first perfect drop
  scores +5, the second +10, …). Any non-perfect drop resets the combo.

## Lives
Status: locked.
- The player starts with 3 lives. A miss costs one. At 0 lives the run ends and the results
  screen shows the final score and a Retry button.

## Levels
Status: prototyped.
- A level sets `swing_period_s`, `block_width_px` and `target_height` (blocks to clear it).
- Clearing a level loads the next one; after the last level the run ends in a win.
