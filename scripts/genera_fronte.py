#!/usr/bin/env python3
"""Genera scripts/fronte.json: la ricetta che ricostruisce lavoro/fronte.pcraft da lavoro/base-a6.pcraft.
Modifica qui (testi, misure, effetti) e poi: python3 scripts/pc.py scripts/fronte.json"""
import json, math, os

def rot_matrix(deg, px, py):
    """Matrice affine [a,b,c,d,e,f] che ruota di `deg` gradi attorno al punto (px,py)."""
    t = math.radians(deg); a, b = math.cos(t), math.sin(t); c, d = -b, a
    return [a, b, c, d, px - a*px - c*py, py - b*px - d*py]

def cmd(id_, **params): return {"cmd": id_, "params": params}
def method(m, **params): return {"method": m, "params": params}

ROT = -7            # inclinazione delle scritte, come la diagonale
VERDE_SCURO = "#1b4a06"; ROSSO_SCURO = "#3a0000"

def scritta_grande(testo, x, y, size, align, grad_stops, stroke, glow, pivot, nome):
    """Testo pesante (Anton) convertito in forma per avere la sfumatura metallica a più tappe."""
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

from PIL import Image
NAT_W, NAT_H = Image.open("risorse/ai/foto-nature.webp").size      # 928 x 1152
SPO_W, SPO_H = Image.open("risorse/ai/foto-sport.webp").size
NAT_CROP_X = int(NAT_W * 0.47)                                      # via la fascia con la scritta
NAT_CW = NAT_W - NAT_CROP_X

# Selezioni degli atleti (coordinate delle foto originali / del ritaglio)
SEL_DONNA = [cmd("select.object", rect=[30, 140, 440, 960])]         # Object Finder sulla donna
SEL_UOMO = [cmd("select.subject"),                                   # uomo + i due dischi del bilanciere
            cmd("select.object", rect=[15, 580, 240, 270], mode="add"),
            cmd("select.object", rect=[325, 590, 170, 200], mode="add")]
SFOCATURA = 30

steps = [
    # --- foto nature: ritaglio senza scritta, soggetto nitido, sfondo sfocato senza donna né scritta
    method("doc.open", path="risorse/ai/foto-nature.webp"),
    cmd("image.crop", x=NAT_CROP_X, y=0, width=NAT_CW, height=NAT_H),
    method("doc.save", path="lavoro/foto/nature-ritaglio.png"),
    method("doc.close"),
    method("doc.open", path="lavoro/foto/nature-ritaglio.png"),
    cmd("layer.new.layerFromBackground", name="Donna"),
    *SEL_DONNA,
    cmd("layer.layerMask.revealSelection"),
    # via il pezzo di prato a sinistra del corpo: nero dipinto nella maschera dentro un poligono
    cmd("select.lasso", points=[[0, 345], [100, 345], [150, 380], [165, 430], [150, 480], [155, 530], [170, 560],
                                [195, 580], [195, 640], [160, 680], [110, 725], [80, 760], [62, 785], [70, 805], [0, 830]]),
    cmd("edit.fill", contents="black", target="mask"),
    cmd("select.rect", x=0, y=995, width=NAT_CW, height=300, feather=22),   # il piede si perde nell'erba
    cmd("edit.fill", contents="black", target="mask"),
    method("doc.save", path="lavoro/foto/nature-soggetto.png"),
    method("doc.close"),
    method("doc.open", path="risorse/ai/foto-nature.webp"),
    cmd("select.rect", x=30, y=110, width=410, height=190),                 # scritta "Find your balance"
    cmd("edit.deleteAndFillSelection"),
    cmd("select.object", rect=[NAT_CROP_X + 30, 140, 440, 960]),
    cmd("select.modify.expand", radius=25),
    cmd("edit.deleteAndFillSelection"),
    cmd("filter.blur.gaussianBlur", radius=SFOCATURA),
    method("doc.save", path="lavoro/foto/nature-sfondo.png"),
    method("doc.close"),
    # --- foto sport: soggetto nitido, sfondo sfocato senza uomo
    method("doc.open", path="risorse/ai/foto-sport.webp"),
    cmd("layer.new.layerFromBackground", name="Uomo"),
    *SEL_UOMO,
    cmd("layer.layerMask.revealSelection"),
    method("doc.save", path="lavoro/foto/sport-soggetto.png"),
    method("doc.close"),
    method("doc.open", path="risorse/ai/foto-sport.webp"),
    *SEL_UOMO,
    cmd("select.modify.expand", radius=50),
    cmd("select.modify.feather", radius=60),
    cmd("edit.fill", contents="color", color="#3a0608"),                    # al posto dell'uomo: rosso scuro sfumato
    cmd("filter.blur.gaussianBlur", radius=SFOCATURA * 2),
    method("doc.save", path="lavoro/foto/sport-sfondo.png"),
    method("doc.close"),
    # --- il volantino
    method("doc.open", path="lavoro/base-a6.pcraft"),
]

