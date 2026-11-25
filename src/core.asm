; ---------------------------------------------------------------------------
; SC_Altered: is the current stage in its SYSTEM CRASH altered state?
;   In : any M/X width, any DB/DP.
;   Out: carry set = altered. A, X, Y, DB, DP and every other flag preserved.
;   Only the five NEW links are answered here; the three retail links keep
;   their own retail code. Stage IDs 09+ (Sigma) and 00 (Highway) never match:
;   that is the Sigma firewall.
; Source flag = bit 6 of the defeated boss's weapon byte ($7E:1F88 + 2*(id-1)).
;
;   stage 07 Boomer Kuwanger   <- Spark Mandrill   ($1F92)  Grid Down
;   stage 05 Storm Eagle       <- Boomer Kuwanger  ($1F94)  Radar Down
;   stage 01 Launch Octopus    <- Armored Armadillo($1F8C)  Empty Arsenal
;   stage 03 Armored Armadillo <- Sting Chameleon  ($1F8A)  Ambush Called Off
;   stage 08 Chill Penguin     <- Flame Mammoth    ($1F8E)  Meltdown
; ---------------------------------------------------------------------------
org $84F200
SC_Altered:
	php
	sep #$20		; 8-bit A only; X/Y untouched
	pha
	lda.l $7E1F7A
	cmp #$07
	beq .s07
	cmp #$05
	beq .s05
	cmp #$01
	beq .s01
	cmp #$03
	beq .s03
	cmp #$08
	beq .s08
	bra .no
.s07:	lda.l $7E1F92
	bra .test
.s05:	lda.l $7E1F94
	bra .test
.s01:	lda.l $7E1F8C
	bra .test
.s03:	lda.l $7E1F8A
	bra .test
.s08:	lda.l $7E1F8E
.test:
	and #$40
	beq .no
	pla
	plp
	sec
	rtl
.no:
	pla
	plp
	clc
	rtl

; ---------------------------------------------------------------------------
; Palette-bank hook. $80:B4E7 builds the dynamic-palette slot index in $02
; (+$0A for the retail Mammoth/Mandrill alternates), then at $80:B512 reads
; $1F0A. For a new altered stage we set $02 so that
;   $86:A260 + L1(stage) + $1F0A*2 + $02  lands on our own slot table.
; Entry state at $80:B512 (verified): M=0, X=0, DP=$0000. A and X are dead
; here (A reloaded by the replaced instruction, X set at $80:B547).
; ---------------------------------------------------------------------------
SC_PalHook:
	lda.l $7E1F7A		; quick exit for every stage without a new palette (A is dead here)
	and #$00FF
	cmp #$0007
	beq .check
	cmp #$0005
	beq .check
	cmp #$0001
	bne .orig
.check:
	jsl SC_Altered
	bcc .orig
	lda.l $7E1F7A
	and #$00FF
	cmp #$0007
	beq .kuw
	cmp #$0005
	beq .eagle
	cmp #$0001
	beq .octo
	bra .orig
.kuw:	lda.w #(SC_KuwSlots&$FFFF)-$A260-$006A
	bra .set
.eagle:	lda.w #(SC_EagleSlots&$FFFF)-$A260-$004C
	bra .set
.octo:	lda.w #(SC_OctoSlots&$FFFF)-$A260-$0022
.set:
	sta $02
.orig:
	lda.l $7E1F0A		; replaced: LDA $1F0A
	and #$00FF		; replaced: AND #$00FF
	rtl
	assert pc() <= $84F300, "code overlaps the next block"

org $80B512
	%assert_bytes($80B512, $AD, $0A, $1F)
	assert read1($80B515) == $29
	assert read2($80B516) == $00FF
	jsl SC_PalHook
	nop
	nop

; L1 offsets the hook depends on
assert read2($86A26E) == $006A		; stage 07
assert read2($86A26A) == $004C		; stage 05
assert read2($86A262) == $0022		; stage 01

