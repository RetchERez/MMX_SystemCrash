# Mega Man X: CHAIN REACTION v1.0 — build and test

Design: https://claude.ai/artifact/Wt3DrUfUaev21QCyKZwdYX (v1.0 master design, three loops).

## Requirements (all local, nothing downloaded at build time)

- Python 3.11+ with Pillow
- `tools/vendor/asar191/asar.exe` (Asar 1.91), `tools/vendor/flips-windows/flips.exe` (Flips v198)
- `tools/vendor/snes9x/snes9x_libretro.dll` (libretro nightly, sha256 in `provenance.json`) for tests
- second emulator: `tools/vendor/bsnes_mercury/bsnes_mercury_balanced_libretro.dll`
  (sha256 9b790e5045a8807e8f6f36600015ce5fa1268c5f1267574144b6e8a3135365b0)
- Your own ROM at `rom_private/Mega Man X (USA) (Rev 1).sfc`
  (unheadered, 1,572,864 bytes, CRC32 DED53C64; a 512-byte copier header is stripped automatically)

## Build and release

Several tests read `audit_output/events.csv`, which is extracted from your ROM and therefore not in the repository:

```
python tools/audit_rom.py "rom_private/Mega Man X (USA) (Rev 1).sfc"   # writes audit_output/
```

```
python tools/build.py --name chain_reaction_test     # build + BPS + roundtrip
python tools/release.py                              # rebuild v1.0 and package both ZIPs
```

`tools/build.py` refuses any other source ROM, then:

1. generates derived data from your ROM into `build/gen/` (palettes, map/collision copies,
   blockMap retarget lists, half-power lists from the retail event stream)
2. pads a copy to 2 MiB (deliberate LoROM expansion) and assembles `src/main.asm` with Asar;
   every hook asserts its original Rev 1 bytes, every code block asserts it does not overlap the next
3. fixes the header checksum and prints every changed byte range
4. creates the BPS and re-applies it to the verified source as a byte-for-byte roundtrip check

## Tests (headless snes9x)

`bash tests/run_all.sh build/<rom>.sfc` runs everything below (logs in `build/qa/`, matrix in `build/matrix/`).

| Script | What it proves |
| --- | --- |
| `tests/matrix.py` | 256 boss masks x 8 stages, patched vs vanilla: a stage changes only when its one source bit is set (Armadillo uses a 600-frame probe) |
| `tests/test_parity.py` | With the source boss alive, WRAM is identical to vanilla during play in all five target stages |
| `tests/test_persist.py` | Altered state at every checkpoint and after a real death and respawn |
| `tests/test_sigma.py` | Fortress icon selected for real (Sigma 1); Sigma 1-4 with every boss beaten: WRAM identical to vanilla over 2,400 frames |
| `tests/test_grid_down*.py` | Kuwanger palette; 3 of 5 sensors live; far beams still arm the traps; Turn Cannon dead only in Grid Down |
| `tests/test_radar_down_turrets.py`, `_claws.py` | One deck turret silent; listed Sky Claws hang dead, the rest work |
| `tests/test_empty_arsenal.py` | Silos render empty from runtime data; Mega Tortoise bombs halved |
| `tests/test_ambush.py` | Listed Batton Bone roosts never wake; listed Metal Wings decline; others unchanged |
| `tests/test_meltdown.py` | Igloos melt at spawn (no Tombot nest), Heart Tank exposed, no snowballs, Penguin's bats unaffected |
| `tests/test_boss_arenas.py` | All five changed stages' boss fights: palette and actors as retail (Kuwanger's room restores its lights at the boss) |
| `tests/test_items.py` | Every Heart Tank and Sub Tank collected and every capsule spawns, in both states of all eight stages |
| `tests/test_hadouken.py` | The Hadouken is awarded by the retail capsule (only reachable with every Maverick beaten, so in Ambush Called Off) |
| `tests/test_collision.py` | Map retargets leave collision identical in every reachable cell, every checkpoint |
| `tests/test_sweep.py` | Every real Batton Bone, Metal Wing, Sky Claw and Turn Cannon placement: exactly the listed ones dead |
| `tests/test_traverse.py` | Controller-only runs from every checkpoint, normal vs altered (no new hazards, no softlocks) |
| `tests/test_radar_lights.py` | Radar Down: the platform light animator (effect $33 sub $09) is refused before Death Rogumer and the lights sit at the unlit value; the ship's lights run as retail |
| `tests/test_minecart.py` | A real minecart ride: listed Metal Wings never come in Ambush; the rest attack as in vanilla; normal ride identical to vanilla |
| `tests/test_ending.py` | Every Maverick beaten, fortress to the ending, vanilla vs patch: Velguarder and Sigma beaten by X's own shots, Wolf Sigma's final shot replaced by the game's lethal-hit writes; all of WRAM compared every 300 frames through the credits |
| `tests/mesen_check.py` | Third emulator, Mesen 2 (`tools/vendor/mesen2`, portable `settings.json`: pad in port 1, Lua file IO, zeroed RAM): every stage normal and altered via real password and stage select |
| `tests/run_bsnes.sh` | The reaction suite, items, Hadouken, boss arenas, Sigma and parity again on bsnes-mercury (`CR_CORE`) |

Test-only RAM pokes (camera borders, HP refill, test spawns, the stage number for Sigma) are marked
in the scripts and never ship.

## Source layout

- `src/main.asm` — free-space assertions, includes
- `src/core.asm` — `CR_Altered` predicate (Sigma firewall), palette-bank hook `$80:B512`,
  post-load hook `$80:BB0F` (map/collision pointers, blockMap retarget), half-power list checks
- `src/grid_down.asm`, `radar_down.asm`, `empty_arsenal.asm`, `ambush.asm`, `meltdown.asm`
- `tools/` — build, release, disassembler, password codec, stage renderer, harness, survey
- `docs/actor_findings.md` — actor research used by the hooks

No ROM bytes, renders or save states are kept in source; `build/`, `rom_private/` and vendor tools are excluded.
