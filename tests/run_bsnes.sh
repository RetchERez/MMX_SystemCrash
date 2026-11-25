#!/bin/bash
# Second emulator: the reaction suite, items, Hadouken, Sigma and parity on bsnes-mercury (balanced) libretro.
# usage: tests/run_bsnes.sh build/<rom>.sfc   (log: build/qa/bsnes_suite.log)
ROM=$1; export SC_ROM=$ROM; export SC_CORE=tools/vendor/bsnes_mercury/bsnes_mercury_balanced_libretro.dll; mkdir -p build/qa
(
for t in test_grid_down test_grid_down_traps test_grid_down_farbeam test_grid_down_cannon test_radar_down_turrets test_radar_down_claws test_empty_arsenal test_ambush test_meltdown test_sigma test_items test_radar_lights; do
  echo "== $t"; timeout 3000 python -u tests/$t.py 2>&1 | grep -v "Map_\|\[bsnes\]"; echo "   (exit ${PIPESTATUS[0]})"
done
echo "== bosses"; timeout 3600 python -u tests/test_bosses.py $ROM 2>&1 | grep -v "Map_\|\[bsnes\]"
echo "== hadouken"; timeout 1800 python -u tests/test_hadouken.py $ROM 2>&1 | grep -v "Map_\|\[bsnes\]"
echo "== parity"; timeout 3600 python -u tests/test_parity.py $ROM 2>&1 | grep -v "Map_\|\[bsnes\]"
) > build/qa/bsnes_suite.log 2>&1
tail -5 build/qa/bsnes_suite.log
