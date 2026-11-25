; Mega Man X: SYSTEM CRASH -- main patch source (Asar 1.91)
; Target: Mega Man X (USA) (Rev 1), unheadered, CRC32 DED53C64.
; Every hook asserts the original Rev 1 bytes before writing.

lorom

; ---------------------------------------------------------------------------
; Free space used (verified $FF, unreferenced, 2026-11-24):
;   $84:F200-$84:FFFF  shared code
;   $B4:8000-$B4:83FF  stage-select OFFLINE label (expansion)
;   $85:B390-$85:B6FF  palette data (source bank of the palette loader is fixed $85)
;   $86:FA50-$86:FFFF  palette slot tables (indexed relative to $86:A260)
;   $87:FEE0-$87:FFFF  bank-87 stubs (reached by JSR/JMP from actor code)
;   $80:FC00-$80:FC0F  bank-80 stub for the post-load hook
;   $80:FF20-$80:FF2F  bank-80 stubs for the title subtitle
;   $BF:8000-$BF:87FF  title subtitle (expansion)
;   $B0:8000, $B1:8000 expansion (ROM grown to 2 MiB): per-stage map/collision copies
; ---------------------------------------------------------------------------

macro assert_bytes(addr, b0, b1, b2)
	assert read1(<addr>) == <b0>, "original byte mismatch at <addr>"
	assert read1(<addr>+1) == <b1>, "original byte mismatch at <addr>+1"
	assert read1(<addr>+2) == <b2>, "original byte mismatch at <addr>+2"
endmacro

macro assert_free(addr, len)
	!i #= 0
	while !i < <len>
		assert read1(<addr>+!i) == $FF, "free space not empty at <addr>"
		!i #= !i+1
	endwhile
endmacro

%assert_free($84F200, $0100)
%assert_free($85B390, $0200)
%assert_free($86FA50, $0080)
%assert_free($87FEE0, $0120)
%assert_free($84F300, $0500)
%assert_free($85B460, $0020)
%assert_free($86FAA0, $0040)
%assert_free($80FC00, $0010)
%assert_free($80FF20, $0010)
%assert_free($84F800, $0500)
%assert_free($85B480, $0100)
%assert_free($86FAE0, $0120)
%assert_free($84FD00, $0040)	; Radar Down: airport lights hook
%assert_free($84FD40, $0040)	; Empty Arsenal: volley counter
%assert_free($84FD80, $0040)	; Ambush: Batton spawn gate
%assert_free($85B4A0, $0020)	; Radar Down: row 1 with the lights off
%assert_free($B48000, $0400)	; stage-select OFFLINE label: code, tiles, palette
%assert_free($BF8000, $0800)	; title subtitle: code, tiles, palette

incsrc "core.asm"
incsrc "grid_down.asm"
incsrc "radar_down.asm"
incsrc "empty_arsenal.asm"
incsrc "ambush.asm"
incsrc "meltdown.asm"
if not(defined("SC_NO_LABEL"))
	incsrc "badge.asm"	; test baseline: build with --define SC_NO_LABEL
endif
if not(defined("SC_NO_TITLE"))
	incsrc "title.asm"	; test baseline: build with --define SC_NO_TITLE
endif
