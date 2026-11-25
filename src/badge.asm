; ---------------------------------------------------------------------------
; STAGE-SELECT "OFFLINE" LABEL (v1.0)
; On the stage select, every stage that a beaten Maverick has changed shows
; OFFLINE at the bottom of its portrait, in the green and navy of the screen's
; STAGE / MAP / SPEC panels. The label marks the CHANGED stage, never the
; beaten Maverick's own stage. All eight links count, the three retail ones
; included.
;
; Only while the player is browsing ($1E49 = 4; it becomes 6 the frame a stage
; is picked):
;  - tiles $C0-$C3 (VRAM word $6C00, unused on this screen) are uploaded once through
;    the game's own NMI queue ($0500, count $A3);
;  - OBJ palette 7 (palette buffer $04E0, unused on this screen) holds the
;    label colours. The row's previous contents are kept at $7F:E1E0 (row 15 of
;    the game's fade copy, idle while browsing) and put back the frame a stage is
;    picked, before the game copies the whole buffer to $7F:E000 for its fade.
;    From then on all of WRAM is as in the original game.
; ---------------------------------------------------------------------------

; Hook: the stage select's own frame loop calls the sprite builder at
; $80:A04B. That call now goes through a stub that runs the builder, then adds
; the label after the game's sprites. Gameplay never runs this code, so its
; timing is exactly the original's. After the builder: $E3 = sprites drawn this
; frame, $E4-$E6 = 0. The label is written from entry $E3 on, its high-table
; bits cleared (8x8, X < 256), and $E3 raised so the next frame's builder hides
; it as it hides any sprite that is not redrawn. M=8 X=8, D=0 at the call.
org $80A04B
	%assert_bytes($80A04B, $20, $6F, $D5)
	jsr SC_BadgeStub		; replaces JSR $D56F

org $80FC10
SC_BadgeStub:
	jsr $D56F			; the sprite builder, as before
	jsl SC_Badge
	rts
	assert pc() <= $80FC20, "stub overflows its 16 bytes"

org $B48000
SC_Badge:
	php
	phb
	sep #$20
	rep #$10
	lda #$80			; bank $80: low WRAM mirror
	pha
	plb
	lda $1E49
	cmp #$04
	beq .browse
	jsr SC_BadgeGiveBack
	bra .done
.browse:
	jsr SC_BadgeGfx
	lda $E3
	sta $E4				; append cursor (the builder leaves $E4 = 0)
	ldx #$0000			; X = 2 * (stage - 1)
.loop:
	rep #$20
	lda.l SC_BadgeSrc,x		; Y = 2 * (source Maverick - 1)
	tay
	sep #$20
	lda $1F88,y			; source Maverick's weapon byte: bit 6 = beaten
	and #$40
	beq .next
	lda $E4
	cmp #$3D			; labels stay inside entries 16-63, the range kept for give-back
	bcs .end
	jsr SC_BadgePut
.next:
	inx
	inx
	cpx #$0010
	bne .loop
.end:
	lda $E4
	sta $E3				; next frame's builder hides what it does not redraw
	stz $E4
.done:
	plb
	plp
	rtl

; four 8x8 sprites (tiles $C0-$C3) at the portrait of stage X/2+1, from entry $E4
SC_BadgePut:
	phx
	rep #$20
	lda.l SC_BadgePos,x		; low byte X, high byte Y of the left sprite
	tax
	lda #$3EC0			; tile $C0, priority 3, OBJ palette 7
.spr:
	pha
	lda $E4
	and #$007F
	asl
	asl
	tay				; Y = entry * 4
	txa
	sta $0700,y
	clc
	adc #$0008			; next sprite 8 pixels to the right
	tax
	pla
	sta $0702,y
	inc				; next tile
	pha
	lda $E4
	and #$007F
	pha				; 1 entry, 3 tile
	lsr
	lsr
	tay				; Y = high-table byte
	lda $01,s
	and #$0003
	phx
	tax
	sep #$20
	lda.l SC_HiMask,x		; clear this entry's two bits: 8x8, X bit 8 = 0
	and $0900,y
	sta $0900,y
	rep #$20
	plx
	pla
	sep #$20
	inc $E4
	rep #$20
	pla
	cmp #$3EC4
	bne .spr
	sep #$20
	plx
	rts

