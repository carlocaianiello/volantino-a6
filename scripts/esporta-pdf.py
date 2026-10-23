#!/usr/bin/env python3
"""Esporta il volantino A6 (fronte e retro) in un PDF pronto per la tipografia.

Pipeline:
  lavoro/fronte.pcraft, lavoro/retro.pcraft
    -> photocraft-cli convert -> export/fronte.png, export/retro.png
       (1311 x 1819 px = 111 x 154 mm a 300 dpi: A6 + 3 mm di abbondanza per lato)
    -> export/volantino-a6-stampa.pdf: 2 pagine da 111 x 154 mm, immagini
       incorporate senza perdita, BleedBox = pagina, TrimBox = 105 x 148 mm.
    -> export/anteprima-fronte.jpg, export/anteprima-retro.jpg (ridotte, per controllo)

Con --crocini produce anche export/volantino-a6-stampa-crocini.pdf: pagina
121 x 164 mm con 5 mm di margine bianco e crocini di taglio fuori dall'abbondanza.

Uso:
  python3 scripts/esporta-pdf.py            # convert + PDF + anteprime
  python3 scripts/esporta-pdf.py --solo-pdf # riusa i PNG già in export/ (senza la CLI)
  python3 scripts/esporta-pdf.py --crocini  # in più, la versione con i crocini
"""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image
from pypdf import PdfReader, PdfWriter
from pypdf.generic import RectangleObject
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

RADICE = Path(__file__).resolve().parent.parent
LAVORO = RADICE / "lavoro"
EXPORT = RADICE / "export"

DPI = 300
ABBONDANZA_MM = 3
RIFILO_MM = (105, 148)                     # A6
PAGINA_MM = (RIFILO_MM[0] + 2 * ABBONDANZA_MM, RIFILO_MM[1] + 2 * ABBONDANZA_MM)  # 111 x 154
PX_ATTESI = (round(PAGINA_MM[0] / 25.4 * DPI), round(PAGINA_MM[1] / 25.4 * DPI))  # 1311 x 1819
PAGINE = ("fronte", "retro")

MARGINE_CROCINI_MM = 5   # bianco oltre l'abbondanza, dove stanno i crocini
LUNGHEZZA_CROCINO_MM = 4


def converti(nome: str) -> Path:
    """Esporta lavoro/<nome>.pcraft in export/<nome>.png con photocraft-cli."""
    sorgente = LAVORO / f"{nome}.pcraft"
    png = EXPORT / f"{nome}.png"
    if not sorgente.is_file():
        sys.exit(f"manca {sorgente.relative_to(RADICE)}: il volantino non è ancora impaginato")
    if shutil.which("photocraft-cli") is None:
        sys.exit("photocraft-cli non trovato: esegui scripts/installa-artcraft.sh "
                 "oppure usa --solo-pdf con i PNG già in export/")
    r = subprocess.run(["photocraft-cli", "convert", str(sorgente), str(png)],
                       capture_output=True, text=True)
    if r.stderr.strip():
        print(r.stderr.strip(), file=sys.stderr)   # font mancanti ecc.
    if r.returncode != 0:
        sys.exit(f"convert di {sorgente.name} fallito (codice {r.returncode})")
    return png


def controlla(png: Path) -> Image.Image:
    """Apre il PNG, verifica le dimensioni e lo appiattisce su bianco."""
    img = Image.open(png)
    if img.size != PX_ATTESI:
        sys.exit(f"{png.name}: {img.size[0]} x {img.size[1]} px, attesi "
                 f"{PX_ATTESI[0]} x {PX_ATTESI[1]} (A6 + abbondanza a {DPI} dpi)")
    dpi = img.info.get("dpi")
    if dpi and round(dpi[0]) != DPI:
        print(f"avviso: {png.name} dichiara {round(dpi[0])} dpi, nel PDF verrà "
              f"comunque posato a {DPI} dpi ({PAGINA_MM[0]} x {PAGINA_MM[1]} mm)", file=sys.stderr)
    if img.mode in ("RGBA", "LA", "P"):
        img = img.convert("RGBA")
        fondo = Image.new("RGB", img.size, "white")
        fondo.paste(img, mask=img.getchannel("A"))
        img = fondo
    elif img.mode != "RGB":
        img = img.convert("RGB")
    return img


