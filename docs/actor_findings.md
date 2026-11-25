# MMX Rev 1 actor findings (read-only RE)

Sources: Rev 1 ROM bytes and tools/dis65.py, the AkiteruSDA Rev 0 bank 87 listing, and the mstan symbol names (eventID_*). I compared every patch site below byte for byte against the Rev 1 ROM, and all match. Bank 82 sits +7 bytes from Rev 0 in this area. "Read" means I traced it in the code. "Inferred" means I did not.

Object pools (read, from 82:82B9-8358):
- Enemies at $0E68-$1228. Allocated by `JSL $828321`; IDs use the bank-80 enemy table
- Player shots at $1228-$1428. These are what `849B43` hit-tests against
- Enemy projectiles at $1428+. Allocated by `JSL $828358`; separate ID table
- Effects at $1928-$1D08, $20 stride (31 slots). Allocated by `JSL $8282D3`; separate ID table, so effect $10 is not enemy $10

Helpers:
- `849B03` = contact damage vs. player
- `849B43` = hit/HP check (negative = killed)
- `848011` = stage-indexed map-block patch (reads $1F7A to choose the table; probably changes collision too, inferred)
- `84A31A` = screen shake / quake request
- `84A4AB` = death explosion
- `8088A2` = play SFX

**None of these actors reads $1F7A or $1F88-$1F97** (grepped every range listed). The only boss-flag read nearby is $47 Flame Pillar (`BIT $1F96` at 87:BD75, not in scope). Every patch below is global: it also hits Sigma and other stages unless you wrap it in a $1F7A check.

Disable idioms:
- Spawn-time "decline": 4-byte `5C 87 83 82` (JML $828387) over the entry point. This is the same path the game uses natively, e.g. 87:E052 and 87:EC4B
- Fire-skip: turn the `BNE` after the slot-allocation JSL into `BRA` (D0→80), so the state machine runs as if the pool were full

---

## $41 breakableGlass, 87:B542 (Storm Eagle tower)
Not an enemy. It is breakable glass (read).
- **sub $00/$01 (glass panes)**
  - HP 2 ($27), $28=3. If flag `$1F3F+sub` is already set, it deletes itself at once (87:B56C)
  - When shot out: patches map blocks (848011, X from 86:D1F3/D203, Y $0230), spawns effect $10/$13, sets `$1F3F+sub`, deletes itself
- **sub $80 (controller)**
  - Spawns **enemy $29 Gun Volt** (sub $80, at Y-6) at 87:B675
  - Watches it each frame (87:B7CF). When Gun Volt dies (its $27=$80) or its slot is reused, it runs a shatter: 8 steps x 6 frames of paired effect $10/$12 debris along the glass, SFX $1B. On step 7 it breaks both panes ($1F3F/$1F40). Then 8 map-block patches 6 frames apart from X $0670, and a `84A311` A=$14 call (screen effect, inferred), then it deletes itself
- **Disable:**
  - Whole object: `87:B542 A5 0B 30 5C` → `5C 87 83 82`. This removes the tower Gun Volt, and the glass becomes permanent background
  - Panes only: write the same bytes inside the sub ≥ 0 path
- **Risk:**
  - $1F3F/$1F40 are generic stage-event bytes. `$1F40` is also read by the Sigma head ($64, 87:EDEB). I did not check whether they are cleared on stage load
  - The map patches may open collision; I have not checked whether progress needs them

## $46 airPortGasTank, 87:BC8B ("missiles", Storm Eagle)
**Does not launch anything.** It is a destructible prop (read).
- Absolute position from the table at 86:D26A by subID. HP $20 (32), $28=3. No contact damage is set
- On kill: every 6 frames it calls `84A31A` (X5/Y2/A6), puts 2 random explosions with SFX $23, and patches map blocks (patch 7/8 alternating; patch 9 for sub 5). The step count comes from 86:D264,sub. Then it deletes itself
- **Disable:** `87:BC8B A6 01 D0 26` → `5C 87 83 82`. The tank graphics stay, unbreakable
- **Risk:** cosmetic only, as far as I can tell. The block patches could change collision (inferred)

