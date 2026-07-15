#!/usr/bin/env python3
"""
Insert Section 6 (sky130 transistor-level sim) and Section 7 (reproduce code)
into ../index.html, just before </div></body></html>, and add index entries.
Idempotent: strips any previously-inserted block first.
"""
import html, os, re

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

RING8_SVG = '''<svg viewBox="0 0 470 200" xmlns="http://www.w3.org/2000/svg" style="max-width:470px">
 <style>.w{stroke:#172B4D;stroke-width:1.5;fill:none}.n{font:600 9px sans-serif;fill:#5E6C84}
  .nm{font:600 8.5px sans-serif}.box{fill:none;stroke:#C1C7D0;stroke-width:1;stroke-dasharray:3 3}</style>
 <path class="w" d="M420,60 H442 V172 H16 V60"/>
 <path d="M120,168 L112,172 L120,176 Z" fill="#172B4D"/>
 <path class="w" d="M16,60 H40"/>
 <polygon points="40,51 40,69 60,60" fill="#FFEBE6" stroke="#DE350B" stroke-width="1.6"/><circle cx="63" cy="60" r="3" fill="#fff" stroke="#DE350B" stroke-width="1.5"/>
 <text class="nm" x="40" y="46" fill="#DE350B">A3‴</text>
 <path class="w" d="M66,60 H92"/>
 <rect class="box" x="96" y="34" width="120" height="98"/>
 <path class="w" d="M92,60 H112"/>
 <polygon points="112,51 112,69 132,60" fill="#DEEBFF" stroke="#0052CC" stroke-width="1.6"/><circle cx="135" cy="60" r="3" fill="#fff" stroke="#0052CC" stroke-width="1.5"/>
 <text class="nm" x="115" y="47" fill="#0052CC">A1</text>
 <path class="w" d="M138,60 H150"/><text class="n" x="140" y="55">Q</text>
 <polygon points="150,51 150,69 170,60" fill="#DEEBFF" stroke="#0052CC" stroke-width="1.6"/><circle cx="173" cy="60" r="3" fill="#fff" stroke="#0052CC" stroke-width="1.5"/>
 <text class="nm" x="153" y="47" fill="#0052CC">A2</text>
 <path class="w" d="M176,60 H212"/>
 <path class="w" d="M100,60 V108 H120"/>
 <polygon points="120,99 120,117 140,108" fill="#DEEBFF" stroke="#00A3BF" stroke-width="1.6"/><circle cx="143" cy="108" r="3" fill="#fff" stroke="#00A3BF" stroke-width="1.5"/>
 <text class="nm" x="122" y="132" fill="#00A3BF">A3</text>
 <path class="w" d="M146,108 H208 V60"/>
 <text class="nm" x="86" y="55" fill="#5E6C84">P</text><text class="nm" x="214" y="55" fill="#5E6C84">R</text>
 <path class="w" d="M212,60 H232"/>
 <polygon points="232,51 232,69 252,60" fill="#FFF0E6" stroke="#FF8B00" stroke-width="1.6"/><circle cx="255" cy="60" r="3" fill="#fff" stroke="#FF8B00" stroke-width="1.5"/>
 <text class="nm" x="234" y="47" fill="#FF8B00">A3′</text>
 <path class="w" d="M258,60 H284"/><text class="nm" x="278" y="55" fill="#5E6C84">S</text>
 <rect class="box" x="288" y="34" width="120" height="98"/>
 <path class="w" d="M284,60 H304"/>
 <polygon points="304,51 304,69 324,60" fill="#DEEBFF" stroke="#0052CC" stroke-width="1.6"/><circle cx="327" cy="60" r="3" fill="#fff" stroke="#0052CC" stroke-width="1.5"/>
 <text class="nm" x="306" y="47" fill="#0052CC">A4</text>
 <path class="w" d="M330,60 H342"/><text class="n" x="332" y="55">T</text>
 <polygon points="342,51 342,69 362,60" fill="#DEEBFF" stroke="#0052CC" stroke-width="1.6"/><circle cx="365" cy="60" r="3" fill="#fff" stroke="#0052CC" stroke-width="1.5"/>
 <text class="nm" x="344" y="47" fill="#0052CC">A5</text>
 <path class="w" d="M368,60 H416"/>
 <path class="w" d="M292,60 V108 H312"/>
 <polygon points="312,99 312,117 332,108" fill="#E3FCEF" stroke="#00875A" stroke-width="1.6"/><circle cx="335" cy="108" r="3" fill="#fff" stroke="#00875A" stroke-width="1.5"/>
 <text class="nm" x="314" y="132" fill="#00875A">A3″</text>
 <path class="w" d="M338,108 H412 V60"/>
 <text class="nm" x="414" y="55" fill="#5E6C84">U</text>
 <text x="235" y="192" text-anchor="middle" style="font:600 10px sans-serif;fill:#DE350B">8 inverters = EVEN parity → non-inverting loop → latch</text>
</svg>'''

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
  <div class="cap"><b>Odd 3-stage (§4 replica):</b> DC loop gain 66 dB; ∠T crosses 0° (Barkhausen) at <b>1.19 GHz</b> with |T| = 45 dB (169×) ≫ 1 → the loop starts oscillating.</div></div>
