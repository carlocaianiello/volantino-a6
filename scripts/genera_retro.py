#!/usr/bin/env python3
"""Genera scripts/retro.json: la ricetta che costruisce lavoro/retro.pcraft dalla scena Higgsfield
(risorse/ai/retro-hangar.webp) con i prodotti veri al posto di quelli generati.
Poi: python3 scripts/pc.py scripts/retro.json"""
import json, os
from PIL import Image

def cmd(id_, **params): return {"cmd": id_, "params": params}
def method(m, **params): return {"method": m, "params": params}

SCENA = "risorse/ai/retro-hangar.webp"
SW, SH = Image.open(SCENA).size                       # 1493 x 2000
S = 1819 / SH                                          # scala per l'altezza A6 con abbondanza
CROP_X = round((SW * S - 1311) / 2)                    # ritaglio simmetrico in larghezza
BASE_Y = round(1365 * S)                               # linea d'appoggio dei prodotti sul tavolo
BORDO_TAVOLO = round(1445 * S)                         # bordo anteriore del piano in acciaio

# prodotti da sinistra a destra: file, altezza reale in cm
PRODOTTI = [("essenziali", 12), ("sostitutivo-pasto", 16.5), ("perfect-whey", 25), ("collagene-rigenera", 15), ("creatina", 12)]
PX_PER_CM = 16                                         # Perfect Whey = 400 px
GAP = 50

def bbox_prodotto(path):
    a = Image.open(path).convert("RGBA").getchannel("A").point(lambda v: 255 if v > 128 else 0)
    return a.getbbox(), Image.open(path).size

steps = [
    method("doc.open", path=SCENA),
    # via i prodotti generati (etichette sbagliate) e i loro riflessi
    cmd("select.object", rect=[150, 870, 1200, 510]),                 # solo i cinque prodotti generati
    cmd("select.modify.expand", radius=25),
    cmd("edit.deleteAndFillSelection"),
    cmd("select.rect", x=240, y=1366, width=1080, height=95),
    cmd("edit.deleteAndFillSelection"),
    # scaffali molto più sfocati (sinistra e destra, sopra il tavolo), con bordo morbido
    cmd("select.rect", x=0, y=0, width=470, height=1250, feather=50),
    cmd("filter.blur.gaussianBlur", radius=28),
    cmd("select.rect", x=1030, y=0, width=SW - 1030, height=1250, feather=50),
    cmd("filter.blur.gaussianBlur", radius=28),
    {"cmd": "select.deselect", "params": {}, "continue": True},
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
        cmd("shape.create", kind="ellipse", name=f"Ombra {m['nome']}", stroke=None,
            rect=[round(cx - m["bw"] / 2 - 14), BASE_Y - 10, round(m["bw"] + 28), 22],
            fill={"gradient": {"stops": [[0, "#000000"], [1, "#ffffff"]], "style": "radial", "angle": 0}}),
        cmd("layer.setProps", opacity=0.6, blend="Multiply"),
        method("doc.place", path=m["path"], scale=m["s"] * 100, center=centro_rifl),
        cmd("layer.renameLayer", name=f"Riflesso {m['nome']}"),
        cmd("edit.transform.flipVertical"),
        cmd("layer.layerMask.revealAll"),
        {"cmd": "paint.gradient", "params": {"from": [round(cx), BASE_Y], "to": [round(cx), BORDO_TAVOLO - 12],
                                              "style": "linear", "colors": ["#ffffff", "#000000"], "target": "mask"}, "continue": True},
        cmd("layer.setProps", opacity=0.28),
        method("doc.place", path=m["path"], scale=m["s"] * 100, center=centro),
        cmd("layer.renameLayer", name=m["nome"]),
    ]

# --- header: logo Nutrihangar
steps += [
    method("doc.place", path="risorse/logo-nutrihangar.webp", scale=45, center=[655, 235]),
    cmd("layer.renameLayer", name="Logo Nutrihangar"),
    cmd("layer.layerStyle.outerGlow", color="#d8b35a", opacity=35, size=40),
    {"cmd": "layer.list", "params": {}},
    method("doc.save", path="lavoro/retro.pcraft"),
    method("doc.save", path="export/anteprima-retro.png"),
]
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "retro.json")
json.dump(steps, open(out, "w"), indent=1, ensure_ascii=False)
print(f"{len(steps)} passi in {out}; scala {S:.4f}, crop x {CROP_X}, base {BASE_Y}, bordo tavolo {BORDO_TAVOLO}")
for m in misure: print(f"  {m['nome']:20s} scala {m['s']:.3f}  {m['bw']:.0f} x {m['bh']:.0f} px")
