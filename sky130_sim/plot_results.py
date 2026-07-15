#!/usr/bin/env python3
"""
Plot the sky130 ring-oscillator ngspice results.
Reads the wrdata .txt files produced by the .spice decks and writes PNGs.
Run after: ngspice -b ac_loopgain_3stage.spice  (etc.)
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BLUE, RED, GREEN, GREY = "#0052CC", "#DE350B", "#00875A", "#5E6C84"
plt.rcParams.update({"font.size": 11, "font.family": "DejaVu Sans",
                     "axes.grid": True, "grid.alpha": .35, "figure.dpi": 130})

def load(fn):
    d = np.loadtxt(fn)
    return d[:, 0], d[:, 1], d[:, 3]      # freq/time, colA, colB


# ---------- 0. Single inverter — small-signal AC amplitude & phase ----------
fs, ms, ps = load("ac_single_inverter.txt")
ps = np.unwrap(np.radians(ps)) * 180/np.pi
A0 = ms[0]
fp = np.interp(-(A0-3), -ms, fs)       # -3 dB pole
fig, (a1, a2) = plt.subplots(2, 1, figsize=(7.2, 5.2), sharex=True)
a1.semilogx(fs, ms, color=BLUE, lw=2)
a1.axhline(A0, color=GREY, ls=":", lw=1); a1.axhline(A0-3, color=GREY, ls=":", lw=1)
a1.axvline(fp, color=RED, ls="--", lw=1.2); a1.plot(fp, A0-3, "o", color=RED)
a1.annotate(f"DC gain A₀ = {A0:.0f} dB ({10**(A0/20):.0f}×)", (fs[0], A0), (fs[0]*3, A0-9),
            color=BLUE, fontsize=9)
a1.annotate(f"−3 dB @ f_p = {fp/1e9:.2f} GHz", (fp, A0-3), (fp*1.4, A0-14),
            color=RED, fontsize=9, arrowprops=dict(arrowstyle="->", color=RED))
a1.set_ylabel("|H|  amplitude  [dB]")
a1.set_title("sky130 single CMOS inverter — small-signal AC (biased at V_trip)", fontsize=11)
a2.semilogx(fs, ps, color=BLUE, lw=2)
a2.axhline(180, color=GREY, ls=":", lw=1); a2.axhline(90, color=GREY, ls=":", lw=1)
a2.axvline(fp, color=RED, ls="--", lw=1.2)
a2.annotate("180° at DC (inverting);\none pole → −90° per decade toward 90°",
            (fp, 135), (fp*1.5, 150), color=BLUE, fontsize=9,
            arrowprops=dict(arrowstyle="->", color=BLUE))
a2.set_ylabel("∠H  phase  [deg]"); a2.set_xlabel("frequency  [Hz]")
a2.set_yticks([0, 45, 90, 135, 180])
fig.tight_layout(); fig.savefig("fig_ac_single_inverter.png", bbox_inches="tight")
print(f"single inverter: A0={A0:.1f} dB, pole fp={fp/1e9:.2f} GHz, DC phase={ps[0]:.0f} deg")

# ---------- 1. AC loop gain, 3-stage (odd -> oscillates) ----------
f, mag, ph = load("ac_loopgain_3stage.txt")
ph = np.unwrap(np.radians(ph)) * 180/np.pi
# small-signal Barkhausen: phase = 0 deg (mod 360) with |T|>=1
i = np.argmin(np.abs(ph))
fx = np.interp(0, [ph[i-1], ph[i]], [f[i-1], f[i]]) if ph[i] != ph[i-1] else f[i]
mx = np.interp(fx, f, mag)

fig, (a1, a2) = plt.subplots(2, 1, figsize=(7.2, 5.4), sharex=True)
a1.semilogx(f, mag, color=BLUE, lw=2)
a1.axhline(0, color=GREY, ls=":", lw=1)
a1.axvline(fx, color=RED, ls="--", lw=1.2)
a1.plot(fx, mx, "o", color=RED)
a1.annotate(f"|T| = {mx:.0f} dB ({10**(mx/20):.0f}×)\n≫ 1  → starts",
            (fx, mx), (fx*1.4, mx+8), color=RED, fontsize=9,
            arrowprops=dict(arrowstyle="->", color=RED))
a1.axvline(4.364e9, color=GREEN, ls="-.", lw=1.2)
a1.set_ylabel("|T|  loop gain  [dB]"); a1.set_title(
    "sky130 3-stage ring — open-loop loop gain  (tt, 1.8 V, 27 °C)", fontsize=11)
a2.semilogx(f, ph, color=BLUE, lw=2)
a2.axhline(0, color=RED, ls=":", lw=1.2)
a2.axvline(fx, color=RED, ls="--", lw=1.2)
a2.axvline(4.364e9, color=GREEN, ls="-.", lw=1.2)
a2.annotate(f"∠T = 0°  @  {fx/1e9:.2f} GHz\nsmall-signal startup\n(trip-point bias, high r_o)",
            (fx, 0), (fx*0.06, 55), color=RED, fontsize=8.5,
            arrowprops=dict(arrowstyle="->", color=RED))
a2.annotate("large-signal f_osc = 4.36 GHz\n(delay-limited, from transient)",
            (4.364e9, -60), (4.8e9, -150), color=GREEN, fontsize=8.5,
            arrowprops=dict(arrowstyle="->", color=GREEN))
a2.set_ylabel("∠T  [deg]"); a2.set_xlabel("frequency  [Hz]")
a2.set_yticks([-180, -90, 0, 90, 180])
fig.tight_layout(); fig.savefig("fig_ac_3stage.png", bbox_inches="tight")
print(f"3-stage AC: small-signal phase=0 at {fx/1e9:.3f} GHz vs large-signal f_osc 4.36 GHz")

# ---------- 2. AC loop gain, 4-stage (even -> never) ----------
f4, mag4, ph4 = load("ac_loopgain_4stage.txt")
ph4 = np.unwrap(np.radians(ph4)) * 180/np.pi
fig, (a1, a2) = plt.subplots(2, 1, figsize=(7.2, 5.4), sharex=True)
a1.semilogx(f4, mag4, color=GREEN, lw=2); a1.axhline(0, color=GREY, ls=":", lw=1)
a1.plot(f4[0], mag4[0], "o", color=RED)
a1.annotate(f"DC |T| = {mag4[0]:.0f} dB", (f4[0], mag4[0]), (f4[0]*3, mag4[0]-18),
            color=RED, fontsize=9, arrowprops=dict(arrowstyle="->", color=RED))
a1.set_ylabel("|T|  [dB]"); a1.set_title(
    "sky130 4-stage ring — open-loop loop gain  (EVEN → positive feedback)", fontsize=11)
a2.semilogx(f4, ph4, color=GREEN, lw=2)
a2.axhline(0, color=RED, ls=":", lw=1.2)
a2.plot(f4[0], ph4[0], "o", color=RED)
a2.annotate("∠T ≈ 0° at DC with |T| = 88 dB\n→ NON-inverting loop = positive feedback\n"
            "→ two stable states → LATCHES (see transient)",
            (f4[0], ph4[0]), (f4[0]*3, -230), color=RED, fontsize=9,
            arrowprops=dict(arrowstyle="->", color=RED))
a2.set_ylabel("∠T  [deg]"); a2.set_xlabel("frequency  [Hz]")
fig.tight_layout(); fig.savefig("fig_ac_4stage.png", bbox_inches="tight")
print(f"4-stage AC: DC phase {ph4[0]:.0f} deg, DC |T| {mag4[0]:.0f} dB -> positive feedback / latch")

# ---------- 3. Transient, 3-stage (oscillates) ----------
t, n1, n2 = load("tran_3stage.txt")
d = np.loadtxt("tran_3stage.txt"); n3 = d[:, 5]
# period from settled rising crossings @ 0.9 V
def crossings(t, v, th=0.9):
    out = []
    for k in range(1, len(v)):
        if v[k-1] < th <= v[k]:
            out.append(t[k-1] + (th-v[k-1])*(t[k]-t[k-1])/(v[k]-v[k-1]))
    return np.array(out)
cx = crossings(t, n1); cx = cx[cx > 3e-9]
Tosc = np.mean(np.diff(cx)); fosc = 1/Tosc
fig, ax = plt.subplots(figsize=(7.4, 3.4))
ax.plot(t*1e9, n1, color=BLUE, lw=1.6, label="v(n1)")
ax.plot(t*1e9, n2, color=RED, lw=1.2, alpha=.8, label="v(n2)")
ax.plot(t*1e9, n3, color=GREEN, lw=1.6, alpha=.85, label="v(n3)")
ax.set_xlabel("time  [ns]"); ax.set_ylabel("V"); ax.set_xlim(2.0, 3.2)
ax.set_ylim(-0.2, 2.0)
ax.set_title(f"sky130 3-stage ring — transient: sustained oscillation, "
             f"f_osc = {fosc/1e9:.2f} GHz  (T = {Tosc*1e12:.0f} ps)", fontsize=11)
# annotate one period, using two settled crossings inside the 2.0-3.2 ns window
cw = cx[(cx > 2.05e-9) & (cx < 3.1e-9)]
if len(cw) >= 2:
    ax.annotate("", (cw[0]*1e9, 1.92), (cw[1]*1e9, 1.92),
                arrowprops=dict(arrowstyle="<->", color=GREY))
    ax.text((cw[0]+cw[1])/2*1e9, 1.95, f"T = {Tosc*1e12:.0f} ps",
            ha="center", va="bottom", fontsize=9, color=GREY)
ax.legend(ncol=3, fontsize=9, loc="lower center")
fig.tight_layout(); fig.savefig("fig_tran_3stage.png", bbox_inches="tight")
print(f"3-stage transient: f_osc = {fosc/1e9:.3f} GHz (T = {Tosc*1e12:.0f} ps)")

# ---------- 4. Open-loop Bode of the parallel-helper cell:  A1·A2 (series) ∥ A3 ----------
fo, mo, po = load("ac_openloop_A12parA3.txt")
po = np.unwrap(np.radians(po)) * 180/np.pi
fx = None
for i in range(1, len(fo)):
    if (po[i-1]+180)*(po[i]+180) < 0:
        fx = fo[i-1] + (-180-po[i-1])*(fo[i]-fo[i-1])/(po[i]-po[i-1])
        mx = np.interp(fx, fo, mo); break
FOSC8 = 2.80e9   # transient f_osc of the 4-helper oscillator built from these cells
fig, (a1, a2) = plt.subplots(2, 1, figsize=(7.2, 5.4), sharex=True)
a1.semilogx(fo, mo, color=BLUE, lw=2); a1.axhline(0, color=GREY, ls=":", lw=1)
a1.axvline(fx, color=RED, ls="--", lw=1.2); a1.plot(fx, mx, "o", color=RED)
a1.annotate(f"|H| = {mx:.0f} dB (>0 dB)", (fx, mx), (fx*1.5, mx+8), color=RED, fontsize=9,
            arrowprops=dict(arrowstyle="->", color=RED))
a1.set_ylabel("|H|  amplitude  [dB]")
a1.set_title("sky130 open-loop  A1·A2 (series) ∥ A3  — 3-inverter helper cell", fontsize=10.5)
a2.semilogx(fo, po, color=BLUE, lw=2)
a2.axhline(-180, color=RED, ls=":", lw=1.2); a2.axvline(fx, color=RED, ls="--", lw=1.2)
a2.axvline(FOSC8/1, color=GREEN, ls="-.", lw=1.2)
a2.annotate(f"∠H = −180°  @  {fx/1e9:.2f} GHz\n≈ 4-helper osc. f_osc = 2.80 GHz",
            (fx, -180), (fo[0]*8, -120), color=RED, fontsize=9,
            arrowprops=dict(arrowstyle="->", color=RED))
a2.set_ylabel("∠H  phase  [deg]"); a2.set_xlabel("frequency  [Hz]")
a2.set_yticks([-360, -270, -180, -90, 0])
fig.tight_layout(); fig.savefig("fig_openloop_A12parA3.png", bbox_inches="tight")
print(f"open-loop A12||A3: ∠H=-180° at {fx/1e9:.2f} GHz, |H|={mx:.1f} dB "
      f"(vs 4-helper transient f_osc 2.80 GHz)")

# ---------- 5. Transient, 8-inverter "4-helper" ring (oscillates) ----------
d = np.loadtxt("tran_8stage.txt")
t8 = d[:, 0]; v8 = [d[:, 1], d[:, 3], d[:, 5], d[:, 7]]; nm = ["α", "β", "γ", "δ"]
cx8 = crossings(t8, v8[0]); cx8 = cx8[cx8 > 3e-9]
T8 = np.mean(np.diff(cx8)); f8osc = 1/T8
fig, ax = plt.subplots(figsize=(7.4, 3.4))
cols = [BLUE, "#FF8B00", GREEN, "#6554C0"]
for k in range(4):
    ax.plot(t8*1e9, v8[k], color=cols[k], lw=1.5, label=f"v({nm[k]})")
ax.set_xlabel("time  [ns]"); ax.set_ylabel("V"); ax.set_xlim(2.0, 3.6); ax.set_ylim(-0.2, 2.0)
ax.set_title(f"sky130 8-inverter '4-helper' ring — transient: sustained oscillation, "
             f"f_osc = {f8osc/1e9:.2f} GHz  (T = {T8*1e12:.0f} ps)", fontsize=10.5)
ax.legend(ncol=4, fontsize=9, loc="lower center")
fig.tight_layout(); fig.savefig("fig_tran_8stage.png", bbox_inches="tight")
print(f"8-inv transient: OSCILLATES, f_osc = {f8osc/1e9:.3f} GHz (T = {T8*1e12:.0f} ps)")

# ---------- 6. Spectrum (FFT) of the 8-inverter oscillation ----------
# resample onto a uniform grid, take the settled window, FFT
mask = t8 > 3e-9
tu = np.linspace(t8[mask][0], t8[-1], 8192)
vu = np.interp(tu, t8, v8[0]) - np.mean(np.interp(tu, t8, v8[0]))
win = np.hanning(len(vu)); sp = np.abs(np.fft.rfft(vu*win))
fr = np.fft.rfftfreq(len(vu), tu[1]-tu[0])
sp = sp/sp.max()
fig, ax = plt.subplots(figsize=(7.4, 3.2))
ax.plot(fr/1e9, 20*np.log10(sp+1e-6), color="#6554C0", lw=1.5)
ax.axvline(f8osc/1e9, color=RED, ls="--", lw=1.2)
ax.annotate(f"f_osc = {f8osc/1e9:.2f} GHz", (f8osc/1e9, -3), (f8osc/1e9+3, -12),
            color=RED, fontsize=9, arrowprops=dict(arrowstyle="->", color=RED))
ax.set_xlim(0, 25); ax.set_ylim(-70, 5)
ax.set_xlabel("frequency  [GHz]"); ax.set_ylabel("spectrum  [dB]")
ax.set_title("sky130 8-inverter '4-helper' ring — output spectrum (FFT of v(α))", fontsize=10.5)
fig.tight_layout(); fig.savefig("fig_spec_8stage.png", bbox_inches="tight")
print(f"8-inv spectrum: fundamental at {f8osc/1e9:.2f} GHz + odd harmonics")
print("All figures written.")
