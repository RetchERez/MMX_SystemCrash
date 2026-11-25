# X1 reverse-engineering handoff

## Status and evidence boundaries

No ROM patch, emulator trace, actual actor modification, or completed gameplay test was produced in the prior chat. The earlier ROM verification was reported in prose; independently recheck the file. The sources below were inspected during the conversation. Their findings are leads, not proof of Rev 1 instruction boundaries. The documented disassembly's bank 80 header explicitly contains version byte $00 (Rev 0), so its address labels must be resolved against the user's Rev 1 image. MegaED X source explicitly distinguishes Rev 0 and Rev 1 event-loader addresses. Do not assume a uniform delta between builds.

## Progression and stages

Source: LordTony/MegaManXRandomizer rando.py (Rev 1 target) and AkiteruSDA disassembly (Rev 0 reference). Candidate stage IDs and weapon acquisition byte addresses derived from their vanilla ordering and existing reaction checks:

| Stage ID (hex) | Stage | Candidate acquisition byte (WRAM bank 7E) |
|---|---|---|
| 00 | Highway | n/a |
| 01 | Launch Octopus | 1F88 |
| 02 | Sting Chameleon | 1F8A |
| 03 | Armored Armadillo | 1F8C |
| 04 | Flame Mammoth | 1F8E |
| 05 | Storm Eagle | 1F90 |
| 06 | Spark Mandrill | 1F92 |
| 07 | Boomer Kuwanger | 1F94 |
| 08 | Chill Penguin | 1F96 |

Current stage candidate $7E:1F7A. Native code tests bit 6 (0x40) of the acquired weapon byte, not merely nonzero weapon energy. In 16-bit accumulator mode BIT $1F95 / BVC examines bit 14, i.e. bit 6 of $1F96. BIT $1F8F tests $1F90; BIT $1F87 tests $1F88. Verify this in Rev 1 via debugger and real password load. Existing progression/weapon flags are suitable only if confirmed to reflect defeat under vanilla progression.

Rev 0 bank 80 reference:
- $80:B4FD conditional graphics/palette table selection; stage 04 uses BIT $1F95, stage 06 uses BIT $1F8F. Altered table offset $000A. The subsequent table at $86:A260 uses stage and current palette selector.
- $80:BC72 conditional stage data state; stage 04 Penguin flag, stage 06 Eagle flag, stage 02 Octopus flag. Native writes to $7E:E840 etc. Do not copy these writes into unrelated stages without understanding map structures.
- $80:F296 password decode loops over weapon/progression bytes, writing $40 for acquired weapons; confirm Rev 1 equivalent.

Rev 1 randomizer source lists these **PC file offsets of operand bytes**, not hooks. Read surrounding instructions. Preserve these for the original reactions:
- Penguin checks: 0x3C72, 0x3509, 0x17A38, 0x218A2, 0x39E97, 0x3BD76
- Eagle checks: 0x3C84, 0x34FD, 0xB4CD, 0xB4F0, 0x17A2C, 0x2311B, 0x3FCED, 0x3F6DE, 0x3F66D, 0x3F715
- Octopus check: 0x3C96

Randomizer changes which weapon flag these checks use. Do not apply its randomization or weapon edits; it is only evidence of native state checks. Verify all bytes independently. Headerless LoROM PC offset = ((bank & 0x7F) * 0x8000) + (address & 0x7FFF), for ROM addresses $8000-$FFFF in mapped banks.

## Stage event data

MegaED X X1 tables (SNES addresses, validate on actual ROM):
- Event pointer table $85:82C2 (16-bit pointers within bank $85, indexed by stage ID * 2)
- Layout $86:8D24; scenes $86:8D93; blocks $86:8E02; maps $86:8E71; collision $86:8EE0 (24-bit pointers indexed by stage ID * 3)
- Background layout $86:8F4F; background scenes $86:8FBE; background blocks $86:902D
- Dynamic palette table PC $32260 (SNES $86:A260); checkpoint table $86:A780
- Graphics config $86:F56F; graphics positions $86:F6F7

Event stream: first byte is block ID. Each record is seven bytes: type/match (type low 2 bits), Y little-endian word, actor/event ID, sub-ID, X/flags little-endian word (X low 13 bits, flags upper 3). Bit 15 means last record in block. Next byte is next block ID; repeated block ID terminates stream. Verify against original size and pointer boundaries. The supplied audit script exports records without modifying them. Type 3 is the usual enemy/object class. Type 0 includes pickups and doors; type 2 includes checkpoints and graphics events.

MegaED X explicitly identifies Rev 1 event loader immediate bank operands around $80:DB7C, $80:DBC3, $80:DD36 (instruction start) and pointer table operand $80:DB88. Rev 0 counterparts $80:DB92, $80:DBD9, $80:DD4C and $80:DB9E. These are not universal relocation offsets. The event-loading code builds a WRAM index of event records. If adding an event stream, trace loader and scanner to ensure pointers/bank/record termination remain correct; avoid overwriting next stage data. Consider a dedicated alternate stream in verified free space, selected at initialization, or a correctly gated actor spawn. Avoid event relocation of the entire ROM unless needed.

## Actor research (Rev 0 disassembly labels unless noted)

XSharp ROMExporter maps type-3 X1 actors $44 Ray Trap, $49 Sky Claw, $50 Death Rogumer cannon, $57 igloo/bunker, $5B Mega Tortoise, $20 Amenhopper, $2B minecart, $2C Mole Borer, $03 Thunder Slimer, $59 Lift Cannon. It does NOT identify Slide Cannon, Metal Wing or Cruiziler in that exporter. Do not assign unknown IDs by name alone. Determine these from actual stage event listings, screenshots and debugger, including actors spawned by another actor rather than direct event records.

