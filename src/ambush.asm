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

; Batton Bone: hooked in its spawn state only, so a bat costs nothing once it lives.
; State 0 = $87:A10D  LDA $0B / AND #$01 (4 bytes, M=1 X=1), reached by the dispatcher's
; JSR ($A105,X) at $87:A081 -> JML SC_BattonSpawn. A declined bat drops that JSR's return
; (2 bytes) so $82:8387's RTL goes back to the actor wrapper, as the old dispatcher stub did.
org $87A10D
	%assert_bytes($87A10D, $A5, $0B, $29)
	assert read1($87A110) == $01
	jml SC_BattonSpawn

org $84FD80
SC_BattonSpawn:
	jsl SC_BattonGate
	bcc .live
	pla			; drop the dispatcher's JSR return (2 bytes, M=1)
	pla
	jml $828387		; decline; RTL returns to the actor wrapper
.live:
	lda $0B			; replaced: LDA $0B / AND #$01 (Z feeds BNE at $87:A111)
	and #$01
	jml $87A111
	assert pc() <= $84FDC0, "code overlaps the next block"

; Metal Wing: state 0 begins $83:DBA6 JSL $84A1D5 (M=1 X=1)
org $83DBA6
	assert read1($83DBA6) == $22 && read1($83DBA7) == $D5 && read1($83DBA8) == $A1 && read1($83DBA9) == $84
	jsl SC_MetalWingInit

org $84FB00
SC_BattonGate:			; C=1: this Batton Bone's roost is empty
	php
	sep #$20
	pha
	jsl SC_Altered
	bcc .no
	lda.l $7E1F7A
	cmp #$03
	bne .no
	jsl SC_BattonIsDead
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

SC_MetalWingInit:
	jsl SC_Altered
	bcc .orig
	lda.l $7E1F7A		; A is free here ($84:A1D5 starts with REP / loads)
	cmp #$03
	bne .orig
	jsl SC_MetalWingIsDead
	bcc .orig
	pla			; drop our JSL return (3 bytes, M=1)
	pla
	pla
	jml $828387		; decline; RTL returns to the actor dispatcher
.orig:
	jml $84A1D5		; replaced call; its RTL returns to $83:DBAA
