#!/usr/bin/env python3
"""
Insert Section 6 (sky130 transistor-level sim) and Section 7 (reproduce code)
into ../index.html, just before </div></body></html>, and add index entries.
Idempotent: strips any previously-inserted block first.
"""
import html, os, re, math

HERE = os.path.dirname(os.path.abspath(__file__))
INDEX = os.path.join(HERE, "..", "index.html")
MARK0 = "<!--SKY130_SIM_START-->"
MARK1 = "<!--SKY130_SIM_END-->"

# ---- CMOS inverter transistor-level schematic (SVG) ----
INV_SVG = '''<svg viewBox="0 0 300 240" xmlns="http://www.w3.org/2000/svg" style="max-width:300px">
 <style>.w{stroke:#172B4D;stroke-width:1.7;fill:none}.d{fill:#172B4D}
  .lbl{font:600 11px sans-serif;fill:#172B4D}.dev{font:600 10px monospace;fill:#0052CC}
  .sub{font:9px monospace;fill:#5E6C84}</style>
 <!-- VDD rail -->
 <line class="w" x1="70" y1="26" x2="200" y2="26"/>
 <line class="w" x1="135" y1="26" x2="135" y2="60"/>
 <text class="lbl" x="205" y="30">VDD = 1.8 V</text>
 <!-- GND -->
 <line class="w" x1="135" y1="180" x2="135" y2="212"/>
 <line class="w" x1="120" y1="212" x2="150" y2="212"/>
 <line class="w" x1="125" y1="217" x2="145" y2="217"/><line class="w" x1="130" y1="222" x2="140" y2="222"/>
 <text class="sub" x="154" y="216">GND</text>
 <!-- PMOS (top) -->
 <line class="w" x1="108" y1="60" x2="108" y2="100"/>            <!-- gate plate -->
 <line class="w" x1="122" y1="58" x2="122" y2="102"/>           <!-- channel -->
 <line class="w" x1="122" y1="62" x2="135" y2="62"/><line class="w" x1="135" y1="62" x2="135" y2="60"/> <!-- source->VDD -->
 <line class="w" x1="122" y1="98" x2="135" y2="98"/><line class="w" x1="135" y1="98" x2="135" y2="118"/> <!-- drain->OUT -->
 <circle cx="108" cy="80" r="4" fill="#fff" stroke="#172B4D" stroke-width="1.5"/> <!-- pmos bubble on gate side -->
 <polygon class="d" points="126,58 132,55 132,61"/>            <!-- source arrow (out) -->
 <text class="dev" x="146" y="70">MP</text><text class="sub" x="146" y="82">pfet_01v8</text><text class="sub" x="146" y="93">W=2µ L=0.15µ</text>
 <!-- NMOS (bottom) -->
 <line class="w" x1="108" y1="140" x2="108" y2="180"/>
 <line class="w" x1="122" y1="138" x2="122" y2="182"/>
 <line class="w" x1="122" y1="142" x2="135" y2="142"/><line class="w" x1="135" y1="142" x2="135" y2="118"/> <!-- drain->OUT -->
 <line class="w" x1="122" y1="178" x2="135" y2="178"/><line class="w" x1="135" y1="178" x2="135" y2="180"/> <!-- source->GND -->
 <polygon class="d" points="122,160 128,157 128,163"/>        <!-- nmos arrow (in) -->
 <text class="dev" x="146" y="150">MN</text><text class="sub" x="146" y="162">nfet_01v8</text><text class="sub" x="146" y="173">W=1µ L=0.15µ</text>
 <!-- IN bus to both gates -->
 <line class="w" x1="30" y1="120" x2="90" y2="120"/>
 <line class="w" x1="90" y1="120" x2="90" y2="80"/><line class="w" x1="90" y1="80" x2="104" y2="80"/>
 <line class="w" x1="90" y1="120" x2="90" y2="160"/><line class="w" x1="90" y1="160" x2="108" y2="160"/>
 <circle class="d" cx="30" cy="120" r="2.5"/><text class="lbl" x="20" y="114">IN</text>
 <!-- OUT node -->
 <line class="w" x1="135" y1="118" x2="270" y2="118"/>
 <circle class="d" cx="270" cy="118" r="2.5"/><text class="lbl" x="250" y="112">OUT</text>
</svg>'''