<div class="simfig"><img src="sky130_sim/fig_ac_4stage.png" alt="sky130 4-stage ring open-loop loop gain: DC phase 0 deg with 88 dB gain, positive feedback">
  <div class="cap"><b>Even 4-stage (§3 replica):</b> ∠T ≈ 0° at DC with |T| = 88 dB → a non-inverting loop = positive feedback = <b>bistable latch</b>, not an oscillator.</div></div>

<p><b>Transient — closed-loop, at the bottom.</b> Let the rings run and watch the time-domain behaviour:</p>
<div class="simfig"><img src="sky130_sim/fig_tran_3stage.png" alt="sky130 3-stage ring transient: three-phase rail-to-rail oscillation at 4.36 GHz">
  <div class="cap"><b>Odd 3-stage → sustained oscillation.</b> Three rail-to-rail waveforms 120° apart; measured <b>f<sub>osc</sub> = 4.36 GHz</b> (T = 229 ps). The large-signal frequency is delay-limited, so it runs faster than the small-signal 1.19 GHz startup crossing — an honest, well-known gap between the two views.</div></div>
<div class="simfig"><img src="sky130_sim/fig_tran_4stage.png" alt="sky130 4-stage ring transient: latches to a stable state, no oscillation">
  <div class="cap"><b>Even 4-stage → latch.</b> Nodes settle to a stable alternating DC state (n1=n3=1.8 V, n2=n4=0 V) and stay there. No oscillation, exactly as the parity argument predicts.</div></div>

<table><thead><tr><th>Ring</th><th>Parity</th><th>Small-signal ∠T=0°</th><th>Loop gain there</th><th>Transient result</th></tr></thead>
<tbody>
<tr><td>3-stage</td><td>odd → inverting</td><td class='num'>1.19 GHz</td><td class='num'>45 dB (169×)</td><td><b>oscillates, f<sub>osc</sub> = 4.36 GHz</b></td></tr>
<tr><td>4-stage</td><td>even → non-inverting</td><td class='num'>— (0° only at DC)</td><td class='num'>88 dB at DC</td><td><b>latches</b> (bistable)</td></tr>
</tbody></table>
'''

sec_8inv = f'''<div id="ring8" class="sub">7 · 🔁 8-inverter "4-helper" ring — the even-parity latch</div>
<p>The hand sketch's <b>"Result: 4 helpers A₃"</b> circuit chains the helper idea into a 4-cell ring:
two 2-inverter cells (each bridged by a parallel helper) plus two single inverters — <b>8 inverters total</b>.
I built and simulated exactly this topology in sky130 ngspice. It is a clean, faithful test of what happens
when you scale the helper trick up — and the answer is a direct consequence of the page's own thesis.</p>

<div class="simfig" style="max-width:560px;margin-left:0">{RING8_SVG}
  <div class="cap" style="text-align:left">Traced topology: U→A₃‴→P→[A1·A2 ∥ helper A3]→R→A₃′→S→[A4·A5 ∥ helper A3″]→U. Both loop paths
  have an <b>even</b> inversion count (6 through the series pairs, 4 through the helpers), so at DC the loop is non-inverting.</div></div>

<div class="panel" style="background:#FFEBE6;border-left:3px solid #DE350B;padding:12px 16px;border-radius:4px;margin:14px 0">
<b>Result: it latches, it does not oscillate.</b> 8 is even → net non-inverting loop → <b>positive feedback</b>.
This is the same mechanism as the §3 four-stage ring ("356°, not enough"): an even ring would need −360° of
pole lag, reachable only at f=∞, so the DC positive feedback wins first. The 4 helpers add phase but cannot
change the loop's parity.</div>

