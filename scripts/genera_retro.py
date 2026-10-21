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
steps += testo_fx("E OTTIENI SUBITO IL", 655, 470, "Montserrat", 12, "center", FX_SCRIPT, "Titolo 2", weight=700, tracking=220)
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

# --- footer: QR a tutta altezza (pavimento sotto il bancone fino al rifilo), con pochi px di margine
PIEDE_TOP = round(1542 * S)                              # inizio del pavimento sotto il bancone
MARGINE = 16
QR_LATO = 1784 - PIEDE_TOP - 2 * MARGINE
steps += [
    method("doc.place", path="risorse/qr-nutrihangar.png", scale=QR_LATO / 2000 * 100,
           center=[1276 - MARGINE - QR_LATO // 2, PIEDE_TOP + MARGINE + QR_LATO // 2]),
    cmd("layer.renameLayer", name="QR code"),
    cmd("layer.layerStyle.dropShadow", color="#000000", opacity=60, angle=120, distance=6, size=18),
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