RING3_SVG = '''<svg viewBox="0 0 240 120" xmlns="http://www.w3.org/2000/svg" style="max-width:230px">
 <style>.w{stroke:#172B4D;stroke-width:1.6;fill:none}.t{fill:#E3FCEF;stroke:#00875A;stroke-width:1.6}.b{fill:#fff;stroke:#00875A;stroke-width:1.6}.n{font:600 9px sans-serif;fill:#5E6C84}</style>
 <path class="w" d="M12,40 H40"/><path class="w" d="M66,40 H104"/><path class="w" d="M130,40 H168"/>
 <path class="w" d="M194,40 H222 V100 H12 V40"/>
 <path d="M126,96 L118,100 L126,104 Z" fill="#172B4D"/>
 <polygon class="t" points="40,31 40,49 60,40"/><circle class="b" cx="63" cy="40" r="3"/>
 <polygon class="t" points="104,31 104,49 124,40"/><circle class="b" cx="127" cy="40" r="3"/>
 <polygon class="t" points="168,31 168,49 188,40"/><circle class="b" cx="191" cy="40" r="3"/>
 <text class="n" x="24" y="28">n1</text><text class="n" x="78" y="34">n2</text><text class="n" x="142" y="34">n3</text>
 <text x="120" y="116" text-anchor="middle" style="font:600 10px sans-serif;fill:#00875A">3 × inverter → odd ring</text>
</svg>'''

# ---- 8-inverter "4-helper" ring: correct 4-net topology (alpha,beta,gamma,delta) ----
def _inv(cx, cy, ang, color, name, nx, ny):
    return (f'<g transform="translate({cx} {cy}) rotate({ang:.1f})">'
            f'<polygon points="-11,-8 -11,8 11,0" fill="{color}22" stroke="{color}" stroke-width="1.6"/>'
            f'<circle cx="14" cy="0" r="3" fill="#fff" stroke="{color}" stroke-width="1.5"/></g>'
            f'<text x="{nx}" y="{ny}" style="font:700 9px sans-serif;fill:{color}">{name}</text>')

_N = {"al": (55, 150), "be": (215, 45), "ga": (375, 150), "de": (215, 255)}
def _ang(p, q): return math.degrees(math.atan2(q[1]-p[1], q[0]-p[0]))
def _mid(p, q): return ((p[0]+q[0])/2, (p[1]+q[1])/2)

_edges = [("al","be","#0052CC","A1"), ("be","ga","#0052CC","A2"),
          ("ga","de","#172B4D","A4"), ("de","al","#172B4D","A5")]
_p = []
# ring + diagonal wires
for s,d,c,nm in _edges:
    p,q=_N[s],_N[d]
    _p.append(f'<line x1="{p[0]}" y1="{p[1]}" x2="{q[0]}" y2="{q[1]}" stroke="#5E6C84" stroke-width="1.3"/>')
_p.append('<line x1="55" y1="150" x2="375" y2="150" stroke="#5E6C84" stroke-width="1.3"/>')
_p.append('<line x1="215" y1="45" x2="215" y2="255" stroke="#5E6C84" stroke-width="1.3"/>')
# edge (ring) inverters
for s,d,c,nm in _edges:
    m=_mid(_N[s],_N[d]); a=_ang(_N[s],_N[d])
    _p.append(_inv(m[0],m[1],a,c,nm,m[0]-8,m[1]-13))
# diagonal (helper) inverters — the 4 helpers
_p.append(_inv(150,150,0,   "#00A3BF","A3", 138,140))   # al->ga  (cyan helper)
_p.append(_inv(280,150,180, "#00875A","A3″",268,140))  # ga->al  (green)
_p.append(_inv(215,110,90,  "#FF8B00","A3′",222,110))  # be->de  (orange)
_p.append(_inv(215,195,270, "#DE350B","A3‴",222,199))  # de->be  (red)
# node dots + Greek labels
for k,(x,y) in _N.items(): _p.append(f'<circle cx="{x}" cy="{y}" r="3.5" fill="#172B4D"/>')
for t,x,y in [("α",38,155),("β",210,34),("γ",384,155),("δ",210,278)]:
    _p.append(f'<text x="{x}" y="{y}" style="font:700 14px serif;fill:#172B4D">{t}</text>')
