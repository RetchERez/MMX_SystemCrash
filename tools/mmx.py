"""Headless MMX test harness on the snes9x libretro core (user's ROMancer frontend)."""
import ctypes, os, sys, time
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools'))
from libretro_frontend import LibretroFrontend  # noqa: E402

CORE = Path(os.environ.get('CR_CORE', ROOT / 'tools/vendor/snes9x/snes9x_libretro.dll'))  # CR_CORE: second emulator
VANILLA = ROOT / 'rom_private/Mega Man X (USA) (Rev 1).sfc'

# weapon/defeat bytes, stage id order 1..8
WEAPON = {1: 0x1F88, 2: 0x1F8A, 3: 0x1F8C, 4: 0x1F8E, 5: 0x1F90, 6: 0x1F92, 7: 0x1F94, 8: 0x1F96}
STAGE_NAME = {0: 'Highway', 1: 'Octopus', 2: 'Chameleon', 3: 'Armadillo', 4: 'Mammoth', 5: 'Eagle', 6: 'Mandrill', 7: 'Kuwanger', 8: 'Penguin'}


class MMX:
    def __init__(self, rom=VANILLA, rt=None):
        rt = Path(rt or ROOT / 'build/runtime')
        if CORE.name != 'snes9x_libretro.dll': rt = rt.with_name(rt.name + '_' + CORE.stem)  # own SRAM dir per core
        self.fe = LibretroFrontend(CORE, save_dir=rt)
        self.fe.initialize()
        self.fe.load_game(rom)
        self._wram_ptr = self.fe.lib.retro_get_memory_data(2)
        self._wram_size = self.fe.lib.retro_get_memory_size(2)
        assert self._wram_size == 0x20000, self._wram_size
        if CORE.name != 'snes9x_libretro.dll':   # bsnes randomizes power-on WRAM; start from zero like snes9x so runs compare
            ctypes.memset(self._wram_ptr, 0, self._wram_size)

    # WRAM access, addresses as 7E:xxxx / 7F:xxxx or 0..1FFFF
    def _off(self, a):
        return a - 0x7E0000 if a >= 0x7E0000 else a

    def rb(self, a):
        return ctypes.string_at(self._wram_ptr + self._off(a), 1)[0]

    def rw(self, a):
        return int.from_bytes(ctypes.string_at(self._wram_ptr + self._off(a), 2), 'little')

    def read(self, a, n):
        return ctypes.string_at(self._wram_ptr + self._off(a), n)

    def wb(self, a, v):
        ctypes.memmove(self._wram_ptr + self._off(a), bytes([v & 0xff]), 1)

    def frames(self, n, buttons=None):
        self.fe.run_frames(n, buttons or [], release_after=True)

    def raw_frame(self):
        r = getattr(self.fe, '_raw_frame', None)
        return r[0] if r else b''

    def tap(self, b, hold=2, settle=6):
        self.fe.tap([b] if isinstance(b, str) else b, hold_frames=hold, settle_frames=settle)

    def shot(self, path):
        f = self.fe.current_frame()
        if f: f.save_png(path)
        return path

    def save(self):
        return self.fe.serialize()

    def load(self, s):
        self.fe.unserialize(s)

    def close(self):
        self.fe.close()


# ---------------- navigation (verified 2026-11-24 on vanilla Rev 1) ----------------
GRID = {1: (1, 0), 8: (2, 0), 3: (0, 1), 4: (3, 1), 5: (0, 2), 7: (3, 2), 6: (1, 3), 2: (2, 3)}
# boss mask bit (password byte $26) per stage id, from $80:F280 loop
MASK_BIT = {8: 0x80, 7: 0x40, 6: 0x20, 5: 0x10, 4: 0x08, 3: 0x04, 2: 0x02, 1: 0x01}
PW_STATE = ROOT / 'build/states/password_screen.state'


def make_password_state(m):
    """boot -> title -> PASSWORD screen; deterministic input sequence"""
    m.frames(300)
    for _ in range(5):
        m.tap('start', hold=2, settle=58)
    m.frames(500)
    m.tap('start', hold=3, settle=90)
    m.tap('down', hold=10, settle=30)
    m.tap('start', hold=3, settle=120)
    m.frames(120)
    assert m.rb(0x1E4F) == 0 and m.rb(0xD1) == 0
    return m.save()     # callers keep their own copy (no shared file: parallel tests)


def to_stage_select(m, mask, rom_bytes, pw_state=None):
    import password
    m.load(pw_state or PW_STATE.read_bytes())
    m.frames(5)
    for i, v in enumerate(password.encode(rom_bytes, mask)):
        m.wb(0x1E60 + i, v)
    m.wb(0x1E4F, 3)  # cursor on END
    m.frames(5)
    m.tap('start', hold=3, settle=1)
    for _ in range(120):
        m.frames(1)
        if (m.rb(0xD1), m.rb(0xD2), m.rb(0xD3)) == (2, 0, 1):
            break
    else:
        raise RuntimeError('password not accepted')
    m.frames(300)


def press(m, b):
    m.fe.run_frames(8, [b]); m.fe.clear_buttons(); m.frames(30)


def enter_stage(m, stage, max_frames=2400):
    x, y = GRID[stage]
    n = 0
    while m.rb(0x1E4C) != x and n < 6:
        press(m, 'right'); n += 1
    n = 0
    while m.rb(0x1E4F) != y and n < 6:
        press(m, 'down'); n += 1
    assert (m.rb(0x1E4C), m.rb(0x1E4F)) == (x, y)
    m.fe.run_frames(4, ['b']); m.fe.clear_buttons()
    for f in range(max_frames):
        m.frames(1)
        if m.rb(0xD2) == 4 and m.rb(0xD3) == 4:
            break
    else:
        raise RuntimeError(f'stage {stage} did not reach gameplay; D={m.rb(0xD1)},{m.rb(0xD2)},{m.rb(0xD3)}')
    assert m.rb(0x1F7A) == stage, (m.rb(0x1F7A), stage)
    return f


def enter_stage_at_cp(m, stage, mask, cp, rom_bytes, pw_state=None):
    """Password -> stage select -> stage, forcing checkpoint index cp during load."""
    to_stage_select(m, mask, rom_bytes, pw_state)
    x, y = GRID[stage]
    while m.rb(0x1E4C) != x:
        press(m, 'right')
    while m.rb(0x1E4F) != y:
        press(m, 'down')
    m.fe.run_frames(4, ['b']); m.fe.clear_buttons()
    for _ in range(2400):
        m.frames(1); m.wb(0x1F81, cp)
        if m.rb(0xD2) == 4 and m.rb(0xD3) == 4:
            break
    assert m.rb(0x1F7A) == stage


def enemy_ids(m, base=0x0E68, n=15):
    return [m.rb(base + i * 0x40 + 0xA) for i in range(n) if m.rb(base + i * 0x40)]
