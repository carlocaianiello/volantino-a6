#!/usr/bin/env python3
"""Genera scripts/retro.json: la ricetta che costruisce lavoro/retro.pcraft dalla scena Higgsfield
(risorse/ai/retro-hangar.webp) con i prodotti veri al posto di quelli generati.
Poi: python3 scripts/pc.py scripts/retro.json"""
import json, os
from PIL import Image

def cmd(id_, **params): return {"cmd": id_, "params": params}
def method(m, **params): return {"method": m, "params": params}

SCENA = "risorse/ai/retro-hangar-vuoto.webp"                # bancone vuoto, scaffali già sfocati
SW, SH = Image.open(SCENA).size                       # 1493 x 2000
S = 1819 / SH                                          # scala per l'altezza A6 con abbondanza
CROP_X = round((SW * S - 1311) / 2)                    # ritaglio simmetrico in larghezza
BASE_Y = round(1395 * S)                               # linea d'appoggio dei prodotti sul tavolo
BORDO_TAVOLO = round(1478 * S)                         # bordo anteriore del piano in acciaio

# prodotti da sinistra a destra: file, altezza reale in cm
PRODOTTI = [("essenziali", 12), ("sostitutivo-pasto", 16.5), ("perfect-whey", 25), ("collagene-rigenera", 15), ("creatina", 12)]
PX_PER_CM = 16                                         # Perfect Whey = 400 px
GAP = 50

def bbox_prodotto(path):
    a = Image.open(path).convert("RGBA").getchannel("A").point(lambda v: 255 if v > 128 else 0)
    return a.getbbox(), Image.open(path).size

steps = [
    method("doc.open", path=SCENA),
    # formato A6 con abbondanza
    cmd("image.imageSize", width=round(SW * S), height=1819, resolution=300, resample="bicubicSharper"),
    cmd("image.crop", x=CROP_X, y=0, width=1311, height=1819),
]
for o, p, c in [("vertical", 35, "lightRed"), ("vertical", 1276, "lightRed"), ("horizontal", 35, "lightRed"), ("horizontal", 1784, "lightRed"),
                ("vertical", 95, "green"), ("vertical", 1216, "green"), ("horizontal", 95, "green"), ("horizontal", 1724, "green")]:
    steps.append(cmd("view.newGuide", orientation=o, position=p, color=c))

# --- prodotti: misure, posizioni, ombre, riflessi
misure = []
for nome, cm in PRODOTTI:
    path = f"risorse/prodotti/{nome}.webp"
    (x0, y0, x1, y1), (W, H) = bbox_prodotto(path)
    s = cm * PX_PER_CM / (y1 - y0)
    misure.append(dict(nome=nome, path=path, s=s, W=W, H=H, bw=(x1 - x0) * s, bh=(y1 - y0) * s,
                       dx=((x0 + x1) / 2 - W / 2) * s, dy=(y1 - H / 2) * s))
larghezza = sum(m["bw"] for m in misure) + GAP * (len(misure) - 1)
x = 655 - larghezza / 2
for m in misure:
    cx = x + m["bw"] / 2; x += m["bw"] + GAP
    centro = [round(cx - m["dx"]), round(BASE_Y - m["dy"])]                      # centro del livello
    centro_rifl = [centro[0], round(2 * BASE_Y - centro[1])]                     # specchiato sulla linea d'appoggio
    steps += [
        # 1) riflesso sull'acciaio (sotto a tutto): specchiato sulla linea d'appoggio, sfumato verso il bordo
        method("doc.place", path=m["path"], scale=m["s"] * 100, center=centro_rifl),
        cmd("layer.renameLayer", name=f"Riflesso {m['nome']}"),
        cmd("edit.transform.flipVertical"),
        cmd("layer.layerMask.revealAll"),
        {"cmd": "paint.gradient", "params": {"from": [round(cx), BASE_Y + 2], "to": [round(cx), BORDO_TAVOLO - 12],
                                              "style": "linear", "colors": ["#a8a8a8", "#000000"], "target": "mask"}, "continue": True},
        cmd("select.rect", x=0, y=0, width=1311, height=BASE_Y + 1),         # niente riflesso sopra la linea d'appoggio
        cmd("edit.fill", contents="black", target="mask"),
        {"cmd": "select.deselect", "params": {}, "continue": True},
        cmd("layer.setProps", opacity=0.12),
        # 2) ombre di contatto sopra al riflesso: una ampia morbida, una stretta scura
        cmd("shape.create", kind="ellipse", name=f"Ombra ampia {m['nome']}", stroke=None,
            rect=[round(cx - m["bw"] / 2 - 30), BASE_Y - 18, round(m["bw"] + 60), 48],
            fill={"gradient": {"stops": [[0, "#000000"], [0.5, "#505050"], [1, "#ffffff"]], "style": "radial", "angle": 0}}),
        cmd("layer.setProps", opacity=0.85, blend="Multiply"),
        cmd("shape.create", kind="ellipse", name=f"Ombra contatto {m['nome']}", stroke=None,
            rect=[round(cx - m["bw"] / 2 - 4), BASE_Y - 8, round(m["bw"] + 8), 18],
            fill={"gradient": {"stops": [[0, "#000000"], [0.7, "#303030"], [1, "#ffffff"]], "style": "radial", "angle": 0}}),
        cmd("layer.setProps", opacity=1.0, blend="Multiply"),
        # 3) il prodotto, con la base leggermente in ombra (velatura ritagliata sul prodotto)
        method("doc.place", path=m["path"], scale=m["s"] * 100, center=centro),
        cmd("layer.renameLayer", name=m["nome"]),
        cmd("layer.layerMask.revealAll"),                                      # via l'ombra grigia incorporata nella foto
        cmd("select.rect", x=0, y=BASE_Y + 1, width=1311, height=1819 - BASE_Y),
        cmd("edit.fill", contents="black", target="mask"),
        {"cmd": "select.deselect", "params": {}, "continue": True},
        cmd("shape.create", kind="rect", name=f"Base in ombra {m['nome']}", stroke=None,
            rect=[round(cx - m["bw"] / 2 - 2), round(BASE_Y - m["bh"] * 0.14), round(m["bw"] + 4), round(m["bh"] * 0.14) + 2],
            fill={"gradient": {"stops": [[0, "#ffffff"], [1, "#000000"]], "style": "linear", "angle": -90}}),
        cmd("layer.createClippingMask"),
        cmd("layer.setProps", opacity=0.55, blend="Multiply"),
    ]