_p.append('<text x="215" y="296" text-anchor="middle" style="font:600 10px sans-serif;fill:#00875A">'
          '4 nets · ring (A1→A2→A4→A5) + 4 helper diagonals → oscillates</text>')
RING8_SVG = ('<svg viewBox="0 0 430 310" xmlns="http://www.w3.org/2000/svg" style="max-width:430px">'
             + "".join(_p) + '</svg>')

sec6 = f'''{MARK0}
<div id="sky130" class="sub">6 · 🔬 SkyWater sky130 transistor-level simulation</div>
<p>The single-pole model above is confirmed against <b>real transistors</b>: a CMOS inverter built from
sky130 core devices (<code>sky130_fd_pr__pfet_01v8</code> / <code>nfet_01v8</code>, 1.8 V), wired into 3- and
4-stage rings and simulated in <b>ngspice</b> (tt corner, 27 °C). Every number and curve below is a live
ngspice result — the exact decks are in Section 7.</p>

<div class="rowflex">
  <aside class="schem"><h4>sky130 CMOS inverter</h4>{INV_SVG}
    <div class="cap">One stage: PMOS sized 2× the NMOS so the trip point sits near VDD/2. Each stage carries a 5 fF load.</div></aside>
  <aside class="schem"><h4>…× 3 → the ring</h4>{RING3_SVG}
    <div class="cap">Three inverters close the loop (odd). The AC test breaks the loop with a 1 MH inductor (DC-closed for bias, AC-open) and injects through a 1 MF cap.</div></aside>
</div>

<p><b>AC — open-loop loop gain (frequency &amp; phase response).</b> This replicates the §3/§4 Bode diagrams with real devices:</p>
<div class="simfig"><img src="sky130_sim/fig_ac_3stage.png" alt="sky130 3-stage ring open-loop loop gain: |T| and phase vs frequency, phase crosses 0 deg at 1.19 GHz with 45 dB gain">
  <div class="cap"><b>Odd 3-stage (§4 replica):</b> DC loop gain 66 dB; ∠T crosses 0° at <b>1.19 GHz</b>
  (red) with |T| = 45 dB (169×) ≫ 1. That is the <b>small-signal startup</b> condition — the actual
  steady-state <b>f<sub>osc</sub> = 4.36 GHz</b> (green) is ~3.7× higher. See the note below on why (and why the
  sky130 model is still correct).</div></div>
<div class="simfig"><img src="sky130_sim/fig_ac_4stage.png" alt="sky130 4-stage ring open-loop loop gain: DC phase 0 deg with 88 dB gain, positive feedback">
  <div class="cap"><b>Even 4-stage (§3 replica):</b> ∠T ≈ 0° at DC with |T| = 88 dB → a non-inverting loop = positive feedback = <b>bistable latch</b>, not an oscillator.</div></div>

<p><b>Transient — closed-loop, at the bottom.</b> Let the rings run and watch the time-domain behaviour:</p>
<div class="simfig"><img src="sky130_sim/fig_tran_3stage.png" alt="sky130 3-stage ring transient: three-phase rail-to-rail oscillation at 4.36 GHz">
  <div class="cap"><b>Odd 3-stage → sustained oscillation.</b> Three rail-to-rail waveforms 120° apart; measured <b>f<sub>osc</sub> = 4.36 GHz</b> (T = 229 ps, i.e. t<sub>d</sub> = 38 ps/stage and f<sub>osc</sub> = 1/(2·3·t<sub>d</sub>)).</div></div>

<div class="panel" style="background:#DEEBFF;border-left:3px solid #4C9AFF;padding:12px 16px;border-radius:4px;margin:14px 0">
<b>Why 1.19 GHz (small-signal) ≠ 4.36 GHz (transient) — and the sky130 model is <i>not</i> wrong.</b>
Both numbers are correct; they answer different questions.
<ul style="margin:8px 0 0;line-height:1.6">
<li><b>The loop-gain AC is a small-signal analysis, linearised at the switching threshold.</b> The DC loop
(closed through the 1 MH inductor) biases every inverter at V<sub>trip</sub> ≈ 0.87 V — verified in the .op.
There both devices are <b>saturated</b>, so the output resistance is at its maximum (r<sub>o</sub> ≈ 30 kΩ
measured), giving the <b>lowest</b> pole, f<sub>p</sub> ≈ 0.69 GHz. Three poles reach −180° at 1.73·f<sub>p</sub>
= 1.19 GHz. That is the frequency at which oscillation <i>starts from noise</i>.</li>
<li><b>The real oscillation is large-signal / slewing.</b> Once it swings rail-to-rail, each stage switches with
its devices in <b>triode</b> (R<sub>on</sub> ≈ 8 kΩ, ~4× lower than r<sub>o</sub>), so the delay is short
(t<sub>d</sub> = 38 ps) and f<sub>osc</sub> = 1/(2N·t<sub>d</sub>) = 4.36 GHz. The r<sub>o</sub>/R<sub>on</sub> ≈
4 ratio is exactly the 3.7× frequency ratio.</li>
<li><b>So it is a physics distinction, not a model error.</b> The sky130 <code>nfet_01v8</code>/<code>pfet_01v8</code>
devices are used correctly; a ring oscillator is inherently a large-signal circuit, and no single-bias
small-signal AC can predict its steady-state frequency. The delay-based f<sub>osc</sub> = 1/(2N·t<sub>d</sub>) is
the right predictor — and it matches the transient to the digit.</li>
</ul></div>
<p><b>Open-loop response of the helper cell — A1·A2 (series) ∥ A3.</b> This is the building block the 4-helper
oscillator (§7) is made of: two inverters in series, in parallel with a single helper A3 (outputs shorted, the
"phase-averaging" node). Its open-loop amplitude &amp; phase directly predict the oscillation frequency:</p>
<div class="simfig"><img src="sky130_sim/fig_openloop_A12parA3.png" alt="Open-loop amplitude and phase of A1.A2 series parallel A3: phase reaches -180 deg at 2.97 GHz, close to the 2.80 GHz transient f_osc">
  <div class="cap"><b>∠H reaches −180° at 2.97 GHz</b> (with |H| = 13 dB &gt; 0 dB) — <b>very close to the 4-helper
  oscillator's transient f<sub>osc</sub> = 2.80 GHz</b> (green line). The A12 path (2 poles) rolls off faster
  than A3 (1 pole), so the summed output swings from non-inverting at DC to fully inverting (−180°) at a finite
  frequency — that crossing is what sets where the ring built from these cells oscillates.</div></div>

<table><thead><tr><th>Ring</th><th>Parity</th><th>Small-signal startup (∠T=0°)</th><th>Loop gain there</th><th>Large-signal transient</th></tr></thead>
<tbody>
<tr><td>3-stage</td><td>odd → inverting</td><td class='num'>1.19 GHz</td><td class='num'>45 dB (169×)</td><td><b>oscillates, f<sub>osc</sub> = 4.36 GHz</b></td></tr>
<tr><td>4-stage</td><td>even → non-inverting</td><td class='num'>— (0° only at DC)</td><td class='num'>88 dB at DC</td><td><b>latches</b> (bistable)</td></tr>
</tbody></table>
'''