The Rev 0 bank 80 actor dispatch table starts $80:F8F3 (2-byte pointers; wrappers call a long routine and RTS). In that reference:

| Actor | Wrapper | Routine |
|---|---|---|
| 44 Ray Trap | 80:FB1B | 87:BA72 |
| 49 Sky Claw | 80:FB34 | 87:C387 |
| 50 Death Rogumer cannon | 80:FB57 | 87:D3AF |
| 57 bunker | 80:FB7A | 87:E354 |
| 5B Mega Tortoise | 80:FB8E | 87:EBFE |
| 20 Amenhopper | 80:FA67 | 82:AAD0 |
| 2B minecart | 80:FA9E | 88:97BA |
| 2C Mole Borer | 80:FAA3 | 83:BF44 |
| 03 Thunder Slimer | 80:F9D6 | 84:AE3D |
| 59 Lift Cannon | 80:FB84 | 87:E7D4 |

These dispatch slots may be useful for resolving actual Rev 1 addresses. Verify type and event mapping from ROM rather than assuming identity.

### Mammoth -> Penguin

Reference actor $57: initialization $87:E397 sets health $10, damage row $11, timers and animation. $87:E354 dispatches state via $01. On lethal hit, $87:E36D assigns state $08; $87:E462 is native destruction state (debris, map update via $84:8011, cleanup). Recomp documentation independently describes bunker behavior. Important: simply preventing the actor spawn may leave terrain intact; simply jumping directly to destruction without initialization may corrupt object state. Native destruction also spawns many debris objects. Identify which bunker(s) and which one covers the Heart Tank from event data. Trigger safe native destruction after initialization or load a proven equivalent open map state, preserve all other items and enemies as much as possible. If other bunkers are thawed, acknowledge their native spawned Tombots are then absent as a direct consequence; prefer only the relevant shelter per design. Visual thaw requires real existing tile replacements (no water import necessary). Inspect actual scene/block map and render before committing. Do not claim entire thaw is done if only bunker changed.

### Mandrill -> Kuwanger

Ray Trap reference $87:BAE3 initializes timer $33 to $20 (32 frames); routine $87:BAE8 decrements; projectile/action call $87:BB09 happens at $33 == 4. Verify what the call actually does in game before changing. Candidate $1B (27 frames) produces 23 vs 28 frames to that event (~18% decrease); retain remaining animation/shot state. Stage gate and source acquisition check required. Slide Cannon identity and exact timing not resolved. Do not change Lift Cannon merely because name is similar. Preserve moving-platform collision and item routes.

### Kuwanger -> Armadillo

No direct native Metal Wing conditional spawn has been proven. StrategyWiki reports extra birds; MMHP calls it a report not tested. Identify bird actor/event (may be dynamically spawned), verify baseline with source alive/dead, then add a single existing formation if needed. Do not blindly use unknown ID $35; a candidate routine at $83:DB9B was examined but not established as Metal Wing. Check object count, final jump and Hadouken ledge.

### Armadillo -> Octopus

Mega Tortoise actor $5B reference $87:EBFE; $87:EC8B sets timer $34 to $28; $87:ECB2 sets timer to $30. $87:ECF1 onward allocates projectile actor $25 plus auxiliary object $10/sub $28. This does not by itself establish that the two are separate bombs: the second allocation may be a parachute/visual component. Confirm actual two-projectile sequence before reducing a volley. A verified cooldown increase is a possible fallback if one-bomb change is unsafe, but document deviation. Cruiziler ID/routine unresolved. Trace real bomb cadence and crash/Heart Tank path. No change to Octopus boss.

### Chameleon -> Eagle

Sky Claw routine $87:C387 reference: follows X horizontally then changes state; timers $15/$1E at $87:C47B, $87:C494, $87:C4AC are tied to movement phases. DO NOT lengthen them blindly, since that changes travel distance and could cause grabs/pit issues. Prefer fallback unless a true acquisition timer is identified. Cannon routine $87:D3AF: $87:D465 and $87:D486 set timer $33 to $5A (90 frames); $87:D43D decrements, $87:D44F checks animation/event flag, $87:D453 calls projectile creation $87:D492 and associated effect $87:D4FA. Candidate 104 frames (~15.6% longer) on genuine attack cadence only. Confirm whether each timer is cooldown or animation-linked, and stage gate. Existing control panels only if verified.

## Engineering and QA

Implement with a per-stage flag predicate, scoped to actual stage and actor subtype where necessary. Preserve accumulator width, index width, DBR, DP, stack and expected flags; avoid globally changing actor constants. Any free-space region must be verified with actual ROM bytes and reference scans. Rev 0 bank 80 has padding after $80:FBE2, but Rev 1 layout differs. Validate checksum handling for non-power-of-two LoROM. No ROM included in release. Use BPS source/target checks and reapply to verify byte-for-byte. No new state in passwords. Test all 256 abstract progression masks plus actual emulator gameplay and password persistence. See design/FINAL_v1.0.txt for complete acceptance checklist.

Known design ambiguity: final design allows water reuse if clean; latest conversation preferred no imported water. Treat water as optional, default to stage-native rock/metal and existing bunker state. Likewise graphic status flourishes are optional but core reactions must be observable. Existing vanilla behaviors are preservation requirements, not independently measured claims. All five proposed links and causal lore are mod design, not historical Capcom content. Facility character descriptions from the later PSP remake are inspiration only, not proof of SNES hardware connections.
