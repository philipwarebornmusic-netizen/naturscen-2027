#!/usr/bin/env python3
"""Build Naturscen proposal C: 28 cm relative stagger between adjacent rows.

Sources remain the verified v1.4/v4.2 artifacts. The layout keeps the 2,112
chairs from alternative B, shifts alternating rows, validates every rotated
chair footprint against the red 5-degree sight boundaries, and emits v1.5
2D artifacts plus the v4.3 A/B/C comparison model.
"""

from __future__ import annotations

import csv
import html
import json
import math
import re
import subprocess
import tempfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CHROME = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
PX_PER_M = 12.5
HALF_STAGGER_PX = 1.75  # 14 cm each way; adjacent rows differ by 28 cm.
HEAD_RADIUS_M = 0.105

SOURCE_CLEAN = ROOT / "Platskarta_Naturscen_2027_UTKAST_v1.4.svg"
SOURCE_PHOTO = ROOT / "Platskarta_Naturscen_2027_FOTOKONTROLL_v1.4.svg"
SOURCE_CSV = ROOT / "Platskarta_Naturscen_2027_KAPACITET_v1.4.csv"
SOURCE_3D = ROOT / "3d" / "naturscenen_3d_sikt_v4.2.html"

STEM = "Platskarta_Naturscen_2027_FORSKJUTNA_RADER_28CM_v1.5"
OUT_CLEAN = ROOT / f"{STEM}.svg"
OUT_PHOTO = ROOT / f"{STEM}_FOTOKONTROLL.svg"
OUT_CLEAN_PNG = ROOT / f"{STEM}.png"
OUT_PHOTO_PNG = ROOT / f"{STEM}_FOTOKONTROLL.png"
OUT_PDF = ROOT / f"{STEM}.pdf"
OUT_CSV = ROOT / "Platskarta_Naturscen_2027_KAPACITET_FORSKJUTNA_RADER_28CM_v1.5.csv"
OUT_3D = ROOT / "3d" / "naturscenen_3d_sikt_v4.3.html"

SEAT_RE = re.compile(
    r'<g class="seat" data-section="([^"]+)" data-row="(\d+)" '
    r'data-seat="(\d+)" transform="translate\(([-\d.]+) ([-\d.]+)\) '
    r'rotate\(([-\d.]+)\)">'
)

# phase=+1 means odd rows +14 cm and even rows -14 cm along local row x.
# Small section base corrections retain all 2,112 B chairs inside the red
# boundaries; the largest correction is 6.8 cm.
STAGGER = {
    "mitt1": {"phase": -1, "base_px": 0.00},
    "mitt2": {"phase": -1, "base_px": 0.00},
    "gul_v": {"phase": +1, "base_px": 0.85},
    "gul_o": {"phase": +1, "base_px": 0.00},
    "bla_v": {"phase": -1, "base_px": 0.00},
    "bla_o": {"phase": +1, "base_px": -0.62},
    "tredje": {"phase": -1, "base_px": 0.00},
}

SECTION_NAMES = {
    "mitt1": "1:a parkett mitt",
    "gul_v": "1:a vänster",
    "gul_o": "1:a höger",
    "mitt2": "2:a parkett mitt",
    "bla_v": "2:a vänster",
    "bla_o": "2:a höger",
    "tredje": "3:e parkett",
}
SECTION_ORDER = ["mitt1", "gul_v", "gul_o", "mitt2", "bla_v", "bla_o", "tredje"]


def parse_seats(text: str) -> list[dict]:
    return [
        {
            "s": m.group(1),
            "r": int(m.group(2)),
            "n": int(m.group(3)),
            "x": float(m.group(4)),
            "y": float(m.group(5)),
            "a": float(m.group(6)),
        }
        for m in SEAT_RE.finditer(text)
    ]


def shift_px(seat: dict) -> float:
    config = STAGGER[seat["s"]]
    parity = 1 if seat["r"] % 2 else -1
    return config["base_px"] + config["phase"] * parity * HALF_STAGGER_PX


def shift_seat(seat: dict) -> dict:
    distance = shift_px(seat)
    angle = math.radians(seat["a"])
    shifted = dict(seat)
    shifted["x"] += distance * math.cos(angle)
    shifted["y"] += distance * math.sin(angle)
    shifted["shift_px"] = distance
    return shifted