# --- header: logo Nutrihangar
steps += [
    method("doc.place", path="risorse/logo-nutrihangar.webp", scale=45, center=[655, 205]),
    cmd("layer.renameLayer", name="Logo Nutrihangar"),
]

# --- scritta centrale: "Inquadra il QR Code e ottieni subito il 25% di sconto su Why Nature e Why Sport"
ORO = [[0, "#fff3c4"], [0.3, "#e8c058"], [0.5, "#fff8dc"], [0.7, "#b8860b"], [1, "#ffe9a8"]]
def testo_fx(testo, x, y, font, size, align, effetti, nome, **extra):
    return [cmd("type.create", x=x, y=y, text=testo, name=nome, font=font, size=size, align=align, color="#ffffff", **extra),
            cmd("layer.layerStyle.replace", effects=effetti)]
FX_SCRIPT = [{"kind": "dropShadow", "params": {"color": "#000000", "opacity": 75, "angle": 120, "distance": 6, "size": 10}},
             {"kind": "outerGlow", "params": {"color": "#ffd97a", "opacity": 45, "size": 22}}]
FX_BIANCO = [{"kind": "dropShadow", "params": {"color": "#000000", "opacity": 80, "angle": 120, "distance": 8, "size": 8}},
             {"kind": "stroke", "params": {"size": 4, "position": "outside", "color": "#2a1d00"}}]
steps += testo_fx("Inquadra il QR Code", 655, 392, "Kaushan Script", 24, "center", FX_SCRIPT, "Titolo 1")
steps += testo_fx("E OTTIENI SUBITO IL", 640, 470, "Montserrat", 12, "center", FX_SCRIPT, "Titolo 2", weight=700, tracking=120)
steps += [   # 25% in oro metallico: testo convertito in forma per il gradiente a più tappe
    cmd("type.create", x=440, y=755, text="25%", name="Titolo 25%", font="Anton", size=72, align="center", color="#ffffff"),
    cmd("type.convertToShape"),
    cmd("shape.edit", fill={"gradient": {"stops": ORO, "angle": 90, "style": "linear"}}, stroke=None),
    cmd("layer.layerStyle.replace", effects=[
        {"kind": "dropShadow", "params": {"color": "#000000", "opacity": 80, "angle": 120, "distance": 16, "size": 12}},
        {"kind": "outerGlow", "params": {"color": "#ffcf5a", "opacity": 50, "size": 40}},
        {"kind": "bevelEmboss", "params": {"style": "inner", "technique": "chiselHard", "depth": 260, "size": 10, "soften": 1, "angle": 120, "altitude": 45}},
        {"kind": "stroke", "params": {"size": 6, "position": "outside", "color": "#3a2a00"}}]),
    cmd("type.create", x=770, y=630, text="DI\nSCONTO", name="Titolo di sconto", font="Anton", size=30, leading=30, align="left", color="#ffffff"),
    cmd("type.convertToShape"),
    cmd("shape.edit", fill={"gradient": {"stops": [[0, "#ffffff"], [1, "#ffe9b0"]], "angle": 90, "style": "linear"}}, stroke=None),
    cmd("layer.layerStyle.replace", effects=FX_BIANCO + [{"kind": "bevelEmboss", "params": {"style": "inner", "technique": "smooth", "depth": 150, "size": 5, "angle": 120, "altitude": 45}}]),
]
steps += testo_fx("su WHY NATURE e WHY SPORT", 655, 835, "Montserrat", 13, "center", FX_BIANCO, "Titolo marchi", weight=800)
steps += [cmd("type.edit", runs=[{"start": 3, "end": 13, "color": "#a6c839"}, {"start": 16, "end": 25, "color": "#e20613"}])]