def anteprima(nome: str, img: Image.Image) -> Path:
    out = EXPORT / f"anteprima-{nome}.jpg"
    piccola = img.copy()
    piccola.thumbnail((PX_ATTESI[0] // 2, PX_ATTESI[1] // 2))
    piccola.save(out, quality=88)
    return out


def crocini(c: canvas.Canvas, x0: float, y0: float, w: float, h: float) -> None:
    """Crocini di taglio agli angoli del rettangolo di rifilo (x0, y0, w, h in punti)."""
    gap = ABBONDANZA_MM * mm
    lung = LUNGHEZZA_CROCINO_MM * mm
    c.setLineWidth(0.25)
    c.setStrokeColorRGB(0, 0, 0)
    for x in (x0, x0 + w):
        for y in (y0, y0 + h):
            sx = -1 if x == x0 else 1
            sy = -1 if y == y0 else 1
            c.line(x, y + sy * gap, x, y + sy * (gap + lung))          # verticale
            c.line(x + sx * gap, y, x + sx * (gap + lung), y)          # orizzontale


def scrivi_pdf(immagini: dict, out: Path, con_crocini: bool) -> None:
    margine = (MARGINE_CROCINI_MM * mm) if con_crocini else 0
    pw, ph = PAGINA_MM[0] * mm + 2 * margine, PAGINA_MM[1] * mm + 2 * margine
    abb = ABBONDANZA_MM * mm
    tmp = out.with_suffix(".tmp")

    c = canvas.Canvas(str(tmp), pagesize=(pw, ph))
    c.setTitle("Volantino A6 - fronte e retro")
    c.setPageCompression(1)
    for nome in PAGINE:
        img_tmp = EXPORT / f".{nome}-piatto.tmp"
        immagini[nome].save(img_tmp, format="PNG")      # RGB senza alfa: incorporato Flate (lossless)
        c.drawImage(str(img_tmp), margine, margine,
                    width=PAGINA_MM[0] * mm, height=PAGINA_MM[1] * mm)
        img_tmp.unlink()
        if con_crocini:
            crocini(c, margine + abb, margine + abb, RIFILO_MM[0] * mm, RIFILO_MM[1] * mm)
        c.showPage()
    c.save()

    # Box di stampa: BleedBox = immagine con abbondanza, TrimBox = A6 rifilato.
    reader = PdfReader(str(tmp))
    writer = PdfWriter()
    for page in reader.pages:
        page.bleedbox = RectangleObject([margine, margine, pw - margine, ph - margine])
        page.trimbox = RectangleObject([margine + abb, margine + abb,
                                        pw - margine - abb, ph - margine - abb])
        page.artbox = page.trimbox
        writer.add_page(page)
    writer.add_metadata({"/Title": "Volantino A6 - fronte e retro",
                         "/Subject": f"A6 {RIFILO_MM[0]}x{RIFILO_MM[1]} mm + {ABBONDANZA_MM} mm abbondanza, {DPI} dpi"})
    with open(out, "wb") as f:
        writer.write(f)
    tmp.unlink()


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--solo-pdf", action="store_true", help="non lanciare photocraft-cli, usa export/*.png")
    ap.add_argument("--crocini", action="store_true", help="produci anche la versione con i crocini")
    a = ap.parse_args()

    EXPORT.mkdir(exist_ok=True)
    immagini = {}
    for nome in PAGINE:
        png = (EXPORT / f"{nome}.png") if a.solo_pdf else converti(nome)
        if not png.is_file():
            sys.exit(f"manca {png.relative_to(RADICE)}")
        immagini[nome] = controlla(png)
        print(f"{nome}: {png.relative_to(RADICE)} ok ({PX_ATTESI[0]} x {PX_ATTESI[1]} px) "
              f"-> {anteprima(nome, immagini[nome]).relative_to(RADICE)}")

    pdf = EXPORT / "volantino-a6-stampa.pdf"
    scrivi_pdf(immagini, pdf, con_crocini=False)
    print(f"PDF tipografia: {pdf.relative_to(RADICE)} "
          f"({PAGINA_MM[0]} x {PAGINA_MM[1]} mm, TrimBox {RIFILO_MM[0]} x {RIFILO_MM[1]} mm, 2 pagine)")
    if a.crocini:
        pdf2 = EXPORT / "volantino-a6-stampa-crocini.pdf"
        scrivi_pdf(immagini, pdf2, con_crocini=True)
        print(f"PDF con crocini: {pdf2.relative_to(RADICE)}")


if __name__ == "__main__":
    main()