sec_8inv = f'''<div id="ring8" class="sub">7 · 🔁 8-inverter "4-helper" ring — a 4-net, 4-phase oscillator</div>
<p>The hand sketch's <b>"Result: 4 helpers A₃"</b> circuit is not a simple chain — it has only <b>four nets</b>
(α, β, γ, δ) wired symmetrically: a distance-1 ring <b>α→β→γ→δ→α</b> (A1, A2, A4, A5) plus four <b>helper
diagonals</b> — α→γ (A3), γ→α (A3″), β→δ (A3′), δ→β (A3‴). Every net is driven by two inverter outputs
(shorted together) and drives two — the "phase-averaging" the sketch is about. I built this exact 4-net
topology in sky130 ngspice.</p>

<div class="simfig" style="max-width:440px;margin-left:0">{RING8_SVG}
  <div class="cap" style="text-align:left">Correct topology: 4 nets, 8 inverters. Ring edges A1·A2·A4·A5 (blue/navy);
  helper diagonals A3·A3″ cross-couple α↔γ, A3′·A3‴ cross-couple β↔δ. Colors match the sketch.</div></div>

<div class="panel" style="background:#E3FCEF;border-left:3px solid #00875A;padding:12px 16px;border-radius:4px;margin:14px 0">
<b>Result: it oscillates — f<sub>osc</sub> = 2.80 GHz</b>, rail-to-rail on all four nets, ~90° apart (a 4-phase
oscillator). The mixed helper+ring paths give <i>odd</i> inversion counts (e.g. α→γ via A3 = 1, then γ→α via
A4·A5 = 2, total 3 = inverting), so the network meets the oscillation condition at a finite frequency —
<b>slower than the 3-inverter ring</b> (more stages / more delay).</p></div>

<p><b>Transient — closed loop:</b></p>
<div class="simfig"><img src="sky130_sim/fig_tran_8stage.png" alt="sky130 8-inverter 4-net ring transient: four-phase sustained oscillation at 2.80 GHz">
  <div class="cap">Four rail-to-rail waveforms v(α), v(β), v(γ), v(δ), each ~90° apart. Measured <b>f<sub>osc</sub> = 2.80 GHz</b> (T = 357 ps).</div></div>
<p><b>Frequency content — FFT of the output:</b></p>
<div class="simfig"><img src="sky130_sim/fig_spec_8stage.png" alt="sky130 8-inverter ring output spectrum: fundamental at 2.80 GHz plus harmonics">
  <div class="cap">Output spectrum: clean fundamental at <b>2.80 GHz</b> + harmonics. (A single-node loop-gain Bode isn't
  representative here — unlike the simple 3-ring, this is a <i>multiply-connected</i> network with several
  interleaved feedback loops, so the transient + spectrum are the right views. The auxiliary single-node cut
  deck is included in §8.)</div></div>

<h3 style="margin:22px 0 6px">Summary — 3-inverter vs 8-inverter (both real sky130 ngspice)</h3>
<table><thead><tr><th>Metric</th><th>3-inverter ring (§6)</th><th>8-inverter "4-helper" ring</th></tr></thead>
<tbody>
<tr><td>Topology</td><td>simple odd ring</td><td>4 nets (α,β,γ,δ): ring + 4 helper diagonals</td></tr>
<tr><td>Inverters</td><td class='num'>3</td><td class='num'>8</td></tr>
<tr><td>Transient behaviour</td><td><b>sustained oscillation</b></td><td><b>sustained oscillation</b> (4-phase)</td></tr>
<tr><td>Oscillation frequency</td><td class='num'>f<sub>osc</sub> = 4.36 GHz</td><td class='num'>f<sub>osc</sub> = 2.80 GHz</td></tr>
<tr><td>Period T</td><td class='num'>229 ps</td><td class='num'>357 ps</td></tr>
<tr><td>Output phases</td><td>3 (120° apart)</td><td>4 (~90° apart)</td></tr>
<tr><td>Verdict</td><td>✅ oscillator</td><td>✅ oscillator, ~1.6× slower</td></tr>
</tbody></table>
<p class="hint">Takeaway: the extra stages and helper diagonals lower f<sub>osc</sub> from 4.36 GHz to 2.80 GHz
(~1.6×) and turn the 3-phase ring into a symmetric <b>4-phase</b> oscillator — more inverters and more feedback
paths buy lower frequency and more output phases, at the cost of area and power.</p>
'''



