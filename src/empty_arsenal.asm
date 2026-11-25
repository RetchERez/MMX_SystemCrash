; ---------------------------------------------------------------------------
; EMPTY ARSENAL -- Launch Octopus (stage 01) altered when Armored Armadillo is beaten.
;   1. The munition silos stand empty: the 34 silo map tiles are retargeted after
;      load to copies in spare BG row 0 (Octopus's stage shows 0 pixels of row 0),
;      loaded with row 4 where the red ordnance colours 3-5 become empty dark glass.
;      Spike-strip bases share colours 3-5 but use other tiles, so they stay red.
;   2. Mega Tortoises ($5B) are short of bombs: in two of every three volleys the
;      second hatch (animation event $0F=2) spawns nothing, so two thirds of the
;      bombs remain. The volley count is kept in the tortoise's own slot byte $3F
;      (never used by the retail actor: 0 throughout 25 measured volleys). Mega
;      Tortoises in other stages (Mandrill, Kuwanger, Sigma) are untouched.
; ---------------------------------------------------------------------------

incsrc "../build/gen/octo_data.asm"	; CR_OctoMaps/Coll/Retarget/Row0/Slots

; $87:ECF1  REP #$10 / JSL $828358 (6 bytes, M=1 X=1; reached when $0F is 1 or 2)
; -> JMP CR87_Tortoise; skip returns via RTS like the retail no-bomb path ($87:ECE3)
org $87ECF1
	%assert_bytes($87ECF1, $C2, $10, $22)
	%assert_bytes($87ECF4, $58, $83, $82)
	jmp CR87_Tortoise

org $87FF80
CR87_Tortoise:
	jsl CR_TortoiseShort
	bcs .skip		; this volley's second hatch is empty
.fire:
	rep #$10		; replaced: REP #$10
	jsl $828358		; replaced: JSL $828358 (Z feeds BNE at $87:ECF7)
	jmp $ECF7
.skip:
	rts
	assert pc() <= $87FFB0, "code overlaps the next block"

org $84FD40
CR_TortoiseShort:		; M=1 X=1, D = tortoise slot. C=1: skip this bomb
	jsl CR_Altered
	bcc .no
	lda.l $7E1F7A
	cmp #$01
	bne .no			; only Launch Octopus's stage
	lda $0F
	cmp #$01
	bne .second
	lda $3F			; first hatch: count the volley 1, 2, 0, 1, 2, 0 ...
	inc
	cmp #$03
	bcc .store
	lda #$00
.store:
	sta $3F
.no:
	clc
	rtl
.second:
	lda $3F
	beq .no			; every third volley is full
	sec
	rtl
	assert pc() <= $84FD80, "code overlaps the next block"
