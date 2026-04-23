# Physical key layout

Hardware reference for this specific Lily58 build. The ZMK keymap
(`config/lily58.keymap`) has **58 binding slots** because that is what
the Lily58 matrix definition allocates — but this particular build
only has **54 physical switches**. The remaining four slots correspond
to positions where no switch is soldered; they are marked `&none` on
every layer.

## Per-half counts

```
Main cluster:   6 cols × 4 rows = 24 keys
Thumb cluster:  3 keys  (not 4 — innermost slot is empty)
Total per half: 27 keys
Total board:    54 keys
```

## Missing positions in the keymap

These four slots have no physical switch behind them. Anything bound
there is ignored by the firmware. Keep them as `&none` on every layer
so the convention stays legible.

| Keymap row    | Slot index (0-based) | Meaning                         |
| ------------- | -------------------- | ------------------------------- |
| Row 3         | 42                   | Left inner (between `B` and center) — no switch  |
| Row 3         | 43                   | Right inner (between center and `N`) — no switch |
| Thumb row     | 53                   | Left innermost thumb — no switch                 |
| Thumb row     | 54                   | Right innermost thumb — no switch                |

(Slot indexing: row 0 = 0–11, row 1 = 12–23, row 2 = 24–35,
row 3 = 36–49, thumb = 50–57. Positions are assigned in the order
they appear in the `bindings = <...>` array, left-to-right,
top-to-bottom, including the `&none` gaps.)

## Physical key position map

Positions with a `—` are non-existent. Numbers shown are the linear
keymap indexes, usable as combo `key-positions`.

```
 0  1  2  3  4  5                       6  7  8  9 10 11
12 13 14 15 16 17                      18 19 20 21 22 23
24 25 26 27 28 29                      30 31 32 33 34 35
36 37 38 39 40 41  (—)            (—)  44 45 46 47 48 49
                 50 51 52  (—)    (—) 55 56 57
```

## Implications for keymap edits

1. **Never bind a keycode to an empty slot** (42, 43, 53, 54). It
   won't do anything — the firmware never generates events for those
   matrix positions.
2. **When more base-layer keys are needed**, use ZMK combos or
   mod-taps on existing physical keys. Typical candidates:
   - `LBKT` (`[` → `х` in UA/RU) — combo on `Z+X` (37, 38) is a
     good fit: same hand, adjacent, rarely typed together in
     English or Cyrillic.
   - `RBKT` (`]` → `ъ` in RU / `ї` in UA) — combo on `. + /`
     (47, 48) mirrors it on the right hand.
3. **Convention**: `&none` marks non-existent hardware; `&trans`
   marks "fall through to the layer below." Do not use `&none` for
   a physical-but-unbound key — that muddles the signal and causes
   exactly the misreading that prompted this doc.

## Verifying this in the future

If a build is ever rewired or keys added:

- Inspect the PCB visually for all soldered switches.
- Or in ZMK Studio, press every key and confirm which positions
  register.
- Update this file and the matching memory entry in
  `~/.claude/projects/.../memory/project_lily58_physical_keys.md`.