SC_HiMask:
	db $FC,$F3,$CF,$3F

; first browsing frame (palette row 15 not yet the label's): keep the row and the
; 8 queue bytes the tile upload will cover and sprite entries 16-63 with their
; high-table bytes (at $7F:E1E0, $7F:E1C0 + offset $7F:E1C8, $7F:E000-$7F:E0CB:
; all inside the game's 512-byte fade copy, which the game rewrites in full when
; a stage is picked), then set the label colours and queue the tiles once.
; If the queue has no room this frame, try again next frame.
SC_BadgeGfx:
	jsr SC_BadgeIsOurs
	bcc .first
.skip:
	jmp .out
.first:
	lda $00A3
	cmp #$F1			; room for one 8-byte entry
	bcs .skip
	ldx #$001E
.keep:
	rep #$20
	lda $04E0,x
	sta.l $7FE1E0,x
	lda.l SC_BadgePal,x
	sta $04E0,x
	dex
	dex
	bpl .keep
	sep #$20
	lda #$01
	sta $00A1			; NMI uploads the whole palette buffer
	rep #$20			; keep sprite entries 16-63 and their high-table bytes:
	ldx #$00BE			; the original game leaves them as they are on this screen
.oam:
	lda $0740,x
	sta.l $7FE000,x
	dex
	dex
	bpl .oam
	ldx #$000A
.hi:
	lda $0904,x
	sta.l $7FE0C0,x
	dex
	dex
	bpl .hi
	sep #$20
	lda $00A3
	rep #$20
	and #$00FF
	tax
	sta.l $7FE1C8			; queue offset of the label's entry
	lda $0500,x
	sta.l $7FE1C0
	lda $0502,x
	sta.l $7FE1C2
	lda $0504,x
	sta.l $7FE1C4
	lda $0506,x
	sta.l $7FE1C6
	sep #$20
	lda #$80
	sta $0500,x			; VMAIN: word increment
	lda.b #SC_BadgeTiles>>16
	sta $0507,x
	rep #$20
	lda #$6C00
	sta $0501,x			; VRAM word address of tile $C0
	lda #$0080
	sta $0503,x			; 128 bytes: tiles $C0-$C3
	lda.w #SC_BadgeTiles
	sta $0505,x
	txa
	clc
	adc #$0008
	sep #$20
	sta $00A3
.out:
	sep #$20
	rts

; a stage was picked: put palette row 15 back before the game copies the buffer,
; sprite entries from the game's own count to 63 (and their high-table bytes),
; and the 8 queue bytes under the label's upload if nothing has reused them
SC_BadgeGiveBack:
	jsr SC_BadgeIsOurs
	bcs .ours
	jmp .out
.ours:
	ldx #$001E
.back:
	rep #$20
	lda.l $7FE1E0,x
	sta $04E0,x
	dex
	dex
	bpl .back
	lda $E3				; sprite entries from the game's own count up to 63 back
	and #$00FF
	cmp #$0010
	bcs .from
	lda #$0010
.from:
	pha
	asl
	asl
	tax				; X = entry * 4
.ro:
	cpx #$0100
	bcs .rhi
	lda.l $7FE000-$40,x
	sta $0700,x
	inx
	inx
	bra .ro
.rhi:
	pla
	clc
	adc #$0003
	lsr
	lsr
	tax				; first high-table byte not shared with the game's own entries
.rh:
	cpx #$0010
	bcs .queue
	sep #$20
	lda.l $7FE0C0-4,x
	sta $0900,x
	rep #$20
	inx
	bra .rh
.queue:
	lda.l $7FE1C8
	tax
	lda $0501,x
	cmp #$6C00
	bne .out
	lda $0503,x
	cmp #$0080
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

incsrc "../build/gen/badge_data.asm"	; SC_BadgeTiles (128 bytes), SC_BadgePal (32 bytes)
	assert pc() <= $B48400, "badge block overflows its reserved space"
