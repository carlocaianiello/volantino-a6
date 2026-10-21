"""Mattoni per scrivere le ricette dei volantini (liste di passi JSON per pc.py / i tool MCP di PhotoCraft).

Uso tipico, in un generatore `genera_fronte.py`:
    import sys; sys.path.insert(0, "<cartella della skill>/scripts")
    from ricetta import *
    steps = [method("doc.open", path="lavoro/base-a6.pcraft")]
    steps += zona("Zona alta", [[0,0],[1311,0],[1311,720],[0,880]], GRAD_VERDE, -35)
    steps += scritta_oro("25%", 455, 755, 92, "center", pivot=(455, 755), rot=-7)
    steps += [method("doc.save", path="lavoro/fronte.pcraft"), method("doc.save", path="export/anteprima-fronte.png")]
    salva(steps, "scripts/fronte.json")
poi:  python3 <skill>/scripts/pc.py scripts/fronte.json
"""
import json, math, os, re, subprocess, sys, tempfile

# ---------------------------------------------------------------- palette (vedi references/stile.md)
ORO = [[0, "#fff3c4"], [0.3, "#e8c058"], [0.5, "#fff8dc"], [0.7, "#b8860b"], [1, "#ffe9a8"]]   # oro metallico a 5 tappe
ORO_TESTO, ORO_SCURO = "#e8c058", "#3a2a00"
GRAD_VERDE = [[0, "#e4f5b0"], [0.5, "#8fc63f"], [1, "#2c6410"]]       # mondo "nature"
GRAD_ROSSO = [[0, "#e20613"], [0.45, "#7d0008"], [1, "#140000"]]      # mondo "sport"
VERDE_SCURO, ROSSO_SCURO = "#1b4a06", "#3a0000"

def cmd(id_, **params): return {"cmd": id_, "params": params}
def method(m, **params): return {"method": m, "params": params}
def salva(steps, path):
    json.dump(steps, open(path, "w"), indent=1, ensure_ascii=False); print(f"{len(steps)} passi in {path}")

def rot_matrix(deg, px, py):
    """Matrice affine [a,b,c,d,e,f] per edit.transform: ruota di `deg` gradi attorno al punto (px,py).
    Con lo stesso perno per più livelli, le scritte restano allineate tra loro dopo la rotazione."""
    t = math.radians(deg); a, b = math.cos(t), math.sin(t); c, d = -b, a
    return [a, b, c, d, px - a*px - c*py, py - b*px - d*py]

def ruota(pivot, deg): return cmd("edit.transform", matrix=rot_matrix(deg, *pivot))

# ---------------------------------------------------------------- forme di fondo
def zona(nome, knots, grad, angle, stroke=None):
    """Area piena a gradiente lineare, con contorno poligonale (knots in px, orario)."""
    return [cmd("shape.create", kind="path", name=nome, stroke=stroke,
                path={"subpaths": [{"closed": True, "knots": knots}]},
                fill={"gradient": {"stops": grad, "angle": angle, "style": "linear"}})]

def separatore(nome, knots, ombra=True):
    """Striscia bianca (es. diagonale tra due zone) con ombra morbida."""
    s = [cmd("shape.create", kind="path", name=nome, fill="#ffffff", stroke=None,
             path={"subpaths": [{"closed": True, "knots": knots}]})]
    if ombra: s.append(cmd("layer.layerStyle.dropShadow", color="#000000", opacity=50, angle=120, distance=12, size=28))
    return s

def targa(nome, rect, radii=30, ombra="#0b2a00"):
    """Targa bianca arrotondata su cui appoggiare un logo che ha bisogno di fondo chiaro."""
    return [cmd("shape.create", kind="roundedRect", name=nome, rect=rect, radii=radii, fill="#ffffff", stroke=None),
            cmd("layer.layerStyle.dropShadow", color=ombra, opacity=35, angle=120, distance=8, size=26)]

def foto_sfondo(path, scale, center, knots, grad, angle, nome, velatura=0.75, luce=0.25):
    """Foto (già sfocata) estesa su una zona: ritagliata sulla forma (clipping) e velata nei colori del marchio
    con due riempimenti a gradiente ritagliati: uno in fusione Colore, uno leggero in normale."""
    velo = lambda suffisso, op, blend: [
        cmd("shape.create", kind="path", name=nome + suffisso, stroke=None,
            path={"subpaths": [{"closed": True, "knots": knots}]},
            fill={"gradient": {"stops": grad, "angle": angle, "style": "linear"}}),
        cmd("layer.createClippingMask"),
        cmd("layer.setProps", opacity=op, **({"blend": blend} if blend else {}))]
    return ([method("doc.place", path=path, scale=scale, center=center),
             cmd("layer.renameLayer", name=nome), cmd("layer.createClippingMask")]
            + velo(" (velatura)", velatura, "Color") + velo(" (luce)", luce, None))