def left_boundary(y: float) -> float:
    return 637.0 + (235.9893885717093 - 637.0) * (y - 315.7) / (930.0 - 315.7)


def right_boundary(y: float) -> float:
    return 862.0 + (1336.2934384039124 - 862.0) * (y - 315.7) / (930.0 - 315.7)


def chair_corners(seat: dict) -> list[tuple[float, float]]:
    angle = math.radians(seat["a"])
    ca, sa = math.cos(angle), math.sin(angle)
    result = []
    for local_x, local_y in ((-2.7, -2.3), (-2.7, 2.3), (2.7, -2.3), (2.7, 2.3)):
        result.append(
            (
                seat["x"] + local_x * ca - local_y * sa,
                seat["y"] + local_x * sa + local_y * ca,
            )
        )
    return result


def inside_red_boundaries(seat: dict) -> bool:
    return all(left_boundary(y) <= x <= right_boundary(y) for x, y in chair_corners(seat))


def seat_key(seat: dict) -> tuple[str, int, int]:
    return seat["s"], seat["r"], seat["n"]


def validate_layout(source: list[dict], shifted: list[dict]) -> None:
    if len(source) != 2112 or len(shifted) != 2112:
        raise ValueError(f"Expected 2,112 B/C seats, got {len(source)}/{len(shifted)}")
    source_keys = [seat_key(s) for s in source]
    shifted_keys = [seat_key(s) for s in shifted]
    if len(source_keys) != len(set(source_keys)) or source_keys != shifted_keys:
        raise ValueError("Seat identifiers are not unique and stable")
    failures = [seat_key(s) for s in shifted if not inside_red_boundaries(s)]
    if failures:
        raise ValueError(f"Shifted chair footprints outside red boundaries: {failures[:8]}")

    by_row: dict[tuple[str, int], list[dict]] = {}
    for seat in shifted:
        by_row.setdefault((seat["s"], seat["r"]), []).append(seat)
    pitches = []
    for row in by_row.values():
        row.sort(key=lambda s: s["n"])
        pitches.extend(
            math.hypot(b["x"] - a["x"], b["y"] - a["y"])
            for a, b in zip(row, row[1:])
        )
    if not pitches or abs(sorted(pitches)[len(pitches) // 2] - 7.0) > 0.001:
        raise ValueError("The normal 56 cm chair pitch changed")


def capacity_box(counts: Counter) -> str:
    rows = []
    y = 209
    for section in SECTION_ORDER:
        count = counts[section]
        rows.append(
            f'<text x="162" y="{y}" font-size="11" text-anchor="start" fill="#222">{SECTION_NAMES[section]}</text>'
            f'<text x="361" y="{y}" font-size="11" text-anchor="end" fill="#222">{count}</text>'
            f'<text x="414" y="{y}" font-size="11" text-anchor="end" fill="#222">{count}</text>'
            f'<text x="467" y="{y}" font-size="11" text-anchor="end" fill="#222">0</text>'
        )
        y += 17
    return (
        '<g id="capacity-comparison"><rect x="150" y="151" width="330" height="216" rx="5" fill="#fffef9" stroke="#b7b6aa" />'
        '<text x="162" y="170" font-size="12" font-weight="700">KAPACITET · B → C v1.5</text>'
        '<text x="162" y="190" font-size="10" text-anchor="start">Sektion</text>'
        '<text x="361" y="190" font-size="10" text-anchor="end">B</text>'
        '<text x="414" y="190" font-size="10" text-anchor="end">C</text>'
        '<text x="467" y="190" font-size="10" text-anchor="end">Skillnad</text>'
        + "".join(rows)
        + '<text x="162" y="337" font-size="12" font-weight="700" text-anchor="start">TOTALT</text>'
        '<text x="361" y="337" font-size="12" font-weight="700" text-anchor="end">2 112</text>'
        '<text x="414" y="337" font-size="12" font-weight="700" text-anchor="end">2 112</text>'
        '<text x="467" y="337" font-size="12" font-weight="700" text-anchor="end">0</text>'
        '<text x="162" y="356" font-size="10" fill="#555">28 cm relativ radförskjutning. Kapacitet oförändrad.</text></g>'
    )


def footer(counts: Counter) -> str:
    metadata = {
        "version": "1.5",
        "proposal": "C",
        "source": SOURCE_CLEAN.name,
        "method": (
            "The 2,112 chairs in B are retained. Adjacent rows differ by 28 cm along each section row axis, "
            "implemented as nominal -14/+14 cm with section base corrections no larger than 6.8 cm. "
            "Chair IDs, row depth, chair pitch, section angle and the 5-degree corner-anchored sight boundaries are retained."
        ),
        "relative_row_stagger_m": 0.28,
        "nominal_alternating_shift_m": [-0.14, 0.14],
        "section_stagger": STAGGER,
        "capacity_b": 2112,
        "capacity_c": 2112,
        "counts_c": dict(counts),
        "chair_symbol_px": [5.4, 4.6],
        "chair_pitch_m": 0.56,
        "row_depth_m": 0.92,
        "photo_px_per_m": PX_PER_M,
    }
    return (
        '<path d="M865 315.700 V330.700 M862 315.700 H868 M862 330.700 H868" fill="none" stroke="#444" stroke-width=".7" />'
        '<text x="872" y="325.5" font-size="8" fill="#333" stroke="white" stroke-width="2" paint-order="stroke">1,20 m</text>'
        '<rect x="152" y="150" width="214" height="173" rx="4" fill="#FBFAF6" stroke="#C8Bfa8" stroke-width="1" />'
        '<text x="1120" y="884" font-size="8.5" font-weight="700" fill="#6E5B33" transform="rotate(-25 1120 884)" stroke="white" stroke-width="2.4" paint-order="stroke">GRUSGÅNG ~1 m</text>'
        '<path d="M637 315.700 L235.989389 930 M862 315.700 L1336.293438 930" fill="none" stroke="#dd3028" stroke-width="2.8" stroke-dasharray="7 5" id="new-sight-boundaries" />'
        + capacity_box(counts)
        + '<text x="1440" y="113" text-anchor="end" font-size="11" font-weight="700">Förslag C v1.5</text>'
        '<text x="182" y="966" font-size="14" fill="#333" font-weight="700">FÖRSLAG C · 28 CM FÖRSKJUTNA STOLRADER</text>'
        '<text x="182" y="988" font-size="12" fill="#333">Utgångspunkt B: 2 112 platser. Förslag C: 2 112 platser. Kapacitet oförändrad.</text>'
        '<text x="182" y="1008" font-size="11" fill="#333">Varannan rad ligger 28 cm förskjuten relativt nästa rad; stolavstånd 56 cm och radavstånd 92 cm behålls.</text>'
        '<text x="182" y="1027" font-size="11" fill="#333">Röd streckad linje: 5° snävare siktgräns från scenhörnen. Alla stolsymboler ryms innanför gränsen.</text>'
        '<text x="182" y="1046" font-size="10" fill="#333">Siktförbättrande arbetsförslag, inte garanti för fri sikt eller godkänd publik-/utsättningsplan. Kontrollmätning krävs.</text>'
        f'<metadata id="geometry-source">{html.escape(json.dumps(metadata, ensure_ascii=False))}</metadata></svg>'
    )


def transform_svg(source_text: str, shifted_by_key: dict, photo: bool) -> str:
    seen = set()

    def replace_seat(match: re.Match) -> str:
        key = (match.group(1), int(match.group(2)), int(match.group(3)))
        shifted = shifted_by_key[key]
        seen.add(key)
        return (
            f'<g class="seat" data-section="{key[0]}" data-row="{key[1]}" data-seat="{key[2]}" '
            f'transform="translate({shifted["x"]:.3f} {shifted["y"]:.3f}) rotate({match.group(6)})">'
        )

    result = SEAT_RE.sub(replace_seat, source_text)
    if len(seen) != 2112:
        raise ValueError(f"Expected to transform 2,112 SVG seats, transformed {len(seen)}")

    result, n = re.subn(
        r'<text x="185" y="115"[^>]*>.*?</text>',
        '<text x="185" y="115" font-size="22" font-weight="700" fill="#222">NY PLATSKARTA 2027 · 28 cm förskjutna rader (Förslag C v1.5)</text>',
        result,
        count=1,
    )
    if n != 1:
        raise ValueError("Could not replace SVG title")
    subtitle = (
        "Fotokontroll: varannan rad är 28 cm förskjuten relativt nästa rad; alla 2 112 stolar behålls."
        if photo
        else "Varannan rad är 28 cm förskjuten relativt nästa rad (nominellt −14/+14 cm). Alla 2 112 stolar behålls."
    )
    result, n = re.subn(
        r'<text x="185" y="140"[^>]*>.*?</text>',
        f'<text x="185" y="140" font-size="13" fill="#555">{subtitle}</text>',
        result,
        count=1,
    )
    if n != 1:
        raise ValueError("Could not replace SVG subtitle")

    marker = '<path d="M865 315.700 V330.700'
    start = result.find(marker)
    if start < 0:
        raise ValueError("Could not find SVG annotation footer")
    counts = Counter(seat["s"] for seat in shifted_by_key.values())
    return result[:start] + footer(counts) + "\n"


def write_csv(source_by_key: dict, shifted_by_key: dict) -> None:
    with SOURCE_CSV.open(newline="", encoding="utf-8") as source, OUT_CSV.open("w", newline="", encoding="utf-8") as output:
        reader = csv.DictReader(source, delimiter=";")
        fields = [
            "sektion", "sida_i_kartan", "rad", "plats", "x_b_px", "y_b_px", "x_c_px", "y_c_px",
            "radvinkel_grader", "radforskjutning_cm", "status",
        ]
        writer = csv.DictWriter(output, fieldnames=fields, delimiter=";", lineterminator="\n")
        writer.writeheader()
        for row in reader:
            key = (row["sektion"], int(row["rad"]), int(row["plats"]))
            source_seat = source_by_key.get(key)
            shifted = shifted_by_key.get(key)
            if shifted:
                shift_cm = shifted["shift_px"] / PX_PER_M * 100
                writer.writerow({
                    "sektion": row["sektion"], "sida_i_kartan": row["sida_i_kartan"], "rad": row["rad"], "plats": row["plats"],
                    "x_b_px": f'{source_seat["x"]:.3f}', "y_b_px": f'{source_seat["y"]:.3f}',
                    "x_c_px": f'{shifted["x"]:.3f}', "y_c_px": f'{shifted["y"]:.3f}',
                    "radvinkel_grader": f'{shifted["a"]:.1f}', "radforskjutning_cm": f"{shift_cm:.1f}", "status": "kvar_forskjuten",
                })
            else:
                writer.writerow({
                    "sektion": row["sektion"], "sida_i_kartan": row["sida_i_kartan"], "rad": row["rad"], "plats": row["plats"],
                    "x_b_px": row["x_px"], "y_b_px": row["y_px"], "x_c_px": "", "y_c_px": "",
                    "radvinkel_grader": row["radvinkel_grader"], "radforskjutning_cm": "", "status": "bort_siktgrans",
                })


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if text.count(old) != 1:
        raise ValueError(f"Expected one {label} occurrence, found {text.count(old)}")
    return text.replace(old, new, 1)


def to_sweref(seat: dict) -> dict:
    return {
        "s": seat["s"], "r": seat["r"], "n": seat["n"],
        "E": round(472510.0 - (seat["x"] - 749.5) / PX_PER_M, 6),
        "N": round(6399861.0 + (seat["y"] - 315.7) / PX_PER_M, 6),
    }


def build_3d(shifted: list[dict]) -> None:
    text = SOURCE_3D.read_text(encoding="utf-8")
    alt_match = re.search(r"const ALTERNATIVES = (\{.*\});\n", text)
    if not alt_match:
        raise ValueError("Could not parse v4.2 alternatives")
    alternatives = json.loads(alt_match.group(1))
    alternatives["staggered"] = [to_sweref(seat) for seat in shifted]
    text = text[: alt_match.start()] + "const ALTERNATIVES = " + json.dumps(alternatives, separators=(",", ":")) + ";\n" + text[alt_match.end() :]

    replacements = [
        ("<title>Naturscen · 3D siktverktyg v4.2</title>", "<title>Naturscen · 3D siktverktyg v4.3</title>", "3D title"),
        ('<div class="sub">3D siktverktyg · v4.2</div>', '<div class="sub">3D siktverktyg · v4.3</div>', "3D header"),
        ("<h2>Jämför alternativ · v4.2</h2>", "<h2>Jämför alternativ · v4.3</h2>", "comparison heading"),
        ('<button data-alt="inward" aria-pressed="false">B · Siktlinje 2</button>', '<button data-alt="inward" aria-pressed="false">B · Siktlinje 2</button>\n      <button data-alt="staggered" aria-pressed="false">C · Förskjutna rader</button>', "C button"),
        ("A: original, 2 353 valbara stolar med gammal yttergräns förankrad i scenhörnen. B: 5° snävare från samma hörn, 2 112 valbara stolar. Välj en stol och tryck ”Sitt i stolen”. Platsval sparas separat för A och B.", "A: 2 353 originalstolar. B: 2 112 stolar innanför den 5° snävare gränsen. C: samma 2 112 platser med 28 cm relativ förskjutning mellan intilliggande rader. Platsval sparas separat för A, B och C.", "alternative help"),
        ('<a style="color:var(--accent)" href="../Platskarta_Naturscen_2027_ALTERNATIV_HORNFIX_5GRADER_v1.4.pdf" target="_blank" rel="noopener">5° snävare hörnfix · 2 112 platser</a>', '<a style="color:var(--accent)" href="../Platskarta_Naturscen_2027_ALTERNATIV_HORNFIX_5GRADER_v1.4.pdf" target="_blank" rel="noopener">5° snävare hörnfix · 2 112 platser</a><br>\n      <a style="color:var(--accent)" href="../Platskarta_Naturscen_2027_FORSKJUTNA_RADER_28CM_v1.5.pdf" target="_blank" rel="noopener">Förslag C · 28 cm förskjutna rader · 2 112 platser</a>', "C PDF link"),
        ('<div class="stat"><span class="k">Fri höjd över framförvarande</span><span class="v" id="sHead">–</span></div>', '<div class="stat"><span class="k">Minsta avstånd till huvud</span><span class="v" id="sHead">–</span></div>\n      <div class="stat"><span class="k">Fria scenmål</span><span class="v" id="sTargets">–</span></div>', "sight stats"),
        ('const alternativeSelection={original:null,inward:null};', 'const alternativeSelection={original:null,inward:null,staggered:null};\nconst ALT_LABELS={original:"A: 2 353 stolar · gammal yttergräns från scenhörn",inward:"B: 2 112 stolar · 5° snävare från scenhörn (241 färre)",staggered:"C: 2 112 stolar · 28 cm förskjutna rader"};', "alternative state"),
        ("document.getElementById('alternativeReadout').textContent=next==='original'?'A: 2 353 stolar · gammal yttergräns från scenhörn':'B: 2 112 stolar · 5° snävare från scenhörn (241 färre)' ;", "document.getElementById('alternativeReadout').textContent=ALT_LABELS[next];", "alternative readout"),
        ("['sStol','sPos','sDist','sGround','sElev','sHead']", "['sStol','sPos','sDist','sGround','sElev','sHead','sTargets']", "clear stats"),
    ]
    for old, new, label in replacements:
        text = replace_once(text, old, new, label)

    old_compute = re.search(r"function computeSight\(\)\{.*?\n\}\n\nfunction drawProfile", text, flags=re.S)
    if not old_compute:
        raise ValueError("Could not find computeSight in v4.2")
    new_compute = r'''const HEAD_RADIUS=0.105,SIGHT_MARGIN=0.05;
function sightToTarget(st,eyeZ,tgt,samples,collect){
  const dE=tgt.E-st.E,dN=tgt.N-st.N,dZ=tgt.Z-eyeZ,D=Math.hypot(dE,dN),L=Math.hypot(D,dZ);
  const uE=dE/L,uN=dN/L,uZ=dZ/L;
  let minC=Infinity,worstD=0,worstKind='',headMin=Infinity,headD=0;const prof=[],heads=[];
  for(let k=0;k<=samples;k++){const t=k/samples,E=st.E+dE*t,N=st.N+dN*t,g=(k===0)?amfiZ(st.E,st.N,st.s):amfiZ(E,N),sz=eyeZ+dZ*t;if(collect)prof.push({d:D*t,ground:g,sight:sz});if(k>0&&k<samples){const c=sz-g;if(c<minC){minC=c;worstD=D*t;worstKind='mark';}}}
  for(let j=0;j<SEATS.length;j++){
    if(j===selIdx)continue;const o=SEATS[j],oGround=amfiZ(o.E,o.N,o.s),hZ=oGround+headHeight-HEAD_RADIUS;
    const wE=o.E-st.E,wN=o.N-st.N,wZ=hZ-eyeZ,along=wE*uE+wN*uN+wZ*uZ;
    if(along<=0.35||along>=L-0.15)continue;
    const qE=wE-uE*along,qN=wN-uN*along,qZ=wZ-uZ*along,clearance=Math.hypot(qE,qN,qZ)-HEAD_RADIUS;
    if(clearance<headMin){headMin=clearance;headD=along*D/L;}
    if(collect){const planAlong=wE*dE/D+wN*dN/D,planLat=Math.abs(-wE*dN/D+wN*dE/D);if(planAlong>0&&planAlong<D&&planLat<0.32)heads.push({d:planAlong,z:hZ+HEAD_RADIUS});}
  }
  if(headMin<minC){minC=headMin;worstD=headD;worstKind='huvud framför';}
  return {minC,worstD,worstKind,headMin,prof,heads,D};
}
function stageTargets(){const c=targetReal(),targets=[];for(const offset of [-8,-6,-4,-2,0,2,4,6,8])targets.push({E:STAGE.E+offset,N:c.N,Z:c.Z});return targets;}
function computeSight(){ if(selIdx<0)return; const st=SEATS[selIdx]; const gz=amfiZ(st.E,st.N,st.s); const eyeZ=gz+eyeHeight; const tgt=targetReal();
  const result=sightToTarget(st,eyeZ,tgt,90,true),minC=result.minC;
  let clearTargets=0;for(const targetPoint of stageTargets()){if(sightToTarget(st,eyeZ,targetPoint,45,false).minC>SIGHT_MARGIN)clearTargets++;}
  document.getElementById('sStol').textContent=SECMETA[st.s].name+' · rad '+st.r+' · plats '+st.n;
  document.getElementById('sPos').textContent='N '+Math.round(st.N)+' · E '+Math.round(st.E);
  document.getElementById('sDist').textContent=result.D.toFixed(1)+' m';
  document.getElementById('sGround').textContent=gz.toFixed(1)+' m ö.h.';
  const deckTop=stageRef.groundZ+stageDeckH; document.getElementById('sElev').textContent=((gz-deckTop>=0?'+':'')+(gz-deckTop).toFixed(2))+' m';
  document.getElementById('sHead').textContent=(result.headMin===Infinity?'—':(result.headMin>=0?'+':'')+result.headMin.toFixed(2)+' m');
  document.getElementById('sTargets').textContent=clearTargets+' av 9';
  const v=document.getElementById('verdict');
  if(minC>SIGHT_MARGIN){v.className='clear';v.textContent='Fri sikt mot scenmitt · marginal '+minC.toFixed(2)+' m';}
  else{v.className='blocked';v.textContent='Skymd sikt mot scenmitt ('+result.worstKind+') · underskott '+Math.max(0,SIGHT_MARGIN-minC).toFixed(2)+' m';}
  if(sightLine)scene.remove(sightLine); const c=seatCache[selIdx]; const ts=currentTargetScene();
  const pts=[new THREE.Vector3(c.x,sceneY(eyeZ),c.z),ts]; const lg=new THREE.BufferGeometry().setFromPoints(pts);
  sightLine=new THREE.Line(lg,new THREE.LineBasicMaterial({color:minC>SIGHT_MARGIN?0x6fbf7a:0xe07a4a})); scene.add(sightLine);
  drawProfile(result.prof,result.heads,eyeZ,tgt.Z,result.D);
  document.getElementById('profEmpty').style.display='none';
}

function drawProfile'''
    text = text[: old_compute.start()] + new_compute + text[old_compute.end() :]
    OUT_3D.write_text(text, encoding="utf-8")


def sight_analysis_page() -> str:
    """Return the documented v4.3 comparison used as PDF page 3."""
    return """<div class="page analysis">
<header><div><p class="kicker">FÖRSLAG C · DOKUMENTERAD SIKTANALYS</p><h1>Blir sikten bättre med förskjutna rader?</h1></div><div class="version">v1.5 / 3D v4.3</div></header>
<section class="answer"><strong>Ja, i modellens standardscenario.</strong> Förskjutningen förbättrar den samlade sikten, särskilt mot scenmitt. Den förbättrar däremot inte varje plats och är ingen garanti när personhöjder eller vertikala förutsättningar ändras.</section>
<div class="metrics">
<section class="metric"><p>FRI SIKT MOT SCENMITT</p><div><span>B&nbsp; 1 201 <small>56,9 %</small></span><b>→</b><strong>C&nbsp; 1 360 <small>64,4 %</small></strong></div><em>+159 platser · +7,5 procentenheter</em></section>
<section class="metric"><p>FRIA STRÅLAR · NIO SCENMÅL</p><div><span>B&nbsp; 11 253 <small>59,2 %</small></span><b>→</b><strong>C&nbsp; 11 489 <small>60,4 %</small></strong></div><em>+236 av 19 008 · +1,2 procentenheter</em></section>
</div>
<div class="columns">
<section><h2>Varför det kan bli bättre</h2><ul><li>28 cm är en halv stolcentrumdelning. En åskådare hamnar därför oftare i öppningen mellan två personer i raden närmast framför.</li><li>Effekten är tydligast för ett centralt mål: 159 fler modellerade platser klarar scenmittsprovet.</li><li>C behåller B:s 2 112 platser, radavstånd, stolavstånd och sektionsvinklar. Förbättringen kräver ingen kapacitetsminskning i planmodellen.</li></ul></section>
<section><h2>Varför det inte alltid blir bättre</h2><ul><li>Sikt är tredimensionell. Marklutning, ögonhöjd, huvudhöjd, avstånd och målets position kan väga tyngre än sidoförskjutningen.</li><li>Varannan-rad-mönstret kan ge ny linjering med en person två rader framför. Därför förbättras inte alla platser eller alla delar av scenen.</li><li>Ökningen över nio scenmål är mindre än ökningen mot scenmitt. C förbättrar alltså främst den centrala siktriktningen.</li></ul></section>
</div>
<section class="warning"><h2>Lång-person-scenariot</h2><p>När <strong>alla</strong> modellerade huvuden höjs från 1,25 till 1,50 m minskar antalet fria scenmittsplatser från 371 i B till 336 i C. Detta är ett konservativt all-heads-test, inte en simulering av en enskild lång person. Slutsats: radförskjutning hjälper i normalfallet men ersätter inte höjdskillnad, lutning eller kontroll av utsatta platser.</p></section>
<footer><strong>Metod:</strong> 2 112 identiska plats-ID i B och C · ögonhöjd 1,20 m · huvudhöjd 1,25 m · huvudradie 10,5 cm · säkerhetsmarginal 5 cm · scenmitt och nio mål −8…+8 m. Resultaten kommer från 3D v4.3:s geometriska stråle–huvud-test. Arbetsmodell, inte inmätning eller siktgaranti.</footer>
</div>"""


def render_artifacts() -> None:
    if not CHROME.exists():
        raise FileNotFoundError(f"Chrome not found at {CHROME}")
    with tempfile.TemporaryDirectory(prefix="naturscen-v15-") as tmp_name:
        tmp = Path(tmp_name)
        for svg_path, png_path in ((OUT_CLEAN, OUT_CLEAN_PNG), (OUT_PHOTO, OUT_PHOTO_PNG)):
            page = tmp / f"{svg_path.stem}.html"
            page.write_text(
                '<!doctype html><meta charset="utf-8"><style>html,body{margin:0;width:1320px;height:980px;overflow:hidden;background:white}img{display:block;width:1320px;height:980px}</style>'
                f'<img src="{svg_path.as_uri()}">',
                encoding="utf-8",
            )
            subprocess.run(
                [str(CHROME), "--headless=new", "--disable-gpu", "--hide-scrollbars", "--allow-file-access-from-files", "--window-size=1320,980", f"--screenshot={png_path}", page.as_uri()],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        pdf_page = tmp / "Naturscen_Forslag_C_v1.5.html"
        pdf_page.write_text(
            '<!doctype html><meta charset="utf-8"><title>Naturscen · Förslag C v1.5</title><style>@page{size:A4 landscape;margin:0}*{box-sizing:border-box}html,body{margin:0;background:white}.page{width:297mm;height:210mm;display:flex;align-items:center;justify-content:center;page-break-after:always}.page:last-child{page-break-after:auto}.page>img{width:100%;height:100%;object-fit:contain}.analysis{display:block;padding:15mm 18mm 12mm;font-family:Arial,sans-serif;color:#1c2a25;background:#f7f5ef}.analysis header{display:flex;justify-content:space-between;align-items:flex-start;border-bottom:1.5px solid #245443;padding-bottom:5mm}.analysis .kicker{margin:0 0 2mm;color:#926d21;font-size:10pt;font-weight:700;letter-spacing:.08em}.analysis h1{margin:0;font-size:25pt;line-height:1.05}.analysis .version{border:1px solid #245443;border-radius:99px;padding:2.5mm 4mm;color:#245443;font-size:9pt;font-weight:700}.analysis .answer{margin:6mm 0 5mm;padding:4mm 5mm;background:#e2eee8;border-left:4px solid #245443;border-radius:2mm;font-size:12pt;line-height:1.35}.analysis .metrics{display:grid;grid-template-columns:1fr 1fr;gap:5mm}.analysis .metric{padding:4mm 5mm;background:white;border:1px solid #d2ccbd;border-radius:3mm}.analysis .metric p{margin:0 0 2.5mm;color:#6b665b;font-size:8.5pt;font-weight:700;letter-spacing:.06em}.analysis .metric div{display:flex;align-items:baseline;gap:4mm;font-size:17pt}.analysis .metric b{color:#928b7b}.analysis .metric strong{color:#245443}.analysis .metric small{font-size:9pt}.analysis .metric em{display:block;margin-top:2mm;color:#245443;font-size:9.5pt;font-style:normal;font-weight:700}.analysis .columns{display:grid;grid-template-columns:1fr 1fr;gap:7mm;margin-top:5mm}.analysis h2{margin:0 0 2mm;font-size:12pt}.analysis ul{margin:0;padding-left:5mm;font-size:9.5pt;line-height:1.36}.analysis li{margin-bottom:1.5mm}.analysis .warning{margin-top:4mm;padding:3.5mm 5mm;background:#f5e7c6;border-left:4px solid #b67b15;border-radius:2mm}.analysis .warning h2{color:#754e0d}.analysis .warning p{margin:0;font-size:9.5pt;line-height:1.35}.analysis footer{margin-top:4mm;padding-top:3mm;border-top:1px solid #cfc8b9;color:#5f5a50;font-size:8.2pt;line-height:1.35}</style>'
            f'<div class="page"><img src="{OUT_CLEAN.as_uri()}"></div><div class="page"><img src="{OUT_PHOTO.as_uri()}"></div>{sight_analysis_page()}',
            encoding="utf-8",
        )
        subprocess.run(
            [str(CHROME), "--headless=new", "--disable-gpu", "--allow-file-access-from-files", "--print-to-pdf-no-header", f"--print-to-pdf={OUT_PDF}", pdf_page.as_uri()],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )


def main() -> None:
    clean_text = SOURCE_CLEAN.read_text(encoding="utf-8")
    source = parse_seats(clean_text)
    shifted = [shift_seat(seat) for seat in source]
    validate_layout(source, shifted)
    source_by_key = {seat_key(seat): seat for seat in source}
    shifted_by_key = {seat_key(seat): seat for seat in shifted}

    OUT_CLEAN.write_text(transform_svg(clean_text, shifted_by_key, photo=False), encoding="utf-8")
    OUT_PHOTO.write_text(transform_svg(SOURCE_PHOTO.read_text(encoding="utf-8"), shifted_by_key, photo=True), encoding="utf-8")
    write_csv(source_by_key, shifted_by_key)
    build_3d(shifted)
    render_artifacts()

    counts = Counter(seat["s"] for seat in shifted)
    print(json.dumps({
        "capacity": len(shifted),
        "counts": {section: counts[section] for section in SECTION_ORDER},
        "boundary_failures": sum(not inside_red_boundaries(seat) for seat in shifted),
        "outputs": [str(path.name) for path in (OUT_CLEAN, OUT_PHOTO, OUT_CLEAN_PNG, OUT_PHOTO_PNG, OUT_PDF, OUT_CSV, OUT_3D)],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