; ---------------------------------------------------------------------------
; Post-load hook. The level loader $80:BAC1 stores the map-table pointer at
; $0B95-$0B97 and the collision pointer at $0B92-$0B94, expands every scene
; into the WRAM blockMap at $7E:2000 (JSR $BB54), then runs the retail stage
; reactions (JSR $BC5C). We run right after the retail reactions, on every
; load path they run on (stage entry, checkpoint reload, death).
; Entry at $80:BB0F (verified): M=0, X=0; the caller does SEP #$30 next and
; reloads A/X itself, so A/X/Y are free; flags are restored by PLP.
; ---------------------------------------------------------------------------
org $80BB0F
	%assert_bytes($80BB0F, $20, $5C, $BC)
	jsr CR80_PostLoad

org $80FC00
CR80_PostLoad:
	jsr $BC5C		; replaced: retail stage reactions
	jsl SC_PostLoad
	rts

macro retarget_stage(stage, name)
	cmp #<stage>
	bne ?next
	lda.w #SC_<name>Maps&$FFFF
	sta.l $7E0B95
	lda.w #SC_<name>Coll&$FFFF
	sta.l $7E0B92
	sep #$20
	lda.b #SC_<name>Maps>>16
	sta.l $7E0B97
	lda.b #SC_<name>Coll>>16
	sta.l $7E0B94
	rep #$20
	ldy #$0000		; walk (blockMap offset, new map index) pairs; long addressing only
?loop:
	tyx
	lda.l SC_<name>Retarget,x
	cmp #$FFFF
	beq ?done
	pha
	lda.l SC_<name>Retarget+2,x
	plx
	sta.l $7E2000,x
	iny
	iny
	iny
	iny
	bra ?loop
?done:
	jmp .done
?next:
endmacro

org $84F300
SC_PostLoad:			; touches only A/X/Y (free here), $0B92-$0B97 and the blockMap
	php
	rep #$30
	lda.l $7E1F7A		; quick exit for every stage without a map retarget
	and #$00FF
	cmp #$0005
	beq .check
	cmp #$0001
	beq .check
	jmp .done
.check:
	jsl SC_Altered
	bcs .altered
	jmp .done
.altered:
	lda.l $7E1F7A
	and #$00FF
	%retarget_stage($0005, Eagle)
	%retarget_stage($0001, Octo)
.done:
	plp
	rtl
	assert pc() <= $84F400, "code overlaps the next block"

; retail pointers the copies in build/gen were made from
assert read2($868E80) == $CCF0 && read1($868E82) == $98	; stage 05 maps ($86:8E71 + 5*3)
assert read2($868EEF) == $E840 && read1($868EF1) == $95	; stage 05 collision ($86:8EE0 + 5*3)

; ---------------------------------------------------------------------------
; Half-power list checks. Each returns carry set if the calling actor's spawn X
; (a DP field of the actor slot) is within 2 px of an entry in the given
; "knocked out" list (build/gen/halves.asm, derived from the retail events).
; In: any M/X, DP = actor slot. Out: C. Preserves A, X, Y, DB, DP, other flags.
; ---------------------------------------------------------------------------
macro xlisted(name, table, field)
<name>:
	pha
	phx
	php
	rep #$30
	ldx #$0000
?loop:
	lda.l <table>,x
	cmp #$FFFF
	beq ?no
	sec
	sbc <field>		; table X - actor X
	clc
	adc #$0002
	cmp #$0005		; within +-2 px (spawn code may shift X by a pixel)
	bcc ?yes
	inx
	inx
	bra ?loop
?yes:
	plp
	plx
	pla
	sec
	rtl
?no:
	plp
	plx
	pla
	clc
	rtl
endmacro

incsrc "../build/gen/halves.asm"	; org $84F800: SC_SkyClawDead, SC_BattonDead, SC_MetalWingDead

org $84FA00
%xlisted(SC_SkyClawIsDead, SC_SkyClawDead, $37)		; Sky Claw saves its spawn X in $37/$38
%xlisted(SC_BattonIsDead, SC_BattonDead, $05)		; checked at spawn (state 0), X = spawn X
%xlisted(SC_MetalWingIsDead, SC_MetalWingDead, $05)	; checked at spawn (state 0), X = spawn X
	assert pc() <= $84FB00, "code overlaps the next block"