# ---------------------------------------------------------------- scritte
def scritta_oro(testo, x, y, size, align, nome="Titolo", stops=ORO, stroke=ORO_SCURO, glow="#ffcf5a",
                font="Anton", pivot=None, rot=0, leading=None):
    """Titolo a grande impatto: Anton convertito in forma (per il gradiente a più tappe), rilievo cesellato,
    traccia scura, ombra netta e bagliore. Per un gradiente bianco/argento passa stops diversi."""
    extra = {"leading": leading} if leading else {}
    s = [cmd("type.create", x=x, y=y, text=testo, name=nome, font=font, size=size, align=align, color="#ffffff", **extra),
         cmd("type.convertToShape"),
         cmd("shape.edit", fill={"gradient": {"stops": stops, "angle": 90, "style": "linear"}}, stroke=None),
         cmd("layer.layerStyle.replace", effects=[
             {"kind": "dropShadow", "params": {"color": "#000000", "opacity": 80, "angle": 120, "distance": 16, "size": 12}},
             {"kind": "outerGlow", "params": {"color": glow, "opacity": 50, "size": 40}},
             {"kind": "bevelEmboss", "params": {"style": "inner", "technique": "chiselHard", "depth": 260, "size": 10, "soften": 1, "angle": 120, "altitude": 45}},
             {"kind": "stroke", "params": {"size": 6, "position": "outside", "color": stroke}}])]
    if pivot and rot: s.append(ruota(pivot, rot))
    return s

def scritta_corsiva(testo, x, y, size, align, nome="Sottotitolo", shadow="#000000", glow="#ffd97a", pivot=None, rot=0):
    """Riga d'accompagnamento in Kaushan Script bianco con ombra, bagliore e traccia sottile."""
    s = [cmd("type.create", x=x, y=y, text=testo, name=nome, font="Kaushan Script", size=size, align=align, color="#ffffff"),
         cmd("layer.layerStyle.replace", effects=[
             {"kind": "dropShadow", "params": {"color": shadow, "opacity": 70, "angle": 120, "distance": 8, "size": 12}},
             {"kind": "outerGlow", "params": {"color": glow, "opacity": 60, "size": 26}},
             {"kind": "stroke", "params": {"size": 3, "position": "outside", "color": shadow}}])]
    if pivot and rot: s.append(ruota(pivot, rot))
    return s

def scritta_spaziata(testo, x, y, size, align, nome="Riga", color="#ffffff", tracking=120, weight=700):
    """Riga in Montserrat maiuscolo spaziato (es. "E OTTIENI SUBITO IL", "IN COLLABORAZIONE CON")."""
    return [cmd("type.create", x=x, y=y, text=testo, name=nome, font="Montserrat", weight=weight, size=size,
                tracking=tracking, align=align, color=color),
            cmd("layer.layerStyle.replace", effects=[
                {"kind": "dropShadow", "params": {"color": "#000000", "opacity": 75, "angle": 120, "distance": 6, "size": 10}}])]

def scritta_bianca_filo_oro(testo, x, y, size, align, nome="Sito", font="Anton", tracking=30):
    """Testo bianco con un filo d'oro, senza ombre né luci (es. l'indirizzo web)."""
    return [cmd("type.create", x=x, y=y, text=testo, name=nome, font=font, size=size, tracking=tracking, align=align, color="#ffffff"),
            cmd("type.convertToShape"), cmd("shape.edit", fill="#ffffff", stroke=None),
            cmd("layer.layerStyle.replace", effects=[{"kind": "stroke", "params": {"size": 2, "position": "outside", "color": ORO_TESTO}}])]

def evidenzia(runs):
    """type.edit sui caratteri [start,end) in oro e grassetto: evidenzia parole dentro una riga."""
    return cmd("type.edit", runs=[{"start": a, "end": b, "color": ORO_TESTO, "weight": 800} for a, b in runs])