# ---- Section 7: complete reproduce code, read from the actual files ----
FILES = [
    ("Environment setup (macOS / Linux)", "bash", None, '''# 1. ngspice
brew install ngspice          # macOS   (Linux: apt install ngspice)

# 2. sky130 device models via volare
pip install volare matplotlib numpy
volare enable --pdk sky130 c6d73a35f524070e85faff4a6a9eef49553ebc2b
#   -> models land in:
#   ~/.volare/volare/sky130/versions/<sha>/sky130A/libs.tech/ngspice/sky130.lib.spice

# 3. run everything (decks + plots)
cd sky130_sim
./run.sh'''),
    ("inv.spice — sky130 CMOS inverter", "spice", "inv.spice", None),
    ("ac_loopgain_3stage.spice — odd ring, open-loop AC", "spice", "ac_loopgain_3stage.spice", None),
    ("ac_openloop_A12parA3.spice — helper cell A1·A2 ∥ A3, open-loop amplitude/phase", "spice", "ac_openloop_A12parA3.spice", None),
    ("ac_loopgain_4stage.spice — even ring, open-loop AC", "spice", "ac_loopgain_4stage.spice", None),
    ("tran_3stage.spice — odd ring, transient (oscillates)", "spice", "tran_3stage.spice", None),
    ("tran_4stage.spice — even ring, transient (latches)", "spice", "tran_4stage.spice", None),
    ("tran_8stage.spice — 8-inverter 4-net ring, transient (oscillates, 2.80 GHz)", "spice", "tran_8stage.spice", None),
    ("ac_loopgain_8stage.spice — 8-inverter ring, auxiliary single-node loop-gain cut", "spice", "ac_loopgain_8stage.spice", None),
    ("plot_results.py — figures from the ngspice data", "python", "plot_results.py", None),
    ("run.sh — one-shot driver", "bash", "run.sh", None),
]