def sfondo_sfocato(path, scale, center, zona_knots, tinta_stops, tinta_angle, nome):
    """Sfondo della foto (già sfocato) esteso sulla zona e velato con i colori del marchio."""
    return [
        method("doc.place", path=path, scale=scale, center=center),
        cmd("layer.renameLayer", name=nome),
        cmd("layer.createClippingMask"),
        cmd("shape.create", kind="path", name=nome + " (velatura)", stroke=None,
            path={"subpaths": [{"closed": True, "knots": zona_knots}]},
            fill={"gradient": {"stops": tinta_stops, "angle": tinta_angle, "style": "linear"}}),
        cmd("layer.createClippingMask"),
        cmd("layer.setProps", opacity=0.75, blend="Color"),
        cmd("shape.create", kind="path", name=nome + " (luce)", stroke=None,
            path={"subpaths": [{"closed": True, "knots": zona_knots}]},
            fill={"gradient": {"stops": tinta_stops, "angle": tinta_angle, "style": "linear"}}),
        cmd("layer.createClippingMask"),
        cmd("layer.setProps", opacity=0.25),
    ]

def soggetto(path, scale, center, ombra, nome):
    """Atleta nitido sopra lo sfondo, ritagliato sulla zona, con ombra morbida."""
    return [
        method("doc.place", path=path, scale=scale, center=center),
        cmd("layer.renameLayer", name=nome),
        cmd("layer.createClippingMask"),
        cmd("layer.layerStyle.dropShadow", color=ombra, opacity=45, angle=120, distance=14, size=34),
    ]

ZONA_NATURE = [[0, 0], [1311, 0], [1311, 720], [0, 880]]
ZONA_SPORT = [[0, 902], [1311, 742], [1311, 1530], [0, 1530]]
GRAD_NATURE = [[0, "#e4f5b0"], [0.5, "#8fc63f"], [1, "#2c6410"]]
GRAD_SPORT = [[0, "#e20613"], [0.45, "#7d0008"], [1, "#140000"]]

# --- zona WHY nature (sopra) -------------------------------------------------
steps += [cmd("shape.create", kind="path", name="Zona nature", stroke=None,
              path={"subpaths": [{"closed": True, "knots": ZONA_NATURE}]},
              fill={"gradient": {"stops": GRAD_NATURE, "angle": -35, "style": "linear"}})]
BG_S = 1.45                                                         # lo sfondo copre tutta la larghezza
steps += sfondo_sfocato("lavoro/foto/nature-sfondo.png", BG_S * 100, [655, round(-330 + NAT_H * BG_S / 2)],
                        ZONA_NATURE, GRAD_NATURE, -35, "Sfondo WHY nature")
NAT_S = 0.76                                                        # donna alta ~640 px
steps += soggetto("lavoro/foto/nature-soggetto.png", NAT_S * 100, [1110, round(-78 + NAT_H * NAT_S / 2)], "#0b2a00", "Donna WHY nature")

# --- zona WHY sport (sotto) --------------------------------------------------
steps += [cmd("shape.create", kind="path", name="Zona sport", stroke=None,
              path={"subpaths": [{"closed": True, "knots": ZONA_SPORT}]},
              fill={"gradient": {"stops": GRAD_SPORT, "angle": -150, "style": "linear"}})]
steps += sfondo_sfocato("lavoro/foto/sport-sfondo.png", BG_S * 100, [655, round(640 + SPO_H * BG_S / 2)],
                        ZONA_SPORT, GRAD_SPORT, -150, "Sfondo WHY sport")
SPO_S = 0.85                                                        # uomo alto ~715 px, piedi sotto il footer
steps += soggetto("risorse/ai/foto-sport.webp".replace("risorse/ai/foto-sport.webp", "lavoro/foto/sport-soggetto.png"),
                  SPO_S * 100, [400, round(760 + SPO_H * SPO_S / 2)], "#000000", "Uomo WHY sport")


# --- separatore e footer -----------------------------------------------------
steps += [
    cmd("shape.create", kind="path", name="Separatore", fill="#ffffff", stroke=None,
        path={"subpaths": [{"closed": True, "knots": [[0, 880], [1311, 720], [1311, 742], [0, 902]]}]}),
    cmd("layer.layerStyle.dropShadow", color="#000000", opacity=50, angle=120, distance=12, size=28),
    cmd("shape.create", kind="rect", name="Footer", rect=[0, 1530, 1311, 289], fill="#ffffff", stroke=None),
    cmd("shape.create", kind="rect", name="Linea footer", rect=[0, 1530, 1311, 10], stroke=None,
        fill={"gradient": {"stops": [[0, "#a6c839"], [1, "#e20613"]], "angle": 0, "style": "linear"}}),
]

# --- logo e slogan WHY nature ------------------------------------------------
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

# --- logo e slogan WHY sport -------------------------------------------------
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

# --- footer: collaborazioni --------------------------------------------------
steps += [
    cmd("type.create", x=655, y=1585, text="IN COLLABORAZIONE CON", name="Testo footer",
        font="Montserrat", weight=700, size=8, tracking=260, color="#333333", align="center"),
    method("doc.place", path="risorse/logo-nutrihangar.webp", scale=26, center=[355, 1660]),
    cmd("layer.renameLayer", name="Logo Nutrihangar"),
    method("doc.place", path="lavoro/loghi/radio-swm.png", scale=18, center=[1100, 1660]),
    cmd("layer.renameLayer", name="Logo Radio SWM"),
    {"cmd": "layer.list", "params": {}},
    method("doc.save", path="lavoro/fronte.pcraft"),
    method("doc.save", path="export/anteprima-fronte.png"),
]

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fronte.json")
json.dump(steps, open(out, "w"), indent=1, ensure_ascii=False)
print(f"{len(steps)} passi scritti in {out}")
