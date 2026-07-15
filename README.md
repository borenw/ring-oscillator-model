# Ring Oscillator — Phase-Shift Model

An interactive, single-file model of a ring oscillator viewed through its phase-shift / loop
conditions — how an odd, net-inverting chain of delay stages sustains oscillation, and how the
loop delay sets the frequency.

**▶ Open the tool:** [`index.html`](index.html) · **Live:** https://borenw.github.io/ring-oscillator-model/

## About

Self-contained HTML (no build, no dependencies) — open `index.html` in any browser, or use the
live link above.

Key ideas explored:

- A **net-inverting** loop (odd number of inversions) has no stable static state, so it must
  oscillate; an **even** loop latches instead.
- The loop **delay sets the frequency**: `f = 1 / (2·T_loop)`.
- Regenerative gates make the loop-gain (magnitude) condition essentially free — the real
  determinants are loop **parity** and having enough **delay** for an edge to propagate.

## Run locally

```bash
git clone https://github.com/borenw/ring-oscillator-model.git
cd ring-oscillator-model
# open index.html in any browser, or serve it:
python3 -m http.server 8000    # then visit http://localhost:8000
```
