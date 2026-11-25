; ---------------------------------------------------------------------------
; TITLE SUBTITLE: "SYSTEM CRASH" under the MEGA MAN X logo, in the gold of the
; logo's X (tools/title_art.py, our own art). Seven 16x16 sprites.
;
; Hooks sit only inside the title states that show or end the subtitle, so the
; intro, the logo fly-in and every other screen run the original code:
;  - logo complete, idle step ($80:9004, $38 = 0, $39 = 4, $3A = $16; the ® and
;    CAPCOM are up): draws it every frame; on the frame the game's attract
;    timer $D7 runs out (the demo takes over) it clears it instead
;    and on the frame START is pressed (the game leaves for the menu right after
;    this step) it clears it too, so the sprite bit goes back before the menu
;    sets it itself
;  - menu setup's sprite-builder call ($80:9259): clears it (a safety net)
;  - menu input's builder call ($80:92B6): draws it
;  - after START in the menu, the animation's builder call ($80:92E7): clears it
;
; What it uses, all of it idle on these screens and given back exactly:
;  - sprite entries 9-15 and their high-table bits (bytes $0902/$0903): never
;    used from boot to the stage select (always Y = $E0, zero bytes, zero bits);
;    cleared back to that state
;  - OBJ palette 7 ($04E0, zero on these screens), set back to zero
;  - on the logo screen only, the main-screen sprite bit ($00C0 bit 4; the game
;    keeps sprites off there): switched on while the subtitle shows and off
;    again when it clears, with entry 8's tile byte as the note that it did
;  - sprite tiles $C0-$CD / $D0-$DD (VRAM words $6C00 / $6D00, empty here; no
;    background reads that range), uploaded once through the game's NMI queue
;    ($0500, count $A3); the 16 queue bytes under the upload are kept in sprite
;    entries 0-5 (idle too, Y left at $E0) and put back when it clears
; Gameplay never runs this loop.
; ---------------------------------------------------------------------------

org $809004
	%assert_bytes($809004, $C2, $20, $C6)
	assert read1($809007) == $D7, "original byte mismatch at $809007"
	jsl SC_LogoIdle			; replaces REP #$20 / DEC $D7

org $809259
	%assert_bytes($809259, $20, $6F, $D5)
	jsr SC_TitleHideStub		; menu setup: JSR $D56F
org $8092B6
	%assert_bytes($8092B6, $20, $6F, $D5)
	jsr SC_TitleShowStub		; menu input: JSR $D56F
org $8092E7
	%assert_bytes($8092E7, $20, $6F, $D5)
	jsr SC_TitleHideStub		; after START: JSR $D56F

org $80FF20
SC_TitleHideStub:
	jsl SC_TitleHide
	jmp $D56F			; the sprite builder, as before
SC_TitleShowStub:
	jsl SC_TitleShow
	jmp $D56F
	assert pc() <= $80FF30, "title stubs overflow"

org $BF8000
; logo idle step. Runs the replaced REP #$20 / DEC $D7 and returns with M = 16,
; X = 8 and Z from the timer, as the original BNE expects.
SC_LogoIdle:
	rep #$20
	dec $D7				; replaced: the attract timer
	beq .expire
	sep #$20
	rep #$10
	lda.l $7E00AC			; START just pressed: the game leaves for the menu in
	bit #$10			; this frame ($80:8C6D, after this step), so give
	bne .leave			; everything back now, sprite bit included
	lda.l $7E00C0			; sprites are off on this screen ($C0 = $07): switch
	bit #$10			; them on, noting it in entry 8's tile byte (entry 8
	bne .show			; is idle too) so the clear can undo exactly that
	ora #$10
	sta.l $7E00C0
	lda #$01
	sta.l $7E0722
.show:
	jsr SC_TitleDraw
	bra .ret
.expire:
	sep #$20
	rep #$10
.leave:
	jsr SC_TitleClear
.ret:
	rep #$20
	sep #$10
	lda $D7				; Z = timer ran out, for the original BNE
	rtl

SC_TitleShow:
	php
	sep #$20
	rep #$10
	jsr SC_TitleDraw
	plp
	rtl

SC_TitleHide:
	php
	sep #$20
	rep #$10
	jsr SC_TitleClear
	plp
	rtl

