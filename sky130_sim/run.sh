#!/usr/bin/env bash
# Reproduce the sky130 ring-oscillator results.
# Prereqs: ngspice, and the sky130 PDK models (via volare).
set -e
# Point this at your sky130 ngspice model library:
#   pip install volare && volare enable --pdk sky130 <version>
LIB="${SKY130_LIB:-$HOME/.volare/volare/sky130/versions/c6d73a35f524070e85faff4a6a9eef49553ebc2b/sky130A/libs.tech/ngspice/sky130.lib.spice}"

for deck in ac_single_inverter ac_loopgain_3stage ac_loopgain_4stage ac_loopgain_8stage \
            ac_openloop_A12parA3 tran_3stage tran_4stage tran_8stage; do
  sed "s|__LIBPATH__|$LIB|" "$deck.spice" > "_run_$deck.spice"
  ngspice -b "_run_$deck.spice"
done

python3 plot_results.py
