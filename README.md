# Mega Man X: System Crash

A Mega Man X (SNES) ROM hack where every Maverick you beat changes another Maverick's stage.

In the original game, beating some Mavericks changes other stages: beat Chill Penguin and Flame Mammoth's factory
freezes, beat Storm Eagle and his airship wrecks Spark Mandrill's power plant, beat Launch Octopus and Sting
Chameleon's forest floods. **System Crash finishes that idea.** Every Maverick now changes exactly one other stage, and
every stage can be changed by exactly one Maverick. Take one down and something else goes offline. The order you
choose shapes the world you play through.

No new enemies and no new bosses. The original three changes are kept exactly as they were.

## The eight stage changes

| Beat | Stage that changes | What happens |
| --- | --- | --- |
| Chill Penguin | Flame Mammoth: **Frozen Factory** (original) | The lava freezes over |
| Flame Mammoth | Chill Penguin: **Meltdown** | The igloos melt open (no Tombots, Heart Tank in the open) and no giant snowballs roll down the slopes |
| Storm Eagle | Spark Mandrill: **Blackout** (original) | Death Rogumer crashes into the power plant |
| Spark Mandrill | Boomer Kuwanger: **Grid Down** | The tower runs on emergency lighting, Kuwanger's arena included; one laser-grid sensor and the Turn Cannon lose power |
| Boomer Kuwanger | Storm Eagle: **Radar Down** | Airport running lights and control tower windows go dark, a third of the Sky Claws hang dead, one of Death Rogumer's deck guns loses its target |
| Launch Octopus | Sting Chameleon: **Flooded Forest** (original) | The low forest floods |
| Sting Chameleon | Armored Armadillo: **Ambush Called Off** | A third of the Batton Bone roosts are empty and a third of the Metal Wing ambushes on the minecart ride never come |
| Armored Armadillo | Launch Octopus: **Empty Arsenal** | The munition silos stand empty and the Mega Tortoises drop one bomb instead of two in two volleys out of three |

If the Maverick has not been beaten, the stage is exactly the original. Bosses, weapons, items, passwords, Sigma's
fortress and the ending are unchanged. Every Heart Tank, Sub Tank, armour part and the Hadouken can still be found in
any order.

## On screen

- **Stage select:** every stage a beaten Maverick has changed says OFFLINE at the bottom of its portrait, in the
  green of the STAGE / MAP / SPEC panels
- **Title screen:** SYSTEM CRASH under the MEGA MAN X logo, in the gold of the X

## How to play

1. Download `MegaManX_SystemCrash_v1.0.zip` from the [Releases](../../releases) page
2. Apply `system_crash_v1.0.bps` to your own **Mega Man X (USA) (Rev 1)** ROM with Floating IPS (Flips), beat, or the
   online ROM Patcher JS
3. Play the patched ROM in your emulator or on a flash cart

| Required ROM | |
| --- | --- |
| Title | Mega Man X (USA) (Rev 1) |
| Size | 1,572,864 bytes, unheadered |
| CRC32 | `DED53C64` |
| SHA-1 | `C65216760BA99178100A10D98457CF11496C2097` |

The patch refuses any other ROM. A file of 1,573,376 bytes has a 512-byte copier header; remove it first. No ROM is
included in this repository or its releases.

## Building from source

You need your own Rev 1 ROM, Python 3, Asar 1.91 and Flips. Put the ROM in `rom_private/`, the tools in
`tools/vendor/` (see `BUILD.md`), then:

```
python tools/build.py --name system_crash_v1.0
```

The build checks the ROM's hashes, assembles `src/main.asm` (every hook asserts the original bytes first), writes the
BPS and checks that it round-trips. `tools/release.py` makes the release zip.

## Testing

The `tests/` folder drives the game headlessly (snes9x and bsnes-mercury through libretro, Mesen 2 through its Lua
test runner) and compares the patched game against the original:

- every combination of beaten Mavericks for every stage
- checkpoints, death and respawn, passwords
- every Heart Tank, Sub Tank and armour capsule in both versions of each stage, and the Hadouken
- every changed enemy placement, and a real minecart ride through Armored Armadillo's mine
- the boss fights of the changed stages, Sigma's fortress, the final battles, the escape and the credits
- the stage select and title additions, with the game after them identical to the original

Not yet tested on real hardware. Please open an issue if anything looks wrong.

## Credits

System Crash by RetchERezzed.

Mega Man X is © Capcom. This is an unofficial fan project, not affiliated with or endorsed by Capcom.
