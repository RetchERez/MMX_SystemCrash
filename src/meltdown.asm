; ---------------------------------------------------------------------------
; MELTDOWN -- Chill Penguin (stage 08) altered when Flame Mammoth is beaten.
;   (No palette change: the snow stays white. Owner decision 2026-11-24 - a
;   recoloured "thawed" snowfield read as dirt.)
;   1. Igloos ($57) are melted: at spawn each applies its own post-destruction
;      map patch (exactly the patch Fire Wave's destruction makes, $87:E472-E492)
;      and deletes itself: no shake, no debris, no Tombot nest. The patch is what
;      opens the Heart Tank igloo.
;   2. Rolling snowballs ($54) decline at spawn: no snow left to roll.
; ---------------------------------------------------------------------------

; --- igloo: $87:E354 LDX $01 / $87:E356 JSR ($E38D,X)  (M=1 X=1, state in X)
org $87E356
	%assert_bytes($87E356, $FC, $8D, $E3)
	jsr CR87_Igloo

org $87FFD0
CR87_Igloo:
	cpx #$00
	bne .live
	jsl SC_MeltGate
	bcc .live
	jsl SC_IglooMelt	; map patch + $3A = 1
	rts			; back at $87:E359: LDA $3A / BNE -> JSL $828398 (delete)
.live:
	jmp ($E38D,x)
	assert pc() <= $87FFEC, "code overlaps the next block"

; --- snowball: entry $87:E037  LDA $35 / TSB $11  (4 bytes) -> JML
org $87E037
	assert read1($87E037) == $A5 && read1($87E038) == $35 && read1($87E039) == $04 && read1($87E03A) == $11
	jml SC_SnowballEntry

org $84FB60
SC_MeltGate:			; C=1: Chill Penguin's stage in its Meltdown state
	php
	sep #$20
	pha
	jsl SC_Altered
	bcc .no
	lda.l $7E1F7A
	cmp #$08
	bne .no
	pla
	plp
	sec
	rtl
.no:
	pla
	plp
	clc
	rtl

SC_IglooMelt:			; replica of the patch step of the native destruction ($87:E472-E492)
	rep #$20
	lda $05
	sec
	sbc #$0030
	sta.w $002C
	lda $08
	sec
	sbc #$0020
	sta.w $002E
	sep #$20
	lda #$00
	sta $0B
	jsl $848011		; native map-block patch
	lda #$01
	sta $3A			; the igloo deletes itself on return
	rtl

SC_SnowballEntry:
	jsl SC_MeltGate
	bcs .decline
	lda $35			; replaced
	tsb $11			; replaced
	jml $87E03B
.decline:
	jml $828387
	assert pc() <= $84FC00, "code overlaps the next block"

; the native destruction step we replicate (bytes checked)
assert read1($87E472) == $C2 && read1($87E477) == $E9 && read2($87E478) == $0030
assert read1($87E480) == $E9 && read2($87E481) == $0020 && read1($87E48C) == $22 && read2($87E48D) == $8011
