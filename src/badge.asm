; ---------------------------------------------------------------------------
; STAGE-SELECT "OFFLINE" LABEL
; On the stage select, every stage that a beaten Maverick has changed shows
; OFFLINE at the bottom of its portrait, in the green and navy of the screen's
; STAGE / MAP / SPEC panels. The label marks the CHANGED stage, never the
; beaten Maverick's own stage. All eight links count, the three retail ones
; included.
;
; Hook: the stage-select cursor object's routine ($81:8000, object slot $0E68),
; at its JSL $8280B4 ($81:8017). That code runs every frame of the stage select,
; keeps running after a stage is picked, and never runs in gameplay, so
; gameplay timing is exactly the original's. Guarded by the stage-select mode
; bytes ($D1-$D3 = 2,0,1).
;
; Each label is two 16x16 sprites in entries 0-15 (eight labels at most). The
; sprite builder starts at entry 16 on this screen and never touches 0-15.
;
; Only while the player is browsing ($1E49 = 4; it becomes 6 the frame a stage
; is picked). On the first browsing frame the label keeps, inside the game's
; 512-byte fade copy at $7F:E000 (idle while browsing, rewritten in full by the
; game when a stage is picked):
;  - sprite entries 0-15 ($7F:E000) and high-table bytes $0900-$0903 ($7F:E040)
;  - OBJ palette 7 ($7F:E1E0), then sets the label colours
;  - the 16 upload-queue bytes its two entries cover ($7F:E1C0, offset at
;    $7F:E1D0), then queues tiles $C0-$C3 (the label) and $D0-$D3 (blank: the
;    lower halves of the 16x16 sprites) through the game's NMI queue
; The frame a stage is picked it puts every one of those back.
; ---------------------------------------------------------------------------

org $818017
	%assert_bytes($818017, $22, $B4, $80)
	assert read1($81801A) == $82, "original byte mismatch at $81801A"
	jsl SC_Badge			; replaces JSL $8280B4

org $B48000
SC_Badge:
	jsl $8280B4			; replaced, with the object's own state
	php
	phb
	phd
	rep #$20
	lda #$0000
	tcd				; D = 0
	sep #$20
	rep #$10
	lda #$80			; bank $80: low WRAM mirror
	pha
	plb
	lda $00D1
	cmp #$02
	bne .done
	lda $00D2
	bne .done
	lda $00D3
	cmp #$01
	bne .done
	rep #$20
	lda.l SC_BadgePal+2		; quick check: palette row 15 holds the label colours,
	cmp $04E2			; i.e. the label is up (it is drawn once and stays)
	sep #$20
	beq .up
	lda $1E49
	cmp #$04
	bne .done			; not browsing and nothing borrowed: nothing to do
	jsr SC_BadgeFirst		; first browsing frame: keep, set up, draw once
	jsr SC_BadgeDraw
	bra .done
.up:
	lda $1E49
	cmp #$04
	beq .done			; browsing, already drawn
	jsr SC_BadgeGiveBack		; a stage was picked: give everything back
.done:
	pld
	plb
	plp
	rtl

; once, on the first browsing frame: entries 0-15 hidden, then two sprites per
; changed stage. Nothing on this screen touches entries 0-15, so they stay drawn.
SC_BadgeDraw:
	jsr SC_BadgeIsOurs		; set up yet? (queue may have been full)
	bcs .go
	rts
.go:
	rep #$20
	ldx #$0000
.hide:
	lda #$E000			; x 0, y $E0
	sta $0700,x
	stz $0702,x
	inx
	inx
	inx
	inx
	cpx #$0040
	bne .hide
	lda #$AAAA			; entries 0-15 large (16x16), X bit 8 clear
	sta $0900
	sta $0902
	ldx #$0000			; X = 2 * (stage - 1)
	ldy #$0000			; Y = next entry * 4
.loop:
	rep #$20
	phx
	lda.l SC_BadgeSrc,x		; source Maverick's weapon byte: bit 6 = beaten
	tax
	sep #$20
	lda $1F88,x
	plx
	and #$40
	beq .next
	rep #$20
	lda.l SC_BadgePos,x		; low byte X, high byte Y
	sta $0700,y
	clc
	adc #$0010			; right half, 16 pixels on
	sta $0704,y
	lda #$3EC0			; tiles $C0/$C1 (+$D0/$D1), priority 3, OBJ palette 7
	sta $0702,y
	lda #$3EC2			; tiles $C2/$C3 (+$D2/$D3)
	sta $0706,y
	tya
	clc
	adc #$0008
	tay
.next:
	inx
	inx
	cpx #$0010
	bne .loop
	sep #$20
	rts

; first browsing frame: keep what the label borrows, then set colours and tiles
SC_BadgeFirst:
	jsr SC_BadgeIsOurs
	bcc .first
	rts
.first:
	lda $00A3
	cmp #$E1			; room for two 8-byte queue entries
	bcc .room
	rts				; try again next frame
.room:
	rep #$20
	ldx #$003E			; entries 0-15
