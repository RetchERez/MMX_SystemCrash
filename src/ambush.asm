; ---------------------------------------------------------------------------
; AMBUSH CALLED OFF -- Armored Armadillo (stage 03) altered when Sting Chameleon
; is beaten. Chameleon's camouflaged ambush squads lose their commander:
;   1. Every third Batton Bone roost ($2D) is empty: 21 of 62 decline at spawn.
;   2. Every third Metal Wing ambush ($35) never comes: 3 of 9 decline at spawn.
; Lists: build/gen/halves.asm (every third spawn X from the retail events; two thirds remain).
; Batton Bones in other stages (Penguin, Sigma) are untouched: gates check stage 03.
; Decline = $82:8387, the game's own "despawn at spawn" exit (clears the spawn
; marker, deletes the actor, RTL to the dispatcher).
; ---------------------------------------------------------------------------

; Batton Bone: $87:A07F LDX $01 / $87:A081 JSR ($A105,X)  (M=1 X=1, state in X)
org $87A081
	%assert_bytes($87A081, $FC, $05, $A1)
	jsr CR87_Batton

org $87FFB0
CR87_Batton:
	cpx #$00		; state 0 = spawn
	bne .live
	jsl CR_BattonGate
	bcc .live
	pla			; drop this JSR's return (2 bytes, M=1)
	pla
	jml $828387		; decline; RTL returns to the actor dispatcher
.live:
	jmp ($A105,x)
	assert pc() <= $87FFD0, "code overlaps the next block"

; Metal Wing: state 0 begins $83:DBA6 JSL $84A1D5 (M=1 X=1)
org $83DBA6
	assert read1($83DBA6) == $22 && read1($83DBA7) == $D5 && read1($83DBA8) == $A1 && read1($83DBA9) == $84
	jsl CR_MetalWingInit

org $84FB00
CR_BattonGate:			; C=1: this Batton Bone's roost is empty
	php
	sep #$20
	pha
	jsl CR_Altered
	bcc .no
	lda.l $7E1F7A
	cmp #$03
	bne .no
	jsl CR_BattonIsDead
	bcc .no
	pla
	plp
	sec
	rtl
.no:
	pla
	plp
	clc
	rtl

CR_MetalWingInit:
	jsl CR_Altered
	bcc .orig
	lda.l $7E1F7A		; A is free here ($84:A1D5 starts with REP / loads)
	cmp #$03
	bne .orig
	jsl CR_MetalWingIsDead
	bcc .orig
	pla			; drop our JSL return (3 bytes, M=1)
	pla
	pla
	jml $828387		; decline; RTL returns to the actor dispatcher
.orig:
	jml $84A1D5		; replaced call; its RTL returns to $83:DBAA