# --- badge adesivo "OMAGGIO IN OGNI PACCO", in alto a destra accanto a "DI SCONTO"
import math
BADGE_C, BADGE_D, BADGE_ROT = (1100, 523), 232, -10
def ruota(deg, px, py):
    t = math.radians(deg); a, b = math.cos(t), math.sin(t); c, d = -b, a
    return [a, b, c, d, px - a*px - c*py, py - b*px - d*py]
GIRA = cmd("edit.transform", matrix=ruota(BADGE_ROT, *BADGE_C))
def quadrato(d): return [BADGE_C[0] - d // 2, BADGE_C[1] - d // 2, d, d]
steps += [
    # sigillo smerlato in oro metallico
    cmd("shape.create", kind="star", name="Badge omaggio (sigillo)", rect=quadrato(BADGE_D), sides=30, starRatio=0.9,
        fill={"gradient": {"stops": ORO, "angle": 60, "style": "linear"}}, stroke={"width": 2, "color": "#3a2a00", "align": "inside"}),
    cmd("layer.layerStyle.replace", effects=[
        {"kind": "dropShadow", "params": {"color": "#000000", "opacity": 80, "angle": 120, "distance": 10, "size": 20}},
        {"kind": "bevelEmboss", "params": {"style": "inner", "technique": "smooth", "depth": 160, "size": 6, "angle": 120, "altitude": 45}}]), GIRA,
    # centro scuro con bordo oro
    cmd("shape.create", kind="ellipse", name="Badge omaggio (centro)", rect=quadrato(BADGE_D - 44),
        fill={"gradient": {"stops": [[0, "#4a3612"], [1, "#0e0902"]], "style": "radial", "angle": 0}},
        stroke={"width": 3, "color": "#fff3c4", "align": "inside"}),
    cmd("layer.layerStyle.innerShadow", color="#000000", opacity=60, angle=120, distance=4, size=10), GIRA,
    # testi
    cmd("type.create", x=BADGE_C[0], y=BADGE_C[1] - 2, text="OMAGGIO", name="Badge: OMAGGIO", font="Anton", size=13.5,
        align="center", color="#ffffff"),
    cmd("type.convertToShape"),
    cmd("shape.edit", fill={"gradient": {"stops": ORO, "angle": 90, "style": "linear"}}, stroke=None),
    cmd("layer.layerStyle.replace", effects=[
        {"kind": "dropShadow", "params": {"color": "#000000", "opacity": 80, "angle": 120, "distance": 4, "size": 4}},
        {"kind": "stroke", "params": {"size": 2, "position": "outside", "color": "#2a1d00"}}]), GIRA,
    cmd("type.create", x=BADGE_C[0], y=BADGE_C[1] + 30, text="IN OGNI PACCO", name="Badge: in ogni pacco", font="Inter", weight=700,
        size=4.6, tracking=40, align="center", color="#ffffff"), GIRA,
]

# --- footer: QR a tutta altezza (pavimento sotto il bancone fino al rifilo), con pochi px di margine
PIEDE_TOP = round(1542 * S)                              # inizio del pavimento sotto il bancone
MARGINE = 16
QR_LATO = 1784 - PIEDE_TOP - 2 * MARGINE
steps += [
    method("doc.place", path="risorse/qr-nutrihangar.png", scale=QR_LATO / 2000 * 100,
           center=[1276 - MARGINE - QR_LATO // 2, PIEDE_TOP + MARGINE + QR_LATO // 2]),
    cmd("layer.renameLayer", name="QR code"),
    cmd("layer.layerStyle.dropShadow", color="#000000", opacity=60, angle=120, distance=6, size=18),
    # sito: sulla fascia scura del bancone, centrato sul QR, a metà tra il bordo d'acciaio e il QR
    cmd("type.create", x=1276 - MARGINE - QR_LATO // 2, y=round((BORDO_TAVOLO + PIEDE_TOP + MARGINE) / 2) + 13,
        text="nutrihangar.it", name="Sito", font="Montserrat", weight=700, size=9.5, tracking=40, align="center", color="#ffffff"),
    cmd("layer.layerStyle.replace", effects=[{"kind": "dropShadow", "params": {"color": "#000000", "opacity": 80, "angle": 120, "distance": 4, "size": 6}}]),
]

# --- footer: termini a sinistra del QR, blocco centrato nello spazio 95..895 e sull'altezza del QR
import re, subprocess, sys, tempfile
ORO_TESTO = "#e8c058"
FX_TESTO = [{"kind": "dropShadow", "params": {"color": "#000000", "opacity": 70, "angle": 120, "distance": 4, "size": 6}}]
TITOLO = dict(font="Cinzel", weight=700, size=8, tracking=90, color=ORO_TESTO)
RIGA = dict(font="Inter", weight=600, size=7.5, color="#ffffff")
NOTA = dict(font="Inter", weight=400, size=5.5, color="#c8c8c8")
RIGHE = [  # (tipo, testo, distanza dalla riga precedente in px, evidenziazioni in oro [(inizio, fine), ...])
    ("titolo", "LO SCONTO È:", 0, []),
    ("punto", "Applicato automaticamente al check-out", 35, []),
    ("punto", "Valido sul primo ordine", 30, []),
    ("punto", "Spesa minima 50 €", 30, []),
    ("punto", "Non cumulabile con altre offerte", 30, []),
    ("testo", "Dopo il primo ordine entri a far parte", 44, []),
    ("testo", "del programma fedeltà con sconti a vita", 29, [(4, 21)]),
    ("testo", "fino al 20% di sconto", 29, [(8, 11)]),
    ("nota", "Ci riserviamo di annullare lo sconto e bloccare il cliente", 30, []),
    ("nota", "in caso di qualsiasi tentativo di utilizzo multiplo o di abuso.", 22, []),
]
def spec_riga(tipo, testo):
    if tipo == "titolo": return dict(text=testo, align="left", **TITOLO)
    if tipo == "nota": return dict(text=testo, align="left", **NOTA)
    if tipo == "testo": return dict(text=testo, align="left", **RIGA)
    return dict(text="•  " + testo, align="left", **RIGA)

def misura_larghezze(specs):
    """Crea ogni riga in un documento di prova e legge la larghezza reale dai bounds di type.create."""
    passi = [method("doc.open", path="lavoro/base-a6.pcraft")]          # a 300 dpi, come il volantino
    passi += [cmd("type.create", x=0, y=500, **sp) for sp in specs]
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f: json.dump(passi, f); tmp = f.name
    out = subprocess.run([sys.executable, "-I", os.path.join(os.path.dirname(os.path.abspath(__file__)), "pc.py"), tmp],
                         capture_output=True, text=True).stdout
    larghezze = []
    for m in re.finditer(r"^\[\d+\] type.create: (\{.*\})$", out, re.M):
        b = json.loads(m.group(1))["result"]["bounds"]; larghezze.append(b[2] - b[0])
    os.unlink(tmp); assert len(larghezze) == len(specs), out[-800:]
    return larghezze

specs = [spec_riga(t, x) for t, x, _, _ in RIGHE]
larghezze = misura_larghezze(specs)
blocco_w = max(larghezze)
sinistra = max(95, round(495 - blocco_w / 2))                 # centro dello spazio 95..895
altezza = sum(d for _, _, d, _ in RIGHE) + 23 + 5               # dalla cima del primo titolo al piede dell'ultima riga
y = round(1580 - altezza / 2) + 23                           # prima linea di base, blocco centrato sul QR
print(f"footer: blocco {blocco_w} px largo, {altezza} px alto, sinistra {sinistra}, prima base {y}")
for (tipo, testo, dist, oro), sp in zip(RIGHE, specs):
    y += dist
    steps += [cmd("type.create", x=sinistra, y=y, name=f"Footer: {testo}", **sp)]
    runs = ([{"start": 0, "end": 1, "color": ORO_TESTO, "size": 10, "weight": 800}] if tipo == "punto" else [])
    runs += [{"start": a, "end": b, "color": ORO_TESTO, "weight": 800} for a, b in oro]
    if runs: steps += [cmd("type.edit", runs=runs)]
    steps += [cmd("layer.layerStyle.replace", effects=FX_TESTO)]

steps += [
    {"cmd": "layer.list", "params": {}},
    method("doc.save", path="lavoro/retro.pcraft"),
    method("doc.save", path="export/anteprima-retro.png"),
    cmd("image.crop", x=35, y=35, width=1241, height=1749),                 # come apparirà rifilato
    method("doc.save", path="export/anteprima-retro-rifilata.png"),
]
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "retro.json")
json.dump(steps, open(out, "w"), indent=1, ensure_ascii=False)
print(f"{len(steps)} passi in {out}; scala {S:.4f}, crop x {CROP_X}, base {BASE_Y}, bordo tavolo {BORDO_TAVOLO}")
for m in misure: print(f"  {m['nome']:20s} scala {m['s']:.3f}  {m['bw']:.0f} x {m['bh']:.0f} px")