<p><b>AC — open-loop loop gain:</b></p>
<div class="simfig"><img src="sky130_sim/fig_ac_8stage.png" alt="sky130 8-inverter ring loop gain: DC phase 0 deg, 119 dB, positive feedback">
  <div class="cap">∠T ≈ 0° at DC with <b>|T| = 119 dB</b> — even higher DC loop gain than the 4-stage ring (more stages), driving a firmer latch.</div></div>
<p><b>Transient — closed loop:</b></p>
<div class="simfig"><img src="sky130_sim/fig_tran_8stage.png" alt="sky130 8-inverter ring transient: latches to a stable DC state, no oscillation">
  <div class="cap">Seeded off the metastable point, the nodes snap to a stable DC state within ~0.4 ns and stay there — no oscillation.</div></div>

<h3 style="margin:22px 0 6px">Summary — 3-inverter vs 8-inverter (both real sky130 ngspice)</h3>
<table><thead><tr><th>Metric</th><th>3-inverter ring (§6)</th><th>8-inverter "4-helper" ring</th></tr></thead>
<tbody>
<tr><td>Inverters / parity</td><td>3 · <b>odd</b></td><td>8 · <b>even</b></td></tr>
<tr><td>Loop at DC</td><td>inverting (negative feedback)</td><td>non-inverting (positive feedback)</td></tr>
<tr><td>DC loop gain |T|</td><td class='num'>66 dB</td><td class='num'>119 dB</td></tr>
<tr><td>Small-signal ∠T = 0° crossing</td><td class='num'>1.19 GHz (Barkhausen met)</td><td class='num'>only at DC → no finite crossing</td></tr>
<tr><td>Transient behaviour</td><td><b>sustained oscillation</b></td><td><b>latches</b> to a stable DC state</td></tr>
<tr><td>Oscillation frequency</td><td class='num'>f<sub>osc</sub> = 4.36 GHz</td><td class='num'>— (none)</td></tr>
<tr><td>Verdict</td><td>✅ oscillator</td><td>❌ bistable latch</td></tr>
</tbody></table>
<p class="hint">Takeaway: the helper trick can shift <i>where</i> an <b>odd</b> ring meets Barkhausen, but it cannot make an
<b>even</b> ring oscillate — parity is set by the number of inversions around the loop, and 8 is even. To build a
slower oscillator you add an <i>odd</i> number of stages (5, 7, 9 …), not an even one.</p>
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
    ("ac_loopgain_4stage.spice — even ring, open-loop AC", "spice", "ac_loopgain_4stage.spice", None),
    ("tran_3stage.spice — odd ring, transient (oscillates)", "spice", "tran_3stage.spice", None),
    ("tran_4stage.spice — even ring, transient (latches)", "spice", "tran_4stage.spice", None),
    ("ac_loopgain_8stage.spice — 8-inverter 4-helper ring, open-loop AC", "spice", "ac_loopgain_8stage.spice", None),
    ("tran_8stage.spice — 8-inverter 4-helper ring, transient (latches)", "spice", "tran_8stage.spice", None),
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
        + "\n".join(blocks) + f"\n{MARK1}\n")

# ---- splice into index.html ----
doc = open(INDEX).read()
# remove any previous insert (idempotent)
doc = re.sub(re.escape(MARK0) + r".*?" + re.escape(MARK1) + r"\s*", "", doc, flags=re.S)

payload = sec6 + "\n" + sec_8inv + "\n" + sec7
close = "</div></body></html>"
assert close in doc, "close marker not found"
doc = doc.replace(close, payload + close, 1)

# normalize index-list entries for the sim sections (idempotent: strip then re-add)
doc = re.sub(r'\n?\s*<li><a href="#(sky130|ring8|repro)">[^<]*</a></li>', '', doc)
li_anchor = '<li><a href="#code">5 · 🐍 Python model source</a></li>'
extra = (li_anchor +
         '\n <li><a href="#sky130">6 · 🔬 SkyWater sky130 transistor-level simulation</a></li>'
         '\n <li><a href="#ring8">7 · 🔁 8-inverter "4-helper" ring — even-parity latch</a></li>'
         '\n <li><a href="#repro">8 · 🧾 Complete code to reproduce</a></li>')
doc = doc.replace(li_anchor, extra, 1)

open(INDEX, "w").write(doc)
print("Inserted sections 6 & 7. index.html now", len(doc), "bytes")
