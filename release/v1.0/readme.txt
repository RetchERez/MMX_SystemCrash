MEGA MAN X: SYSTEM CRASH
Version 1.0
by RetchERezzed

In the original Mega Man X, beating some Mavericks changes other stages:
beat Chill Penguin and Flame Mammoth's factory freezes; beat Storm Eagle and
his airship wrecks Spark Mandrill's power plant; beat Launch Octopus and
Sting Chameleon's forest floods.

SYSTEM CRASH finishes that idea. Every Maverick now changes exactly one
other Maverick's stage, and every stage can be changed by exactly one
Maverick. Take one down and something else goes offline. The order you
choose shapes the world you play through.

No new enemies and no new bosses. The original three changes are kept
exactly as they were.


THE EIGHT STAGE CHANGES
-----------------------
Beat...            ...and this stage changes

Chill Penguin   -> Flame Mammoth: Frozen Factory (original)
                   The lava freezes over.

Flame Mammoth   -> Chill Penguin: Meltdown (new)
                   Mammoth's furnaces burn out of control and the heat
                   reaches the snow base. The igloos have melted open (no
                   more Tombots pouring out, and the Heart Tank lies open),
                   and no giant snowballs roll down the slopes.

Storm Eagle     -> Spark Mandrill: Blackout (original)
                   Death Rogumer crashes into the power plant.

Spark Mandrill  -> Boomer Kuwanger: Grid Down (new)
                   The power plant stops feeding the tower. The interior
                   runs on emergency lighting, Kuwanger's arena
                   included (the sky and the outside climb stay lit).
                   One laser-grid sensor loses power and the Turn Cannon
                   near the top is dead. The elevator, the hover
                   platforms and every robot still work.

Boomer Kuwanger -> Storm Eagle: Radar Down (new)
                   Kuwanger's tower carried the airport's radar. The
                   running lights on the airport's platforms go out,
                   the control tower's windows go dark, a third of the
                   Sky Claw cranes hang dead at their posts, and one of
                   Death Rogumer's two deck guns loses its target.

Launch Octopus  -> Sting Chameleon: Flooded Forest (original)
                   The low forest floods.

Sting Chameleon -> Armored Armadillo: Ambush Called Off (new)
                   Chameleon's ambush squads lose their commander. A third
                   of the Batton Bone roosts are empty, and a third of the
                   Metal Wing ambushes on the minecart ride never come.

Armored Armadillo -> Launch Octopus: Empty Arsenal (new)
                   The mine fed the sea base's ammunition. The munition
                   silos stand empty, and the Mega Tortoises run short:
                   two volleys in three come with one bomb instead of two.

If the Maverick has not been beaten, the stage is exactly the original.
The bosses themselves, weapons, items, Sigma's fortress and the ending are
unchanged.
Every Heart Tank, Sub Tank, armour part and the Hadouken can still be found
in any order. Passwords work as normal and restore every change.


ON SCREEN
---------
- Stage select: every stage a beaten Maverick has changed says OFFLINE at
  the bottom of its portrait, in the green of the STAGE / MAP / SPEC panels
- The label marks the stage that was changed, not the Maverick you beat,
  so you can see at a glance where the world is different
- Title screen: SYSTEM CRASH under the MEGA MAN X logo, in the gold of the X


REQUIRED ROM
------------
Mega Man X (USA) (Rev 1)
Unheadered, 1,572,864 bytes
CRC32: DED53C64
SHA-1: C65216760BA99178100A10D98457CF11496C2097

The patch refuses any other ROM. A file of 1,573,376 bytes has a 512-byte
copier header; remove it first.

After patching: 2,097,152 bytes (2 MB), CRC32 FE1AC27A.


HOW TO PATCH
------------
Apply system_crash_v1.0.bps to your own Mega Man X (USA) (Rev 1) ROM with
Floating IPS (Flips), beat, or the online ROM Patcher JS. No ROM is included.


CHANGELOG
---------
Version 1.0 (first release)
- Five new stage changes: Meltdown, Grid Down, Radar Down, Ambush Called
  Off and Empty Arsenal, so all eight Mavericks now change another stage
- The three original changes (Frozen Factory, Blackout, Flooded Forest)
  kept exactly as in the original game
- Every cut takes away one third, so two thirds of each enemy group or
  hazard stays in place
- Grid Down: emergency lighting through the tower interior and Kuwanger's
  arena; one laser-grid sensor and the Turn Cannon lose power
- Radar Down: airport running lights off, control tower windows dark, a
  third of the Sky Claws dead, one of Death Rogumer's deck guns silent
- Meltdown: melted igloos (no Tombots, Heart Tank in the open) and no
  rolling snowballs
- Ambush Called Off: a third of the Batton Bone roosts empty and a third of
  the Metal Wing ambushes on the minecart ride gone
- Empty Arsenal: empty munition silos and Mega Tortoises that drop one bomb
  instead of two in two volleys out of three
- Stage select: OFFLINE label on every stage a beaten Maverick has changed
- Title screen: SYSTEM CRASH subtitle under the logo
- Bosses, weapons, items, passwords, Sigma's fortress and the ending
  unchanged


TESTED WITH
-----------
snes9x (libretro), headless and scripted:
- every combination of beaten Mavericks for every stage
- checkpoints, death and respawn, passwords
- every Heart Tank and Sub Tank collected, and every armour capsule found,
  in both versions of each stage; the Hadouken awarded
- every changed enemy placement, against the original game, and a real
  minecart ride through Armored Armadillo's mine
- the boss fights of the changed stages
- Sigma's fortress entered from stage select; its four stages behave
  exactly like the original
- the final battles, the escape, the epilogue and the credits, identical to
  the original from start to finish
- the stage select and title screen additions: every combination of
  beaten Mavericks, and the game after them identical to the original

The stage changes, items, Hadouken, boss fights, Sigma's fortress,
identical-to-original play and the stage select and title additions were
run again on bsnes-mercury (libretro) with the same results, and every
stage was checked once more in Mesen 2. On bsnes, which runs the console
cycle by cycle, the stage select cursor can move a frame later while the
OFFLINE labels are shown; everything after it is identical.

Not yet tested on real hardware. Please report anything odd.
