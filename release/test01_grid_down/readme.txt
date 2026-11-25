MEGA MAN X: CHAIN REACTION
Test patch 01 - Grid Down (Boomer Kuwanger)
by RetchERezzed

THIS IS A TEST BUILD, NOT THE FINISHED HACK.
It contains one of the five new stage reactions planned for v1.0.

WHAT IT DOES
------------
Beat Spark Mandrill, then enter Boomer Kuwanger's tower.

With Mandrill's power plant gone, the Maverick grid is down and the tower
runs on emergency power:

- The tower's interior is dark (emergency lighting). The sky and the sunlit
  outside climb are unchanged.
- The Ray Trap security sensors are dead, so the Ray Traps never fire.
- The fixed Turn Cannon near the top is dead.

Everything that moves still works: the elevator, the hover platforms, and
every robot (Dodge Blasters, Mega Tortoises, Kammingers, Ladder Yadders).
Boomer Kuwanger himself is unchanged.

If Spark Mandrill has NOT been beaten, the stage is exactly the original.
Every other stage, every boss, the Sigma stages and the ending are unchanged.
The three original stage reactions (frozen factory, power-plant blackout,
flooded forest) still work as before.

Passwords work as normal: a password with Spark Mandrill beaten gives you
the Grid Down tower.

REQUIRED ROM
------------
Mega Man X (USA) (Rev 1)
Unheadered, 1,572,864 bytes
CRC32: DED53C64
SHA-1: C65216760BA99178100A10D98457CF11496C2097

The patch will refuse any other ROM. If your file is 1,573,376 bytes it has
a 512-byte copier header; remove it first.

HOW TO PATCH
------------
Use Floating IPS (Flips), Beat, or the online ROM Patcher JS:
apply chain_reaction_test01_grid_down.bps to your own Mega Man X (USA)
(Rev 1) ROM. No ROM is included with this patch.

KNOWN LIMITS OF THIS TEST BUILD
-------------------------------
- Only Grid Down is in. The other four new reactions come in later test
  patches.
- Tested in snes9x (libretro). Not yet tested on real hardware or in other
  emulators.
