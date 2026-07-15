#!/usr/bin/env bash
# Reproduce the sky130 ring-oscillator results.
# Prereqs: ngspice, and the sky130 PDK models (via volare).
set -e
# 1) point this at your sky130 ngspice model library:
#    (installed by:  pip install volare && volare enable --pdk sky130 <version>)
LIB="${SKY130_LIB:-$HOME/.volare/volare/sky130/versions/c6d73a35f524070e85faff4a6a9eef49553ebc2b/sky130A/libs.tech/ngspice/sky130.lib.spice}"
for deck in ac_loopgain_3stage ac_loopgain_4stage tran_3stage tran_4stage; do
  sed "s|__LIBPATH__|$LIB|" "$deck.spice" > "_run_$deck.spice"
  ngspice -b "_run_$deck.spice"
done
# 4-stage AC deck is generated from the 3-stage one:
python3 - "$LIB" <<'PY'
import sys,re
lib=sys.argv[1]
s=open("ac_loopgain_3stage.spice").read().replace("__LIBPATH__",lib)
s=s.replace("Xi3 n3  n3o vdd 0 inv","Xi3 n3  n4  vdd 0 inv\nXi4 n4  n3o vdd 0 inv")
s=s.replace("ac_loopgain_3stage.txt","ac_loopgain_4stage.txt")
open("_run_ac_loopgain_4stage.spice","w").write(s)
PY
ngspice -b _run_ac_loopgain_4stage.spice
python3 plot_results.py