## $48 deathRogumerPlatform, 87:C07A
**Do not disable. It is the boss-entry lift** (read).
- Fixed at X $1840 / Y $0160
- When the player stands on it (82D7D0 sets $2C), it takes player control (`$0C0C=2`), sets checkpoint `$1F81=2`, `INC $1F41`, and lifts the player
- Then it shakes the screen (A=$78), patches 21 map blocks via `848000` with SFX $21, waits $3C frames, sets `$1F08=7` and calls `80B087`
- Finally it **spawns enemy $52 (Storm Eagle)** at 87:C209

## $50 rogumerCanon, 87:D3AF
Deck turret. Does not move; turns to face the player (read).
- HP $0D, contact 3. Uses state 4 (turn anim) when the player is behind it
- Fire cycle: every $5A (90) frames it spawns enemy projectile **$13 sub 2**, horizontal ±$0200 at ±$20 px, plus muzzle effect $09
- On death: effect $38 plus 6x effect $2B debris
- **No shots:** `87:D453 20 92 D4 20 FA D4` → six `EA`. Turning and contact damage stay

## $44 laserTrap (Ray Trap), 87:BA72
Wall turret, HP 1, contact 1 (read).
- Idles until its $36 is set by a sensor beam (see $42)
- Then it charges for $20 frames. At count 4 it aims at the player (84A07C, sine table 86:EE37) and fires enemy projectile **$1C**, SFX $55. It fires once per trigger, then returns to idle
- **Never fires:** `87:BAD0 D0 07` → `EA EA`. It stays idle and shootable
- Do not patch the fire step instead: $36 then never clears and it re-charges forever

## $42 laser (sensor emitter), 87:B808
Invulnerable emitter ($30 set) (read).
- Cycle: delay of 1 frame, or $14 frames if sub bit $10 is set. Then $20 charge, then it spawns enemy **$43** (the beam; $33 = direction, cross variant when $1D toggles). Then $32 frames, and repeat (cycle ~83-103 frames)
- The beam is $43, 87:B91C. It flashes 8 frames, then stays live for $32 frames and only checks overlap with the player ($0BA8). It has no `849B03` call, so **no damage**, and no solid or platform code, so **it cannot block progress**
- When the beam touches X:
  - Normal subs: it sets $36 on **every $44 Ray Trap** in the enemy list (87:BA44), then deletes itself. The emitter waits $3C frames
  - Sub bit $20: instead spawns enemy **$01 Hoganmer** 30 px right and 64 px up, only if none exists (87:BA17)
- **Disable:** `87:B8C4 20 ED B8` → `EA EA EA`. The emitter still animates, but no beam appears and no Ray Traps trigger. Off is safe either way

## $13 dodgeBlaster, 82:99A6 (Rev 1)
Wall-mounted, but **slides vertically** along its wall (read).
- On spawn it steps up to 8 times toward a wall and snaps to it; with no wall it despawns. HP 3, contact 2
- Wakes when the player is within $80 px in front
- Tracks the player's Y at $0080. If the player has a shot out (`$1F0D`) and is within $20 px vertically, it dodges at $0200 for $10 frames
- When it is aligned within 4 px: waits $30 frames, then fires enemy projectile **$02** at ±$0C
- **No shots:** `82:9B03 D0 30` → `80 30`

