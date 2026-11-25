; ---------------------------------------------------------------------------
; RADAR DOWN -- Storm Eagle (stage 05) altered when Boomer Kuwanger is beaten.
;   1. The control tower's and the booth's window glass go dark.
;      Window map tiles share colours with Death Rogumer's hull, so instead of a
;      palette edit the tower's own map cells are retargeted (in WRAM, after the
;      level loader) to appended copies of those map entries that use BG row 0,
;      which Eagle's stage never shows (verified: 0 visible pixels, all layers).
;      Row 0 is loaded with the tower's own colours, glass indices darkened.
;   2. One of Death Rogumer's two deck turrets ($50, the one at x 6190) never fires.
;   3. A third of the radar-guided Sky Claws ($49) hang dead: every third spawn X (5 of 17)
;      skips its behaviour dispatch, so it stays at its post; it can still be shot
;      and still hurts on contact. The other 12 work normally.
;   4. The running lights on the airport's platforms go out (see the end of this file).
; Data in build/gen/eagle_*.asm is generated from the user's ROM by tools/build.py.
; ---------------------------------------------------------------------------

incsrc "../build/gen/eagle_data.asm"	; CR_EagleMaps, CR_EagleColl, CR_EagleRetarget, CR_EagleSlots

; --- 2. deck turret: skip shot + muzzle effect -------------------------------
; $87:D453  JSR $D492 / JSR $D4FA  (M=1 X=1)  ->  JSR CR87_Turret / NOP x3
; $87:D459  JMP $D465 (re-arms the 90-frame timer) is untouched.
org $87D453
	%assert_bytes($87D453, $20, $92, $D4)
	%assert_bytes($87D456, $20, $FA, $D4)
	jsr CR87_Turret
	nop
	nop
	nop

org $87FF40
CR87_Turret:			; M=1 X=1, DP = turret actor slot ($05 = X position)
	jsl CR_Altered
	bcc .fire
	; Radar loss knocks out one of the two deck turrets (x 6086 live, x 6190 dead)
	rep #$20
	lda $05
	cmp #$1800
	sep #$20
	bcs .skip
.fire:
	jsr $D492		; replaced: fire projectile
	jsr $D4FA		; replaced: muzzle effect
.skip:
	rts
	assert pc() <= $87FF80, "code overlaps the next block"

; --- 3. Sky Claw: dead claws skip their behaviour dispatch --------------------
; $87:C3D5 LDX $02 / $87:C3D7 JSR ($C404,X)  (M=1 X=1, DP = claw slot)
; -> JSR CR87_SkyClaw; live claws continue with the same JMP ($C404,X), whose RTS
;    returns to $87:C3DA exactly as before. Collision, damage and drawing follow.
org $87C3D7
	%assert_bytes($87C3D7, $FC, $04, $C4)
	jsr CR87_SkyClaw

org $87FF60
CR87_SkyClaw:
	jsl CR_Altered
	bcc .live
	jsl CR_SkyClawIsDead
	bcs .dead
.live:
	jmp ($C404,x)
.dead:
	rts
	assert pc() <= $87FF80, "code overlaps the next block"

; --- 4. airport lights out ----------------------------------------------------
; The chasing lights on every girder platform are BG row 1, colours 1-7/13/14, cycled by the
; palette animator effect $33 sub $09 (one per section: x 128, 3440 and 6800). The retail game
; already switches this same animator for its own reactions ($82:FA19: Frozen Factory adds $0A,
; Blackout adds $0E). Radar Down refuses sub $09 before Death Rogumer (x < 6800) with the
; routine's own duplicate-decline path, and the altered palette list loads row 1 with those
; colours at the game's unlit value $0000 (CR_EagleRow1Off). Death Rogumer has its own power:
; its animator (x 6800) runs as retail, so the ship and the Storm Eagle fight are unchanged.
; $82:FA41  LDA $0B / CLC / ADC $0000 / JML $848F7D  (M=1 X=1, D = effect slot)  ->  JML CR_FxAnim
org $82FA41
	%assert_bytes($82FA41, $A5, $0B, $18)
	%assert_bytes($82FA44, $6D, $00, $00)
	%assert_bytes($82FA47, $5C, $7D, $8F)
	%assert_bytes($82FA48, $7D, $8F, $84)
	jml CR_FxAnim

org $84FD00
CR_FxAnim:
	lda $0B
	cmp #$09
	bne .retail
	jsl CR_Altered
	bcc .retail
	lda.l $7E1F7A
	cmp #$05
	bne .retail
	rep #$20
	lda $05
	cmp #$1A90			; x 6800: Death Rogumer's own animator stays
	sep #$20
	bcs .retail
	jml $828387			; decline (as $82:F9FF does for duplicates)
.retail:
	lda $0B				; replaced instructions
	clc
	adc.w $0000
	jml $848F7D
	assert pc() <= $84FD40, "code overlaps the next block"
