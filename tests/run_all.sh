#!/bin/bash
# Full v1.0 QA run. usage: tests/run_all.sh build/<rom>.sfc  (logs to build/qa/)
ROM=$1; export CR_ROM=$ROM; mkdir -p build/qa build/matrix
for s in 1 2 3 4 5 6 7 8; do timeout 7200 python -u tests/matrix.py $s $ROM build/matrix/stage$s.json > build/matrix/stage$s.log 2>&1 & done
(
for t in test_grid_down test_grid_down_traps test_grid_down_farbeam test_grid_down_cannon test_radar_down_turrets test_radar_down_claws test_empty_arsenal test_ambush test_meltdown test_sigma; do  # each test prints its own verdict lines
  echo "== $t"; timeout 3000 python -u tests/$t.py 2>&1 | grep -v Map_; echo "   (exit ${PIPESTATUS[0]})"
done
for sb in "7 20" "5 40" "1 04"; do   # Ambush/Meltdown change nothing at load: covered by test_ambush/test_meltdown and the matrix probes
  echo "== persist $sb"; timeout 1800 python -u tests/test_persist.py $ROM $sb 2>&1 | grep -v Map_; done
echo "== parity"; timeout 3600 python -u tests/test_parity.py $ROM 2>&1 | grep -v Map_
for t in test_items; do echo "== $t"; timeout 5400 python -u tests/$t.py 2>&1 | grep -v Map_; done
for t in test_hadouken test_collision test_sweep test_traverse test_minecart test_radar_lights test_ship_lights test_bosses test_ending; do echo "== $t"; timeout 7200 python -u tests/$t.py $ROM 2>&1 | grep -v Map_; done
) > build/qa/suite.log 2>&1
wait
echo "== matrix"; grep -h "stage" build/matrix/stage*.log
cat build/qa/suite.log