def badge_sigillo(center, d, titolo, sottotitolo, rot=-10, nome="Badge"):
    """Sigillo smerlato in oro metallico con centro scuro: per "OMAGGIO", "NOVITÀ", "-25%"..."""
    gira = ruota(center, rot)
    q = lambda dd: [center[0] - dd // 2, center[1] - dd // 2, dd, dd]
    return [
        cmd("shape.create", kind="star", name=nome + " (sigillo)", rect=q(d), sides=30, starRatio=0.9,
            fill={"gradient": {"stops": ORO, "angle": 60, "style": "linear"}}, stroke={"width": 2, "color": ORO_SCURO, "align": "inside"}),
        cmd("layer.layerStyle.replace", effects=[
            {"kind": "dropShadow", "params": {"color": "#000000", "opacity": 80, "angle": 120, "distance": 10, "size": 20}},
            {"kind": "bevelEmboss", "params": {"style": "inner", "technique": "smooth", "depth": 160, "size": 6, "angle": 120, "altitude": 45}}]), gira,
        cmd("shape.create", kind="ellipse", name=nome + " (centro)", rect=q(d - 44),
            fill={"gradient": {"stops": [[0, "#4a3612"], [1, "#0e0902"]], "style": "radial", "angle": 0}},
            stroke={"width": 3, "color": "#fff3c4", "align": "inside"}),
        cmd("layer.layerStyle.innerShadow", color="#000000", opacity=60, angle=120, distance=4, size=10), gira,
        cmd("type.create", x=center[0], y=center[1] - 2, text=titolo, name=nome + ": " + titolo, font="Anton", size=round(d * 0.058, 1),
            align="center", color="#ffffff"),
        cmd("type.convertToShape"), cmd("shape.edit", fill={"gradient": {"stops": ORO, "angle": 90, "style": "linear"}}, stroke=None),
        cmd("layer.layerStyle.replace", effects=[
            {"kind": "dropShadow", "params": {"color": "#000000", "opacity": 80, "angle": 120, "distance": 4, "size": 4}},
            {"kind": "stroke", "params": {"size": 2, "position": "outside", "color": "#2a1d00"}}]), gira,
        # il sottotitolo deve restare dentro la corda del cerchio scuro: piccolo e poco spaziato, altrimenti finisce sull'oro
        cmd("type.create", x=center[0], y=center[1] + round(d * 0.13), text=sottotitolo, name=nome + ": " + sottotitolo, font="Inter",
            weight=700, size=round(d * 0.02, 1), tracking=40, align="center", color="#ffffff"), gira,
    ]

# ---------------------------------------------------------------- prodotti su un piano
def bbox_opaco(path, soglia=128):
    """Bounding box della parte opaca di un PNG con alfa (ignora aloni semitrasparenti)."""
    from PIL import Image
    im = Image.open(path).convert("RGBA")
    return im.getchannel("A").point(lambda v: 255 if v > soglia else 0).getbbox(), im.size

def prodotti_su_piano(prodotti, base_y, bordo_piano, px_per_cm, centro_x, gap=50):
    """Confezioni (PNG con alfa) in fila su un piano, in proporzione reale (altezza in cm), appoggiate:
    riflesso debole specchiato sotto la linea d'appoggio, ombra ampia + ombra di contatto, base scurita.
    prodotti = [(path, altezza_cm), ...] da sinistra a destra."""
    mis = []
    for path, cm in prodotti:
        (x0, y0, x1, y1), (W, H) = bbox_opaco(path)
        s = cm * px_per_cm / (y1 - y0)
        mis.append(dict(path=path, s=s, W=W, H=H, bw=(x1 - x0) * s, bh=(y1 - y0) * s,
                        dx=((x0 + x1) / 2 - W / 2) * s, dy=(y1 - H / 2) * s, nome=os.path.basename(path).rsplit(".", 1)[0]))
    x = centro_x - (sum(m["bw"] for m in mis) + gap * (len(mis) - 1)) / 2
    steps = []
    for m in mis:
        cx = x + m["bw"] / 2; x += m["bw"] + gap
        centro = [round(cx - m["dx"]), round(base_y - m["dy"])]
        rifl = [centro[0], round(2 * base_y - centro[1])]
        steps += [
            method("doc.place", path=m["path"], scale=m["s"] * 100, center=rifl),
            cmd("layer.renameLayer", name=f"Riflesso {m['nome']}"), cmd("edit.transform.flipVertical"),
            cmd("layer.layerMask.revealAll"),
            {"cmd": "paint.gradient", "params": {"from": [round(cx), base_y + 2], "to": [round(cx), bordo_piano - 12],
                                                  "style": "linear", "colors": ["#a8a8a8", "#000000"], "target": "mask"}, "continue": True},
            cmd("select.rect", x=0, y=0, width=10000, height=base_y + 1), cmd("edit.fill", contents="black", target="mask"),
            {"cmd": "select.deselect", "params": {}, "continue": True},
            cmd("layer.setProps", opacity=0.12),
            cmd("shape.create", kind="ellipse", name=f"Ombra ampia {m['nome']}", stroke=None,
                rect=[round(cx - m["bw"] / 2 - 30), base_y - 18, round(m["bw"] + 60), 48],
                fill={"gradient": {"stops": [[0, "#000000"], [0.5, "#505050"], [1, "#ffffff"]], "style": "radial", "angle": 0}}),
            cmd("layer.setProps", opacity=0.85, blend="Multiply"),
            cmd("shape.create", kind="ellipse", name=f"Ombra contatto {m['nome']}", stroke=None,
                rect=[round(cx - m["bw"] / 2 - 4), base_y - 8, round(m["bw"] + 8), 18],
                fill={"gradient": {"stops": [[0, "#000000"], [0.7, "#303030"], [1, "#ffffff"]], "style": "radial", "angle": 0}}),
            cmd("layer.setProps", opacity=1.0, blend="Multiply"),
            method("doc.place", path=m["path"], scale=m["s"] * 100, center=centro),
            cmd("layer.renameLayer", name=m["nome"]),
            cmd("layer.layerMask.revealAll"),                                 # via l'ombra grigia incorporata nel PNG
            cmd("select.rect", x=0, y=base_y + 1, width=10000, height=10000), cmd("edit.fill", contents="black", target="mask"),
            {"cmd": "select.deselect", "params": {}, "continue": True},
            cmd("shape.create", kind="rect", name=f"Base in ombra {m['nome']}", stroke=None,
                rect=[round(cx - m["bw"] / 2 - 2), round(base_y - m["bh"] * 0.14), round(m["bw"] + 4), round(m["bh"] * 0.14) + 2],
                fill={"gradient": {"stops": [[0, "#ffffff"], [1, "#000000"]], "style": "linear", "angle": -90}}),
            cmd("layer.createClippingMask"), cmd("layer.setProps", opacity=0.55, blend="Multiply"),
        ]
    return steps, mis

# ---------------------------------------------------------------- misure reali del testo (per centrare)
def misura_bounds(specs, base="lavoro/base-a6.pcraft"):
    """Crea ogni riga in un documento di prova (x=0, linea di base y=500) e restituisce i bounds reali
    [x0,y0,x1,y1] di type.create: servono per centrare un blocco di testo con precisione.
    `specs` = lista di dict con i parametri di type.create (text, font, size, align, ...)."""
    passi = [method("doc.open", path=base)] + [cmd("type.create", x=0, y=500, **sp) for sp in specs]
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f: json.dump(passi, f); tmp = f.name
    out = subprocess.run([sys.executable, "-I", os.path.join(os.path.dirname(os.path.abspath(__file__)), "pc.py"), tmp],
                         capture_output=True, text=True).stdout
    bounds = [json.loads(m.group(1))["result"]["bounds"] for m in re.finditer(r"^\[\d+\] type.create: (\{.*\})$", out, re.M)]
    os.unlink(tmp); assert len(bounds) == len(specs), out[-800:]
    return bounds

def blocco_centrato(righe, centro, base="lavoro/base-a6.pcraft"):
    """righe = [(spec_type_create, distanza_dalla_riga_precedente_px, [(a,b) da evidenziare in oro]), ...].
    Restituisce i passi per creare il blocco con il bordo sinistro allineato e centrato sul punto `centro`."""
    specs = [r[0] for r in righe]
    bs = misura_bounds(specs, base)
    largh = max(b[2] - b[0] for b in bs); alt = sum(r[1] for r in righe) + (bs[0][3] - bs[0][1])
    sinistra = round(centro[0] - largh / 2); y = round(centro[1] - alt / 2) + (500 - bs[0][1])
    steps = []
    for (sp, dist, oro), b in zip(righe, bs):
        y += dist
        steps.append(cmd("type.create", x=sinistra - b[0], y=y, name="Blocco: " + sp["text"][:30], **sp))
        if oro: steps.append(evidenzia(oro))
    return steps

def colore_medio(path, box):
    """Colore medio (#rrggbb) di una porzione di immagine: utile per riempire buchi con i colori accanto."""
    from PIL import Image
    im = Image.open(path).convert("RGB").crop(box)
    px = list(im.get_flattened_data()) if hasattr(im, "get_flattened_data") else list(im.getdata())
    return "#%02x%02x%02x" % tuple(sum(c[i] for c in px) // len(px) for i in range(3))
