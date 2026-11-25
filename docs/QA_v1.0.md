# CHAIN REACTION v1.0 — QA record

Build: `chain_reaction_v1.0.sfc`, 2,097,152 bytes, CRC32 2FCD2B72 (byte-identical to candidate rc6).
BPS 4,447 bytes, roundtrip verified against the Rev 1 source (CRC32 DED53C64).
Logs: `qa/` in the development ZIP (`run_all_final.log`, `ending.log`, `bsnes_*.log`, `mesen.log`, matrix JSON).

Changes since the first v1.0 package (2026-11-25, user requests):
- every cut is one in three, so two thirds remain: 21 of 62 Batton Bone roosts, 3 of 9 Metal Wings and 5 of 17 Sky
  Claws go quiet; Grid Down keeps 4 of its 6 powered weapons (one laser sensor, x $0370, and the Turn Cannon are dead);
  Mega Tortoises skip their second bomb in two of every three volleys (counted in the tortoise's own unused slot byte
  $3F); Radar Down's radar-guided weapons were already a third (5 of 17 Sky Claws + 1 of 2 deck turrets = 6 of 19)
- Radar Down also turns off the running lights on every airport platform: the stage's palette animator (effect $33
  sub $09) is refused before Death Rogumer, and row 1 loads with the lights at the game's unlit value. The retail game
  uses this same animator switch for Frozen Factory and Blackout ($82:FA19). Death Rogumer keeps its lights
- Kuwanger's boss room restores its lights when the boss appears (from rc3)
- timing quirks removed (rc6): the Batton Bone gate moved from the bat's per-frame dispatch to its spawn state
  ($87:A10D), and the two load hooks exit on a quick stage-number check, so stages without a new reaction run the same
  CPU cycles as the original. This removed the bsnes Sigma 2 joypad-byte difference and the Mesen Mandrill
  frame-counter offset that earlier builds showed

## Exercised (snes9x libretro, headless, scripted)

| Area | Result |
| --- | --- |
| Load matrix: 256 boss masks x 8 stages vs vanilla | 0 failures; each new target changes for exactly its 128 masks, one altered signature; retail stages unchanged |
| Parity: source boss alive, 10 stage/mask combos | WRAM identical to vanilla over 900 frames |
| Persistence: checkpoints 0-2, real death + respawn, passwords | altered state restored every time (Grid Down, Radar Down, Empty Arsenal) |
| Reaction tests | 4 of 5 sensors live; far beams arm traps in both states; Turn Cannon dead only in Grid Down; 1 of 2 deck turrets silent; listed Sky Claws frozen; Mega Tortoise bombs 28 -> 18; listed bat roosts empty; listed Metal Wings declined; igloos melt, no snowballs; platform lights out |
| Whole-stage sweep, differential vs vanilla | all 62 Batton Bones (21 quiet), 17 Sky Claws (5 frozen), 9 Metal Wings (3 declined), the real Turn Cannon; normal state identical to vanilla; unlisted placements behave as on vanilla. One known variance: whether the game spawns the Sky Claw at x 4848 depends on timing and route (from checkpoint 1 it does not appear in vanilla either), so in the glide test it is absent in Radar Down; it is not a placement the patch removes |
| Real minecart ride (Armadillo), hands-off from the cart | normal identical to vanilla; Ambush: the 3 listed Metal Wings never come, every other wing that attacks in vanilla attacks |
| Collision | identical normal vs altered in every reachable cell, every checkpoint, all five stages |
| Items, both states, all 8 stages | every Heart Tank and Sub Tank collected; every capsule spawns |
| Hadouken | awarded by the retail capsule ($87:D0DB) at the same frame as vanilla; in real play it is always taken in Ambush Called Off (it needs every Maverick beaten) |
| Boss fights of changed stages | Kuwanger and Storm Eagle fights as retail (Eagle differs only in the undisplayed row 0) |
| Controller-only traversal, every checkpoint | no softlocks or crashes; deaths only at retail pits the bot also falls into on the normal stage |
| Sigma | fortress icon appears after all 8 and loads Sigma 1 for real; Sigma 1-4 WRAM identical to vanilla over 2,400 frames |
| Ending (`tests/test_ending.py`) | final room, Velguarder (HP set to 1 once it fights, killed by X's shot), Sigma (real buster hits only), Wolf Sigma (its head is out of reach from the floor: after 300 frames the game's own lethal-hit writes $88:CBF3-CC0F stand in for the final shot), then the game's own death sequence, escape, epilogue, credits and Sigma's last message: all of WRAM identical to vanilla in all 134 snapshots (every 300 frames, about 40,000 frames) |

## Other emulators

**bsnes-mercury balanced (libretro)**, WRAM cleared at load (bsnes randomizes power-on RAM): reaction tests, items,
Hadouken, boss arenas, platform lights, parity (10/10 identical) and Sigma 1-4 (all identical to vanilla) rerun with the
same results.

**Mesen 2.1.1** (`--testrunner`, Lua, real password and stage select, every stage, source alive and beaten): normal
states identical to vanilla after 240 frames of play; Grid Down, Radar Down and Empty Arsenal differ at load only in their
own palette rows, level pointers and blockMap (plus loader scratch `$10-$1F`, and for Radar Down the refused light
animator's effect slot and event flag); Ambush and Meltdown identical at load. All 16 runs pass.

## Not exercised

- Real hardware (no flash cart run).
- Sigma stages 1-3 played through to their ends (each is WRAM-identical to vanilla over 2,400 frames from its start;
  the ending run starts at Sigma stage 4). Wolf Sigma's last hit is a stand-in, as described above.
- A human playtest of difficulty and feel.
- Test-only pokes (camera borders, HP refill, positions, Sigma 2-4 stage number, Hadouken gear, minecart glide inside
  the mine region) are marked in each script and never ship.
