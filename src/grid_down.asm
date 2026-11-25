; ---------------------------------------------------------------------------
; GRID DOWN -- Boomer Kuwanger (stage 07) altered when Spark Mandrill is beaten.
;   1. Emergency-lighting palette bank (dimmed copies of the stage's own sets)
;   2. Two thirds of the powered weapons work (4 of 6): Ray Trap sensor emitters ($42)
;      at x $0260 and $0370 are dead (no beam $43); sensors at $01FC, $02EE and
;      $0410 stay on backup power, and any live beam still arms every Ray Trap
;   3. The fixed Turn Cannon ($17) never fires
; Gameplay hooks call CR_Altered, which is false outside stage 07 (Sigma safe).
; ---------------------------------------------------------------------------

; --- 1. palette data + slot table (generated from the user's ROM by tools/build.py)
; Slot lists mirror the retail stage-07 lists; rows 2-4 (interior) point at dimmed
; copies, all other rows (sky, sunlit exterior, ladders) at the original data.
incsrc "../build/gen/kuw_palette.asm"

; retail slot lists we mirror (stage 07: slot0 @A260+$018D, slot1 @A260+$01A7)
assert read2($86A260+$006A) == $018D
assert read2($86A260+$006C) == $01A7
assert read2($86A260+$018D) == $E640
assert read2($86A260+$01A7) == $E9C0

; --- 2. sensor emitter: skip the beam spawn ---------------------------------
; $87:B8C4  JSR $B8ED  (M=1 X=1, DP = actor slot)  ->  JSR CR87_Sensor
org $87B8C4
	%assert_bytes($87B8C4, $20, $ED, $B8)
	jsr CR87_Sensor

; --- 3. Turn Cannon: skip the fire path -------------------------------------
; $87:9A26  REP #$10 / JSL $828358 (6 bytes, reached by BEQ when anim event $0F=2)
; -> JMP CR87_TurnFire; altered returns via RTS exactly like $87:9A25.
org $879A26
	%assert_bytes($879A26, $C2, $10, $22)
	%assert_bytes($879A29, $58, $83, $82)	; JSL $828358 is overwritten too; the stub re-executes it
	jmp CR87_TurnFire

; second fire path: diagonal pair, reached by BMI when anim event $0F < 2
org $879A5B
	%assert_bytes($879A5B, $C2, $10, $22)
	%assert_bytes($879A5E, $58, $83, $82)	; JSL $828358 is overwritten too; the stub re-executes it
	jmp CR87_TurnFire2

org $87FEE0
CR87_Sensor:			; M=1 X=1, DP = sensor actor slot ($05/$06 = X position)
	jsl CR_Altered
	bcc .live
	; Two thirds of the tower's powered weapons stay on backup power (4 of 6): sensors at
	; x $01FC, $0260, $02EE, $0410 live; the sensor at x $0370 dead; Turn Cannon dead.
	rep #$20
	lda $05
	cmp #$0350
	bcc .live16
	cmp #$03A0
	bcc .dead16		; $0350-$039F: the $0370 sensor
.live16:
	sep #$20
.live:
	jmp $B8ED		; original subroutine; its RTS returns to $87:B8C7
.dead16:
	sep #$20
	rts

CR87_TurnFire:
	jsl CR_Altered
	bcs .skip
	rep #$10		; replaced: REP #$10
	jsl $828358		; replaced: JSL $828358 (its Z result feeds BNE at $87:9A2C)
	jmp $9A2C
.skip:
	rts			; same as the retail non-firing path ($87:9A25)

CR87_TurnFire2:
	jsl CR_Altered
	bcs .skip
	rep #$10		; replaced: REP #$10
	jsl $828358		; replaced: JSL $828358 (its Z result feeds BNE at $87:9A61)
	jmp $9A61
.skip:
	rts
	assert pc() <= $87FF40, "code overlaps the next block"		; bank-87 stub area for Grid Down ends here (Radar Down starts at $87:FF40)

; --- 4. Kuwanger's arena ----------------------------------------------------------
; The arena is part of the tower and stays on emergency lighting like the rest of it.
; Boomer Kuwanger himself is untouched: no patch code runs in his actor (verified by
; tests/test_bosses.py: his actor memory is identical to the original every frame).