; Draws once: on the first frame (entry 9 not yet the subtitle's) it sets the
; palette, queues the tiles and writes the sprites; while it stays up nothing
; changes, so later frames return at once. The 16 queue bytes the upload covers
; are kept in the X, tile and attribute bytes of sprite entries 0-5 (idle, like
; 9-15; their Y stays $E0, off screen) with the queue offset in entry 5's tile
; byte, and put back by the clear.
SC_TitleDraw:
	lda.l $7E0727			; already up?
	cmp #$3E
	bne .first
	rts
.first:
	lda.l $7E00A3
	cmp #$E1			; room for two 8-byte queue entries
	bcc .room
	rts				; queue full this frame: try again next frame
.room:
	ldx #$001E			; OBJ palette 7
	ldy #$0000
.pal:
	rep #$20
	lda.l SC_TitlePal,x
	cmp.l $7E04E0,x
	beq .same
	sta.l $7E04E0,x
	ldy #$0001
.same:
	dex
	dex
	bpl .pal
	sep #$20
	cpy #$0000
	beq .tiles
	lda #$01
	sta.l $7E00A1			; NMI uploads the whole palette buffer
.tiles:
	lda.l $7E00A3
	sta.l $7E0716			; queue offset, in entry 5's tile byte
	rep #$20
	and #$00FF
	tax
	sep #$20			; keep the 16 queue bytes the upload covers in the X,
				; tile and attribute bytes of entries 0-5 (Y stays $E0)
	lda.l $7E0500,x
	sta.l $7E0700
	lda.l $7E0501,x
	sta.l $7E0702
	lda.l $7E0502,x
	sta.l $7E0703
	lda.l $7E0503,x
	sta.l $7E0704
	lda.l $7E0504,x
	sta.l $7E0706
	lda.l $7E0505,x
	sta.l $7E0707
	lda.l $7E0506,x
	sta.l $7E0708
	lda.l $7E0507,x
	sta.l $7E070A
	lda.l $7E0508,x
	sta.l $7E070B
	lda.l $7E0509,x
	sta.l $7E070C
	lda.l $7E050A,x
	sta.l $7E070E
	lda.l $7E050B,x
	sta.l $7E070F
	lda.l $7E050C,x
	sta.l $7E0710
	lda.l $7E050D,x
	sta.l $7E0712
	lda.l $7E050E,x
	sta.l $7E0713
	lda.l $7E050F,x
	sta.l $7E0714
	sep #$20
	lda #$80
	sta.l $7E0500,x
	sta.l $7E0508,x
	lda.b #SC_TitleTiles>>16
	sta.l $7E0507,x
	sta.l $7E050F,x
	rep #$20
	lda #$6C00			; tiles $C0-$CD
	sta.l $7E0501,x
	lda #$6D00			; tiles $D0-$DD
	sta.l $7E0509,x
	lda #$01C0			; 14 tiles each
	sta.l $7E0503,x
	sta.l $7E050B,x
	lda.w #SC_TitleTiles
	sta.l $7E0505,x
	lda.w #SC_TitleTiles+$01C0
	sta.l $7E050D,x
	txa
	clc
	adc #$0010
	sep #$20
	sta.l $7E00A3
.sprites:
	rep #$20
	ldx #$0000			; X = 4 * n, entry 9 + n
.spr:
	txa
	asl
	asl
	clc
	adc #$7248			; x 72 + 16n, y 114
	sta.l $7E0724,x
	txa
	lsr
	clc
	adc #$3EC0			; tile $C0 + 2n, priority 3, OBJ palette 7
	sta.l $7E0726,x
	inx
	inx
	inx
	inx
	cpx #$001C
	bne .spr
	sep #$20
	lda.l $7E0902			; entries 9-11 large, X bit 8 clear (entry 8's bits kept)
	and #$03
	ora #$A8
	sta.l $7E0902
	lda #$AA			; entries 12-15 large
	sta.l $7E0903
	rts

SC_TitleClear:
	lda.l $7E0722			; sprites switched on by the subtitle: switch them off
	beq .cspr
	lda #$00
	sta.l $7E0722
	lda.l $7E00C0
	and #$EF
	sta.l $7E00C0
.cspr:
	lda.l $7E0727			; entry 9 holds the subtitle (its attributes)?
	cmp #$3E
	beq .up
	jmp .out
.up:
	rep #$20			; the 16 queue bytes back, if nothing has reused them
	lda.l $7E0716
	and #$00FF
	tax
	lda.l $7E0501,x
	cmp #$6C00
	bne .noq
	lda.l $7E0505,x
	cmp.w #SC_TitleTiles
	beq .q
.noq:
	jmp .slots
.q:
	sep #$20
	lda.l $7E0700
	sta.l $7E0500,x
	lda.l $7E0702
	sta.l $7E0501,x
	lda.l $7E0703
	sta.l $7E0502,x
	lda.l $7E0704
	sta.l $7E0503,x
	lda.l $7E0706
	sta.l $7E0504,x
	lda.l $7E0707
	sta.l $7E0505,x
	lda.l $7E0708
	sta.l $7E0506,x
	lda.l $7E070A
	sta.l $7E0507,x
	lda.l $7E070B
	sta.l $7E0508,x
	lda.l $7E070C
	sta.l $7E0509,x
	lda.l $7E070E
	sta.l $7E050A,x
	lda.l $7E070F
	sta.l $7E050B,x
	lda.l $7E0710
	sta.l $7E050C,x
	lda.l $7E0712
	sta.l $7E050D,x
	lda.l $7E0713
	sta.l $7E050E,x
	lda.l $7E0714
	sta.l $7E050F,x
	rep #$20
.slots:
	ldx #$0000			; entries 0-5 and 9-15 back to x 0, y $E0, tile 0, attr 0
.k:
	lda #$E000
	sta.l $7E0700,x
	lda #$0000
	sta.l $7E0702,x
	inx
	inx
	inx
	inx
	cpx #$0018
	bne .k
	ldx #$0000
.e:
	lda #$E000			; x 0, y $E0
	sta.l $7E0724,x
	lda #$0000			; tile 0, attributes 0
	sta.l $7E0726,x
	inx
	inx
	inx
	inx
	cpx #$001C
	bne .e
	sep #$20
	lda.l $7E0902
	and #$03
	sta.l $7E0902
	lda #$00
	sta.l $7E0903
	rep #$20
	lda.l SC_TitlePal+2		; OBJ palette 7 back to zero if it holds the subtitle
	cmp.l $7E04E2
	bne .out
	ldx #$001E
	lda #$0000
.z:
	sta.l $7E04E0,x
	dex
	dex
	bpl .z
.out:
	sep #$20
	rts

incsrc "../build/gen/title_data.asm"	; SC_TitleTiles (2 x 448 bytes), SC_TitlePal (32 bytes)
	assert pc() <= $BF8800, "title block overflows its reserved space"
