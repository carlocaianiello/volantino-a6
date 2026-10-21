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

steps = [method("doc.open", path="lavoro/base-a6.pcraft")]

# --- zona WHY nature (sopra) -------------------------------------------------
steps += [
    cmd("shape.create", kind="path", name="Zona nature",
        path={"subpaths": [{"closed": True, "knots": [[0, 0], [1311, 0], [1311, 720], [0, 880]]}]},
        fill={"gradient": {"stops": [[0, "#e4f5b0"], [0.5, "#8fc63f"], [1, "#2c6410"]], "angle": -35, "style": "linear"}}, stroke=None),
]
for nome, rect, op in [("[provv] luce nature 1", [860, 90, 400, 400], 0.55), ("[provv] luce nature 2", [1030, 430, 230, 230], 0.55), ("[provv] luce nature 3", [700, 520, 150, 150], 0.55)]:
    steps += [cmd("shape.create", kind="ellipse", name=nome, rect=rect, stroke=None,
                  fill={"gradient": {"stops": [[0, "#ffffff"], [0.7, "#9fb070"], [1, "#000000"]], "style": "radial", "angle": 0}}),
              cmd("layer.setProps", opacity=op, blend="Screen")]

# --- zona WHY sport (sotto) --------------------------------------------------
steps += [
    cmd("shape.create", kind="path", name="Zona sport",
        path={"subpaths": [{"closed": True, "knots": [[0, 902], [1311, 742], [1311, 1530], [0, 1530]]}]},
        fill={"gradient": {"stops": [[0, "#e20613"], [0.45, "#7d0008"], [1, "#140000"]], "angle": -150, "style": "linear"}}, stroke=None),
    cmd("shape.create", kind="ellipse", name="[provv] bagliore sport", rect=[-80, 930, 760, 760], stroke=None,
        fill={"gradient": {"stops": [[0, "#ff5a5a"], [0.55, "#8a0010"], [1, "#000000"]], "style": "radial", "angle": 0}}),
    cmd("layer.setProps", opacity=0.75, blend="Screen"),
    cmd("shape.create", kind="path", name="[provv] striscia sport 1", fill="#ffffff", stroke=None,
        path={"subpaths": [{"closed": True, "knots": [[0, 1480], [640, 960], [700, 960], [60, 1480]]}]}),
    cmd("layer.setProps", opacity=0.10, blend="Screen"),
    cmd("shape.create", kind="path", name="[provv] striscia sport 2", fill="#ffffff", stroke=None,
        path={"subpaths": [{"closed": True, "knots": [[120, 1530], [760, 1010], [785, 1010], [145, 1530]]}]}),
    cmd("layer.setProps", opacity=0.07, blend="Screen"),
]

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
