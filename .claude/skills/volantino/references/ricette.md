# Ricette: come si costruisce un lato

Una ricetta è una lista JSON di passi eseguiti in ordine da `scripts/pc.py` (o dai tool MCP `doc_*`/`command_run`).
Scrivila con un piccolo script Python che importa `scripts/ricetta.py`, così misure e ripetizioni restano calcolate.
Gli esempi completi sono in `references/esempi/`: `genera_fronte.py` (fronte a livelli con due mondi, scritte
inclinate, figure ritagliate), `genera_retro.py` (scena generata + prodotti veri + scritta centrale + badge +
footer misurato + QR), `fronte-ai.json` (immagine generata adattata al formato con footer rifatto).

## Scheletro

```python
import sys; sys.path.insert(0, "<skill>/scripts"); from ricetta import *
steps = [method("doc.open", path="lavoro/base-a6.pcraft")]
# ... fondi, foto, loghi, scritte, footer ...
steps += [{"cmd": "layer.list", "params": {}},
          method("doc.save", path="lavoro/fronte.pcraft"),
          method("doc.save", path="export/anteprima-fronte.png"),
          cmd("image.crop", x=35, y=35, width=1241, height=1749),      # anteprima rifilata (A6)
          method("doc.save", path="export/anteprima-fronte-rifilata.png")]
salva(steps, "scripts/fronte.json")
```

Ordine dei livelli = ordine dei passi (ogni passo crea sopra al precedente). Metti il footer bianco per ultimo
se deve coprire gambe o oggetti.

## Mattoni (in `ricetta.py`)

| Funzione | Cosa fa |
|---|---|
| `zona(nome, knots, grad, angle)` | area a gradiente con contorno poligonale (zone, diagonali) |
| `separatore(nome, knots)` | striscia bianca con ombra tra due zone |
| `targa(nome, rect)` | targa bianca arrotondata per un logo |
| `foto_sfondo(path, scale, center, knots, grad, angle, nome)` | foto sfocata estesa sulla zona + velature colore |
| `scritta_oro(testo, x, y, size, align, ...)` | titolo Anton oro metallico (o altri stops) con rilievo, traccia, ombra, bagliore |
| `scritta_corsiva(...)` | riga Kaushan Script luminosa |
| `scritta_spaziata(...)` | riga Montserrat maiuscola spaziata |
| `scritta_bianca_filo_oro(...)` | testo bianco con filo d'oro, senza effetti |
| `evidenzia([(a,b),...])` | parole in oro dentro una riga (type.edit runs) |
| `badge_sigillo(center, d, titolo, sottotitolo)` | sigillo smerlato oro con centro scuro |
| `prodotti_su_piano([(png, cm),...], base_y, bordo, px_per_cm, centro_x)` | confezioni in proporzione reale, appoggiate con ombre e riflesso |
| `misura_bounds(specs)` / `blocco_centrato(righe, centro)` | misure reali del testo e blocco centrato |
| `rot_matrix(deg, px, py)` / `ruota(pivot, deg)` | rotazione attorno a un perno comune |
| `colore_medio(path, box)` | colore medio di una porzione di immagine |

## Pezzi da ricordare (parametri dei comandi engine)

- `type.create {x, y (linea di base), text, font, size pt, color, align, weight, tracking, leading, box:[x,y,w,h]}`;
  `\n` nel testo fa più righe. `type.edit {runs:[{start,end,color,size,weight}]}` cambia porzioni.
  `type.fonts {family}` elenca le facce installate.
- `shape.create {kind: rect|roundedRect|ellipse|polygon|star|line|path, rect|path, fill: "#hex"|{gradient:{stops,angle,style}}|null, stroke:{width,color,align}}`;
  `shape.edit` cambia fill/stroke di una forma esistente (anche di un testo convertito).
- `layer.layerStyle.replace {effects:[{kind, params}]}` sostituisce tutti gli effetti; `layer.layerStyle.<kind>` ne aggiunge uno.
  Kind: dropShadow, innerShadow, outerGlow, innerGlow, bevelEmboss, stroke, colorOverlay, gradientOverlay, satin.
- `layer.setProps {opacity 0..1, blend, visible, name}`; `layer.createClippingMask` ritaglia il livello su quello sotto.
- `doc.place {path, scale %, center:[x,y]}` inserisce un file come oggetto avanzato (restituisce i bounds);
  `layer.renameLayer {name}` subito dopo.
- Selezioni: `select.subject`, `select.object {rect|point}`, `select.rect {x,y,width,height,feather,mode}`,
  `select.lasso {points}`, `select.colorRange {color,fuzziness}`, `select.modify.expand|contract|feather {radius}`,
  `select.inverse`, `select.deselect` (errore se vuota).
- Maschere: `layer.layerMask.revealSelection|revealAll`, `edit.fill {contents:black|white, target:"mask"}`,
  `paint.gradient {from,to,colors,target:"mask"}`.
- Pixel: `edit.deleteAndFillSelection`, `edit.contentAwareFill {sampling:auto|custom, area}`,
  `filter.blur.gaussianBlur {radius}`, `image.adjustments.hueSaturation {reds|greens|blues|...:{hue,saturation,lightness}}`.
- Geometria: `edit.transform {matrix|rotate|scaleX|dx|dy}`, `edit.transform.flipVertical`, `image.crop {x,y,width,height}`,
  `image.imageSize {width,height,resolution,resample}`, `image.canvasSize {width,height,anchor,extensionColor}`.
- Guide: `view.newGuide {orientation, position, color}`.
- Esportazione: `doc.save {path}` (estensione = formato: pcraft, png, tif, jpg, pdf); `layer.flattenImage`;
  `image.mode.cmyk {profile, intent, bpc}` (solo CLI con profilo su file).

## Adattare un'immagine generata al formato (fronte-ai.json)

`doc.open` → `image.imageSize` alla larghezza del file (o altezza) a 300 dpi → `image.canvasSize` alla misura
con abbondanza, ancorata al centro → `select.rect` sulle bande aggiunte + `edit.contentAwareFill` (o `edit.fill`
bianco/nero se la banda è piatta) → guide → footer rifatto con testo e loghi veri → salva. Controlla che i
contenuti dell'immagine restino a 95 px dal bordo; se un elemento decorativo sfora, dillo all'utente.