## $17 turnCannon, 87:9944
Stationary, no movement code. HP 5, contact 3 (read).
- Waits $30 frames, then plays a fire animation
- Anim event $0F=2: a horizontal pair (projectile **$13 sub 5**, ±$0200), each with an effect
- $0F=1: a diagonal pair (projectile **$27**)
- Sub bit 7 links it to a parent through $33 (it reports its fire state and death to the parent's $35/$36). Look for that use before patching broadly
- **No shots:** `87:9A21 F0 03 30 36` → `EA EA EA EA` (falls into RTS)

## $5B megaTortoise, 87:EBFE
**Stationary.** No velocity or move calls. HP $10, contact 4 (read).
- Sub bit 0: despawns at spawn if the player is already right of it (87:EC48)
- Idles $28 frames. If facing the player it plays the fire anim (state 6); after that, $30 frames, then it repeats or goes back to idle
- **Volley:** each anim event with $0F = 1 or 2 spawns **one enemy projectile $25** at X ±7 (left/right hatch by event number, mirrored by facing), Y -$1C. It also spawns **effect $10 sub $28** at the same spot (a cosmetic puff in the effects pool, no hitbox) and SFX $1E
  - Inferred: the anim has two events, so **one volley = two real bombs**, one per hatch. The second object is not a parachute
  - Any parachute or descent behaviour would live inside projectile $25, which I did not read
- **No bombs:** `87:ECF7 D0 75` → `80 75`. This skips the bomb, the puff and the SFX; animation, contact damage and HP stay
- **Risk:** it is shared by Octopus, Kuwanger, Mandrill and Sigma; gate on $1F7A if the change is per-stage

## $53 snowShooter, 87:DE93
Stationary turret, faces the player. HP 8, contact 3 (read).
- At count $14 it aims (84A07C). It fires only inside an angle window: 4-$C when facing right, $14-$1C when facing left. Otherwise it resets to $5A
- Then it waits $30 frames and fires enemy projectile **$23 sub 2** with the aimed velocity. Period ~138 frames
- **No shots:** `87:DFBC 20 CD DF` → `EA EA EA`

## $54 snowBall, 87:E037
**A rolling, growing snowball hazard. It is not the Shooter's projectile** (the Shooter fires projectile $23) (read).
- Only spawns if it is right of the player (87:E052). Starts at x-speed $FF80, with gravity and bounces
- Grows every $1C ground frames: contact 1 → 2 → 3, with bigger hitboxes. HP 4. Leaves a snow-trail effect ($10/$27) every 4 frames
- When it hits a wall or is killed, it bursts into 6/8/10/12 effect $2B chunks with SFX $57 and deletes itself
- **Disable:** `87:E037 A5 35 04 11` → `5C 87 83 82`

## $57 igloo, 87:E354
HP $10, $28=$11 (read).
- **It does spawn Tombots:** in state 4 it spawns **enemy $3A sub $12** at Y+$26 every $60 frames
  - Spawning stops while 6 or more $3A are alive
  - Phases: first a $3C-frame delay; spawning for $120 frames; a $120-frame rest; then spawning for $180 frames, and so on
- Lethal hit → state 8 (87:E36D)
- **Native destruction** (87:E462):
  - Screen shake (A=$10, X3/Y1)
  - 2 big halves (effect $2B sub $D3/$D4 at ±$24, -$12)
  - **25 small chunks** (effect $2B, random sub from 86:D46A). These are capped by free effect slots; there are 31 in total
  - Map-block patch 0 at (X-$30, Y-$20)
  - 2 death explosions (one at X-$20); deletes itself next frame
- It never spawns the Heart Tank. The tank is presumably a separate actor or item revealed by the block patch (inferred)
- **No Tombots:** `87:E420 D0 21` → `80 21`; it stays destructible
- **Risk:** deleting the igloo at spawn would skip the block patch, which may leave the Heart Tank sealed

## $35, 83:DB9B (Armadillo; mstan calls it "metalWing")
Confirmed (read):
- Spawn condition: fewer than 5 of this ID alive (`84A1D5`, `CPY #$0A`) and `$0C26` bit 5 set
- HP 2, contact 3. X-speed $0480. Random delay $3C + (rand & $7E)
- **Disable:** `83:DBA6 22 D5 A1 84` → `5C 87 83 82`
