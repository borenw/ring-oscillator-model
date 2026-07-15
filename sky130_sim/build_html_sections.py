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

sec7 = ('<div id="repro" class="sub">7 · 🧾 Complete code to reproduce</div>\n'
        '<p>Everything needed to regenerate every curve above from scratch. Files live in '
        '<code>sky130_sim/</code>. The netlists carry a <code>__LIBPATH__</code> placeholder that '
        '<code>run.sh</code> substitutes with your local sky130 model path.</p>\n'
        + "\n".join(blocks) + f"\n{MARK1}\n")

# ---- splice into index.html ----
doc = open(INDEX).read()
# remove any previous insert (idempotent)
doc = re.sub(re.escape(MARK0) + r".*?" + re.escape(MARK1) + r"\s*", "", doc, flags=re.S)

payload = sec6 + "\n" + sec7
close = "</div></body></html>"
assert close in doc, "close marker not found"
doc = doc.replace(close, payload + close, 1)

# add index list entries after the Python-model item (idempotent-ish)
li_anchor = '<li><a href="#code">5 · 🐍 Python model source</a></li>'
extra = (li_anchor +
         '\n <li><a href="#sky130">6 · 🔬 SkyWater sky130 transistor-level simulation</a></li>'
         '\n <li><a href="#repro">7 · 🧾 Complete code to reproduce</a></li>')
if '#sky130' not in doc.split('<div class="wrap">')[0] + doc[:doc.find('id="concept"')]:
    doc = doc.replace(li_anchor, extra, 1)

open(INDEX, "w").write(doc)
print("Inserted sections 6 & 7. index.html now", len(doc), "bytes")
