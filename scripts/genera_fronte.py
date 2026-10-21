#!/usr/bin/env python3
"""Genera scripts/fronte.json: la ricetta che ricostruisce lavoro/fronte.pcraft da lavoro/base-a6.pcraft.
Modifica qui (testi, misure, effetti) e poi: python3 scripts/pc.py scripts/fronte.json"""
import json, math, os
from PIL import Image

def cmd(id_, **params): return {"cmd": id_, "params": params}
def method(m, **params): return {"method": m, "params": params}
def rot_matrix(deg, px, py):
    """Matrice affine [a,b,c,d,e,f] che ruota di `deg` gradi attorno al punto (px,py)."""
    t = math.radians(deg); a, b = math.cos(t), math.sin(t); c, d = -b, a
    return [a, b, c, d, px - a*px - c*py, py - b*px - d*py]
def colore_medio(path, box):
    im = Image.open(path).convert("RGB").crop(box); px = list(im.get_flattened_data()) if hasattr(im, "get_flattened_data") else list(im.getdata())
    return "#%02x%02x%02x" % tuple(sum(c[i] for c in px) // len(px) for i in range(3))

# ---------------------------------------------------------------- misure e colori
ROT = -7                                   # inclinazione delle scritte, come la diagonale
VERDE_SCURO, ROSSO_SCURO = "#1b4a06", "#3a0000"
ZONA_NATURE = [[0, 0], [1311, 0], [1311, 720], [0, 880]]
ZONA_SPORT = [[0, 902], [1311, 742], [1311, 1530], [0, 1530]]
GRAD_NATURE = [[0, "#e4f5b0"], [0.5, "#8fc63f"], [1, "#2c6410"]]
GRAD_SPORT = [[0, "#e20613"], [0.45, "#7d0008"], [1, "#140000"]]
SFOCATURA = 30

FOTO_NATURE, FOTO_SPORT = "risorse/ai/foto-nature.webp", "risorse/ai/foto-sport.webp"   # solo per gli sfondi sfocati
COMPOSIZIONE = "risorse/ai/composizione-ai.webp"                                       # personaggi generati sul volantino
NAT_W, NAT_H = Image.open(FOTO_NATURE).size
SPO_W, SPO_H = Image.open(FOTO_SPORT).size
AI_W, AI_H = Image.open(COMPOSIZIONE).size

# Ritagli dei personaggi nella composizione AI e pezzi di volantino da cancellare nella maschera
# (coordinate del ritaglio; la banda bianca della diagonale va da (0,969) a (1611,793) nell'immagine intera)
RIT_DONNA = [940, 40, 671, 840]
VIA_DONNA = [[[0, 824], [671, 750], [671, 840], [0, 840]]]                 # diagonale e striscia rossa sotto i piedi
RIT_UOMO = [0, 840, 860, 866]
VIA_UOMO = [[[0, 121], [503, 66], [503, 104], [0, 159]],                   # banda bianca a sinistra della testa (con i bordi)
            [[612, 51], [860, 27], [860, 65], [612, 89]],                  # banda bianca a destra della testa
            [[628, 440], [860, 380], [860, 566], [628, 566]],              # inizio di "Supera" e sfondo accanto al braccio
            [[768, 540], [860, 540], [860, 866], [768, 866]]]              # angolo di "LIMITI"
AGGIUNGI_UOMO = [cmd("select.object", rect=[0, 480, 250, 380], mode="add")]   # disco sinistro, scuro su scuro

def personaggio(rit, via, nome, out, aggiungi=()):
    """Ritaglia la porzione della composizione AI, isola la figura (Select Subject) e cancella nella
    maschera i pezzi di volantino rimasti attaccati."""
    s = [method("doc.open", path=COMPOSIZIONE),
         cmd("image.crop", x=rit[0], y=rit[1], width=rit[2], height=rit[3]),
         cmd("layer.new.layerFromBackground", name=nome),
         cmd("select.subject"), *aggiungi,
         cmd("layer.layerMask.revealSelection")]
    for poly in via:
        s += [cmd("select.lasso", points=poly), cmd("edit.fill", contents="black", target="mask")]
    s += [method("doc.save", path=out), method("doc.close")]
    return s

# ---------------------------------------------------------------- preparazione delle foto
steps = []
steps += personaggio(RIT_DONNA, VIA_DONNA, "Donna", "lavoro/foto/nature-soggetto.png")
steps += personaggio(RIT_UOMO, VIA_UOMO, "Uomo", "lavoro/foto/sport-soggetto.png", AGGIUNGI_UOMO)
steps += [   # sfondo nature: via la scritta e la donna della prima foto, poi sfocatura
    method("doc.open", path=FOTO_NATURE),
    cmd("select.rect", x=30, y=110, width=410, height=190),
    cmd("edit.deleteAndFillSelection"),
    cmd("select.object", rect=[int(NAT_W * 0.47) + 30, 140, 440, 960]),
    cmd("select.modify.expand", radius=30),
    cmd("select.modify.feather", radius=40),
    cmd("paint.gradient", **{"from": [700, 150], "to": [700, 1130], "style": "linear",
                            "colors": [colore_medio(FOTO_NATURE, (875, 150, 925, 320)),
                                       colore_medio(FOTO_NATURE, (875, 600, 925, 760)),
                                       colore_medio(FOTO_NATURE, (875, 980, 925, 1140))]}),
    {"cmd": "select.deselect", "params": {}, "continue": True},
    cmd("filter.blur.gaussianBlur", radius=SFOCATURA),
    method("doc.save", path="lavoro/foto/nature-sfondo.png"),
    method("doc.close"),
]
steps += [   # sfondo sport: via l'uomo della prima foto, poi sfocatura
    method("doc.open", path=FOTO_SPORT),
    cmd("select.subject"),
    cmd("select.object", rect=[15, 580, 240, 270], mode="add"),
    cmd("select.object", rect=[325, 590, 170, 200], mode="add"),
    cmd("select.modify.expand", radius=50),
    cmd("select.modify.feather", radius=60),
    cmd("edit.fill", contents="color", color="#3a0608"),
    {"cmd": "select.deselect", "params": {}, "continue": True},
    cmd("filter.blur.gaussianBlur", radius=SFOCATURA * 2),
    method("doc.save", path="lavoro/foto/sport-sfondo.png"),
    method("doc.close"),
]

# ---------------------------------------------------------------- il volantino
steps += [method("doc.open", path="lavoro/base-a6.pcraft")]

def zona(nome, knots, grad, angle):
    return [cmd("shape.create", kind="path", name=nome, stroke=None,
                path={"subpaths": [{"closed": True, "knots": knots}]},
                fill={"gradient": {"stops": grad, "angle": angle, "style": "linear"}})]

def sfondo_sfocato(path, scale, center, knots, grad, angle, nome):
    """Sfondo sfocato esteso sulla zona (ritagliato sulla forma) e velato con i colori del marchio."""
    velo = lambda suffisso, op, blend: [
        cmd("shape.create", kind="path", name=nome + suffisso, stroke=None,
            path={"subpaths": [{"closed": True, "knots": knots}]},
            fill={"gradient": {"stops": grad, "angle": angle, "style": "linear"}}),
        cmd("layer.createClippingMask"),
        cmd("layer.setProps", opacity=op, **({"blend": blend} if blend else {}))]
    return ([method("doc.place", path=path, scale=scale, center=center),
             cmd("layer.renameLayer", name=nome),
             cmd("layer.createClippingMask")]
            + velo(" (velatura)", 0.75, "Color") + velo(" (luce)", 0.25, None))

BG_S = 1.45
steps += zona("Zona nature", ZONA_NATURE, GRAD_NATURE, -35)
steps += sfondo_sfocato("lavoro/foto/nature-sfondo.png", BG_S * 100, [655, round(-330 + NAT_H * BG_S / 2)],
                        ZONA_NATURE, GRAD_NATURE, -35, "Sfondo WHY nature")
steps += [cmd("shape.create", kind="ellipse", name="Ombra piede donna", rect=[955, 722, 170, 28], stroke=None,
              fill={"gradient": {"stops": [[0, "#000000"], [1, "#ffffff"]], "style": "radial", "angle": 0}}),
          cmd("layer.createClippingMask"),
          cmd("layer.setProps", opacity=0.4, blend="Multiply")]
steps += zona("Zona sport", ZONA_SPORT, GRAD_SPORT, -150)
steps += sfondo_sfocato("lavoro/foto/sport-sfondo.png", BG_S * 100, [655, round(640 + SPO_H * BG_S / 2)],
                        ZONA_SPORT, GRAD_SPORT, -150, "Sfondo WHY sport")

steps += [   # separatore diagonale
    cmd("shape.create", kind="path", name="Separatore", fill="#ffffff", stroke=None,
        path={"subpaths": [{"closed": True, "knots": [[0, 880], [1311, 720], [1311, 742], [0, 902]]}]}),
    cmd("layer.layerStyle.dropShadow", color="#000000", opacity=50, angle=120, distance=12, size=28),
]

# ---------------------------------------------------------------- loghi e slogan
def scritta_grande(testo, x, y, size, align, grad_stops, stroke, glow, pivot, nome):
    """Testo pesante (Anton) convertito in forma per la sfumatura metallica a più tappe."""
    return [
        cmd("type.create", x=x, y=y, text=testo, name=nome, font="Anton", size=size, color="#ffffff", align=align),
        cmd("type.convertToShape"),
        cmd("shape.edit", fill={"gradient": {"stops": grad_stops, "angle": 90, "style": "linear"}}, stroke=None),
        cmd("layer.layerStyle.replace", effects=[
            {"kind": "dropShadow", "params": {"color": "#000000", "opacity": 70, "angle": 120, "distance": 16, "size": 10}},
            {"kind": "outerGlow", "params": {"color": glow, "opacity": 55, "size": 34}},
            {"kind": "bevelEmboss", "params": {"style": "inner", "technique": "chiselHard", "depth": 220, "size": 8, "soften": 1, "angle": 120, "altitude": 45}},
            {"kind": "stroke", "params": {"size": 7, "position": "outside", "color": stroke}},
        ]),
        cmd("edit.transform", matrix=rot_matrix(ROT, *pivot)),
    ]

def scritta_corsiva(testo, x, y, size, align, shadow, glow, pivot, nome):
    return [
        cmd("type.create", x=x, y=y, text=testo, name=nome, font="Kaushan Script", size=size, color="#ffffff", align=align),
        cmd("layer.layerStyle.replace", effects=[
            {"kind": "dropShadow", "params": {"color": shadow, "opacity": 70, "angle": 120, "distance": 8, "size": 12}},
            {"kind": "outerGlow", "params": {"color": glow, "opacity": 60, "size": 26}},
            {"kind": "stroke", "params": {"size": 3, "position": "outside", "color": shadow}},
        ]),
        cmd("edit.transform", matrix=rot_matrix(ROT, *pivot)),
    ]

steps += [
    cmd("shape.create", kind="roundedRect", name="Targa WHY nature", rect=[80, 78, 590, 224], radii=30, fill="#ffffff", stroke=None),
    cmd("layer.layerStyle.dropShadow", color="#0b2a00", opacity=35, angle=120, distance=8, size=26),
    method("doc.place", path="risorse/logo-why-nature.png", scale=188, center=[375, 190]),
    cmd("layer.renameLayer", name="Logo WHY nature"),
]
PIV_N = (110, 650)
steps += scritta_corsiva("Nutri il tuo", 118, 448, 30, "left", VERDE_SCURO, "#d9ff8a", PIV_N, "Slogan nature 1")
steps += scritta_grande("BENESSERE", 110, 650, 46, "left",
                        [[0, "#ffffff"], [0.42, "#f1ffd2"], [0.5, "#a8dd4a"], [0.58, "#f1ffd2"], [1, "#ffffff"]],
                        VERDE_SCURO, "#d9ff8a", PIV_N, "Slogan nature 2")
steps += [
    method("doc.place", path="risorse/logo-why-sport.png", scale=187.5, center=[1006, 935]),
    cmd("layer.renameLayer", name="Logo WHY sport"),
    cmd("layer.layerStyle.dropShadow", color="#000000", opacity=55, angle=120, distance=8, size=20),
]
PIV_S = (1190, 1420)
steps += scritta_corsiva("Supera i tuoi", 1182, 1183, 30, "right", ROSSO_SCURO, "#ff6a6a", PIV_S, "Slogan sport 1")
steps += scritta_grande("LIMITI", 1190, 1420, 60, "right",
                        [[0, "#ffffff"], [0.42, "#ffe6e6"], [0.5, "#ff3a3a"], [0.58, "#ffe6e6"], [1, "#ffffff"]],
                        ROSSO_SCURO, "#ff3b3b", PIV_S, "Slogan sport 2")

# ---------------------------------------------------------------- personaggi (sopra agli slogan, come nella composizione AI)
DON_S, DON_TOP = 0.80, 113            # piedi a ~735 px, appena sopra la diagonale; capelli fino al bordo destro
steps += [method("doc.place", path="lavoro/foto/nature-soggetto.png", scale=DON_S * 100,
                 center=[round(1311 - RIT_DONNA[2] * DON_S / 2), round(DON_TOP + RIT_DONNA[3] * DON_S / 2)]),
          cmd("layer.renameLayer", name="Donna WHY nature")]
UOM_S, UOM_TOP = 0.87, 785            # la testa supera la diagonale, le gambe finiscono sotto il footer
steps += [method("doc.place", path="lavoro/foto/sport-soggetto.png", scale=UOM_S * 100,
                 center=[round(-8 + RIT_UOMO[2] * UOM_S / 2), round(UOM_TOP + RIT_UOMO[3] * UOM_S / 2)]),
          cmd("layer.renameLayer", name="Uomo WHY sport")]

# ---------------------------------------------------------------- footer (sopra a tutto: copre le gambe)
steps += [
    cmd("shape.create", kind="rect", name="Footer", rect=[0, 1530, 1311, 289], fill="#ffffff", stroke=None),
    cmd("shape.create", kind="rect", name="Linea footer", rect=[0, 1530, 1311, 10], stroke=None,
        fill={"gradient": {"stops": [[0, "#a6c839"], [1, "#e20613"]], "angle": 0, "style": "linear"}}),
    cmd("type.create", x=655, y=1585, text="IN COLLABORAZIONE CON", name="Testo footer",
        font="Montserrat", weight=700, size=8, tracking=260, color="#333333", align="center"),
    method("doc.place", path="risorse/logo-nutrihangar.webp", scale=26, center=[355, 1660]),
    cmd("layer.renameLayer", name="Logo Nutrihangar"),
    method("doc.place", path="lavoro/loghi/radio-swm.png", scale=18, center=[1100, 1660]),
    cmd("layer.renameLayer", name="Logo Radio SWM"),
    {"cmd": "layer.list", "params": {}},
    method("doc.save", path="lavoro/fronte-livelli.pcraft"),
    method("doc.save", path="export/anteprima-fronte-livelli.png"),
]

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fronte.json")
json.dump(steps, open(out, "w"), indent=1, ensure_ascii=False)
print(f"{len(steps)} passi scritti in {out}")