.oam:
	lda $0700,x
	sta.l $7FE000,x
	dex
	dex
	bpl .oam
	lda $0900			; their high-table bytes
	sta.l $7FE040
	lda $0902
	sta.l $7FE042
	ldx #$001E			; OBJ palette 7
.pal:
	lda $04E0,x
	sta.l $7FE1E0,x
	lda.l SC_BadgePal,x
	sta $04E0,x
	dex
	dex
	bpl .pal
	sep #$20
	lda #$01
	sta $00A1			; NMI uploads the whole palette buffer
	lda $00A3
	sta.l $7FE1D0			; queue offset
	rep #$20
	and #$00FF
	tax
	lda $0500,x			; the 16 queue bytes the two entries cover
	sta.l $7FE1C0
	lda $0502,x
	sta.l $7FE1C2
	lda $0504,x
	sta.l $7FE1C4
	lda $0506,x
	sta.l $7FE1C6
	lda $0508,x
	sta.l $7FE1C8
	lda $050A,x
	sta.l $7FE1CA
	lda $050C,x
	sta.l $7FE1CC
	lda $050E,x
	sta.l $7FE1CE
	sep #$20
	lda #$80
	sta $0500,x			; VMAIN: word increment
	sta $0508,x
	lda.b #SC_BadgeTiles>>16
	sta $0507,x
	sta $050F,x
	rep #$20
	lda #$6C00			; tiles $C0-$C3: the label
	sta $0501,x
	lda #$6D00			; tiles $D0-$D3: blank lower halves
	sta $0509,x
	lda #$0080
	sta $0503,x
	sta $050B,x
	lda.w #SC_BadgeTiles
	sta $0505,x
	lda.w #SC_BadgeBlank
	sta $050D,x
	txa
	clc
	adc #$0010
	sep #$20
	sta $00A3
	rts

; a stage was picked: put back everything the label borrowed
SC_BadgeGiveBack:
	jsr SC_BadgeIsOurs
	bcs .ours
	rts
.ours:
	rep #$20
	ldx #$001E			; OBJ palette 7, before the game copies the buffer
.pal:
	lda.l $7FE1E0,x
	sta $04E0,x
	dex
	dex
	bpl .pal
	ldx #$003E			; entries 0-15 and their high-table bytes
.oam:
	lda.l $7FE000,x
	sta $0700,x
	dex
	dex
	bpl .oam
	lda.l $7FE040
	sta $0900
	lda.l $7FE042
	sta $0902
	lda.l $7FE1D0			; the queue bytes, if nothing has reused them
	and #$00FF
	tax
	lda $0501,x
	cmp #$6C00
	bne .out
	lda $0505,x
	cmp.w #SC_BadgeTiles
	bne .out
	lda.l $7FE1C0
	sta $0500,x
	lda.l $7FE1C2
	sta $0502,x
	lda.l $7FE1C4
	sta $0504,x
	lda.l $7FE1C6
	sta $0506,x
	lda.l $7FE1C8
	sta $0508,x
	lda.l $7FE1CA
	sta $050A,x
	lda.l $7FE1CC
	sta $050C,x
	lda.l $7FE1CE
	sta $050E,x
.out:
	sep #$20
	rts

; carry set if palette row 15 holds exactly the label colours
SC_BadgeIsOurs:
	ldx #$001E
.cmp:
	rep #$20
	lda.l SC_BadgePal,x
	cmp $04E0,x
	bne .no
	dex
	dex
	bpl .cmp
	sep #$20
	sec
	rts
.no:
	sep #$20
	clc
	rts

; stage 1..8 -> 2 * (source Maverick id - 1)
;   1 Octopus <- Armadillo(3)  2 Chameleon <- Octopus(1)  3 Armadillo <- Chameleon(2)
;   4 Mammoth <- Penguin(8)    5 Eagle <- Kuwanger(7)     6 Mandrill <- Eagle(5)
;   7 Kuwanger <- Mandrill(6)  8 Penguin <- Mammoth(4)
SC_BadgeSrc:
	dw $0004,$0000,$0002,$000E,$000C,$0008,$000A,$0006

; left sprite X, Y of each stage's label: centred on the portrait (cell = 35 + 48 * column,
; 18 + 48 * row; label 32 wide, 5 in from the cell's left edge), bottom of the portrait
SC_BadgePos:
	db 88,52	; 1 Octopus    (1,0)
	db 136,196	; 2 Chameleon  (2,3)
	db 40,100	; 3 Armadillo  (0,1)
	db 184,100	; 4 Mammoth    (3,1)
	db 40,148	; 5 Eagle      (0,2)
	db 88,196	; 6 Mandrill   (1,3)
	db 184,148	; 7 Kuwanger   (3,2)
	db 136,52	; 8 Penguin    (2,0)

SC_BadgeBlank:			; tiles $D0-$D3: transparent
	fillbyte $00 : fill 128

incsrc "../build/gen/badge_data.asm"	; SC_BadgeTiles (128 bytes), SC_BadgePal (32 bytes)
	assert pc() <= $B48400, "badge block overflows its reserved space"
