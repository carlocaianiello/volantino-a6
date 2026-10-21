#!/usr/bin/env bash
# Produce i file per la tipografia in export/stampa/ a partire da lavoro/fronte.pcraft e lavoro/retro.pcraft:
#   volantino-a6-fronte.pdf, volantino-a6-retro.pdf   PDF 300 dpi, 111 x 154 mm (A6 + 3 mm di abbondanza per lato),
#                                                      senza crocini, CMYK Coated FOGRA39 (ISO Coated v2), immagine senza perdita
#   volantino-a6-fronte-retro.pdf                      gli stessi due in un unico PDF a due pagine
#   alternative/                                        TIFF CMYK e PDF RGB (sRGB), se la tipografia li preferisce
#   ../anteprima-stampa-<lato>.png                      prova colore a video: il CMYK riportato in sRGB
set -euo pipefail
cd "$(dirname "$0")/.."
OUT=export/stampa; mkdir -p "$OUT/alternative"
PROFILO=risorse/profili/craft-coated-fogra39.icc
CMYK='{"profile":"'$PROFILO'","intent":"relative","bpc":true}'
for lato in fronte retro; do
  src=lavoro/$lato.pcraft
  photocraft-cli run "$src" --cmd layer.flattenImage --cmd image.mode.cmyk --params "$CMYK" --out "$OUT/volantino-a6-$lato.pdf" >/dev/null
  photocraft-cli run "$src" --cmd layer.flattenImage --cmd image.mode.cmyk --params "$CMYK" --out "$OUT/alternative/volantino-a6-$lato-cmyk.tif" >/dev/null
  photocraft-cli convert "$src" "$OUT/alternative/volantino-a6-$lato-rgb.pdf" >/dev/null
done
python3 -I - "$OUT" <<'PY'
import sys, io
from pypdf import PdfWriter, PdfReader
from PIL import Image, ImageCms
out = sys.argv[1]
w = PdfWriter()
for lato in ("fronte", "retro"):
    for p in PdfReader(f"{out}/volantino-a6-{lato}.pdf").pages: w.add_page(p)
w.add_metadata({"/Title": "Volantino A6 Nutrihangar - fronte e retro", "/Subject": "A6 + 3 mm abbondanza, 300 dpi, CMYK Coated FOGRA39"})
w.write(f"{out}/volantino-a6-fronte-retro.pdf")
# prova colore a video
for lato in ("fronte", "retro"):
    im = Image.open(f"{out}/alternative/volantino-a6-{lato}-cmyk.tif")
    src = ImageCms.ImageCmsProfile(io.BytesIO(im.info["icc_profile"]))
    rgb = ImageCms.profileToProfile(im, src, ImageCms.createProfile("sRGB"), outputMode="RGB",
                                    renderingIntent=ImageCms.Intent.RELATIVE_COLORIMETRIC)
    rgb.save(f"export/anteprima-stampa-{lato}.png", dpi=(300, 300))
PY
cat > "$OUT/LEGGIMI.txt" <<'TXT'
Volantino A6 Nutrihangar - file per la stampa

volantino-a6-fronte.pdf, volantino-a6-retro.pdf
  PDF, 1 pagina ciascuno, 111 x 154 mm = A6 (105 x 148) + 3 mm di abbondanza per lato.
  Rifilare a 105 x 148 mm. Nessun crocino di taglio. 300 dpi, immagine senza perdita.
  Colore: CMYK, profilo Coated FOGRA39 (equivalente a ISO Coated v2) incorporato.
volantino-a6-fronte-retro.pdf
  Gli stessi due lati in un unico PDF a due pagine (pagina 1 fronte, pagina 2 retro).
alternative/
  TIFF CMYK 300 dpi con profilo incorporato e PDF in RGB (sRGB), se la tipografia li preferisce.
TXT
ls -la "$OUT" "$OUT/alternative"
for f in "$OUT"/*.pdf; do printf '%s: ' "$(basename "$f")"; pdfinfo "$f" | grep -E "Pages|Page size" | tr -s ' ' | tr '\n' ' '; echo; done
