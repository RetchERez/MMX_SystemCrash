MEGA MAN X: CHAIN REACTION
Version 1.0
by RetchERezzed

In the original Mega Man X, beating some Mavericks changes other stages:
beat Chill Penguin and Flame Mammoth's factory freezes; beat Storm Eagle and
his airship wrecks Spark Mandrill's power plant; beat Launch Octopus and
Sting Chameleon's forest floods.

CHAIN REACTION finishes that idea. Every Maverick now changes exactly one
other Maverick's stage, and every stage can be changed by exactly one
Maverick. The order you choose shapes the world you play through.

No new enemies, no new bosses, no text. The original three changes are kept
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
                   runs on emergency lighting (the sky and the outside
                   climb stay lit), one laser-grid sensor loses power,
                   and the Turn Cannon near the top is dead. The elevator,
                   the hover platforms and every robot still work.

Boomer Kuwanger -> Storm Eagle: Radar Down (new)
                   Kuwanger's tower carried the airport's radar. The
                   running lights on the airport's platforms go out,
                   the control tower's windows go dark, a third of the
                   Sky Claw cranes hang dead at their posts, and one of
                   Death Rogumer's two deck guns loses its target.
                   Death Rogumer has its own power: its lights stay on.

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
Bosses, weapons, items, Sigma's fortress and the ending are unchanged.
Every Heart Tank, Sub Tank, armour part and the Hadouken can still be found
in any order. Passwords work as normal and restore every change.


REQUIRED ROM
------------
Mega Man X (USA) (Rev 1)
Unheadered, 1,572,864 bytes
CRC32: DED53C64
SHA-1: C65216760BA99178100A10D98457CF11496C2097

The patch refuses any other ROM. A file of 1,573,376 bytes has a 512-byte
copier header; remove it first.

After patching: 2,097,152 bytes (2 MB), CRC32 2FCD2B72.


HOW TO PATCH
------------
Apply chain_reaction_v1.0.bps to your own Mega Man X (USA) (Rev 1) ROM with
Floating IPS (Flips), beat, or the online ROM Patcher JS. No ROM is included.


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

The stage changes, items, Hadouken, boss fights, Sigma's fortress and
identical-to-original play were run again on bsnes-mercury (libretro) with
the same results, and every stage was checked once more in Mesen 2.

Not yet tested on real hardware. Please report anything odd.