blocks = []
for title, lang, fname, inline in FILES:
    code = inline if inline is not None else open(os.path.join(HERE, fname)).read().rstrip("\n")
    esc = html.escape(code)
    blocks.append(
        f'<details class="codeblk"><summary>📄 {html.escape(title)}</summary>'
        f'<div class="body"><pre class="code">{esc}</pre></div></details>')

sec7 = ('<div id="repro" class="sub">8 · 🧾 Complete code to reproduce</div>\n'
        '<p>Everything needed to regenerate every curve above from scratch. Files live in '
        '<code>sky130_sim/</code>. The netlists carry a <code>__LIBPATH__</code> placeholder that '
        '<code>run.sh</code> substitutes with your local sky130 model path.</p>\n'
        + "\n".join(blocks))

sec_mistakes = (
    '<div id="mistakes" class="sub">9 · 🧭 Mistakes &amp; Corrections</div>\n'
    '<p>Kept honestly, in the spirit of the AI-mistakes log:</p>\n'
    '<ul style="line-height:1.7">\n'
    '<li><b>Mistake Claude made:</b> On the first pass I mis-read the "4 helpers A₃" sketch as a '
    '<b>7-node linear cascade</b> (P→Q→R→S→T→U with a feedback wire). That version has even parity, '
    'so ngspice showed it <b>latching</b> — and I reported "8-inverter ring can\'t oscillate."</li>\n'
    '<li><b>Correction Bo-Ren suggested:</b> The real circuit has only <b>4 nets — α, β, γ, δ</b>: a '
    'distance-1 ring α→β→γ→δ→α plus <b>four helper diagonals</b> (α↔γ and β↔δ cross-couples). Every net is '
    'driven by two shorted inverter outputs.</li>\n'
    '<li><b>What Claude learned:</b> With the correct 4-net topology it <b>oscillates at 2.80 GHz</b> '
    '(a 4-phase oscillator) — the mixed helper+ring paths form <i>odd</i> feedback loops. Lesson: trace the '
    'actual <b>nets and loops</b> from the drawing before assuming a linear cascade, and re-simulate the '
    'corrected netlist rather than trusting the first reading.</li>\n'
    '</ul>\n'
    f"{MARK1}\n")

# ---- splice into index.html ----
doc = open(INDEX).read()
# remove any previous insert (idempotent)
doc = re.sub(re.escape(MARK0) + r".*?" + re.escape(MARK1) + r"\s*", "", doc, flags=re.S)

payload = sec6 + "\n" + sec_8inv + "\n" + sec7 + "\n" + sec_mistakes
close = "</div></body></html>"
assert close in doc, "close marker not found"
doc = doc.replace(close, payload + close, 1)

# normalize index-list entries for the sim sections (idempotent: strip then re-add)
doc = re.sub(r'\n?\s*<li><a href="#(sky130|ring8|repro|mistakes)">[^<]*</a></li>', '', doc)
li_anchor = '<li><a href="#code">5 · 🐍 Python model source</a></li>'
extra = (li_anchor +
         '\n <li><a href="#sky130">6 · 🔬 SkyWater sky130 transistor-level simulation</a></li>'
         '\n <li><a href="#ring8">7 · 🔁 8-inverter "4-helper" ring — 4-net oscillator</a></li>'
         '\n <li><a href="#repro">8 · 🧾 Complete code to reproduce</a></li>'
         '\n <li><a href="#mistakes">9 · 🧭 Mistakes &amp; Corrections</a></li>')
doc = doc.replace(li_anchor, extra, 1)

open(INDEX, "w").write(doc)
print("Inserted sections 6 & 7. index.html now", len(doc), "bytes")
