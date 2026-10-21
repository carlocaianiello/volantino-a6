#!/usr/bin/env bash
# File per la tipografia: PDF a 300 dpi con abbondanza, senza crocini, CMYK Coated FOGRA39 (ISO Coated v2),
# immagine senza perdita, profilo incorporato. Un PDF per lato, più un PDF unico a più pagine, più in alternative/
# TIFF CMYK e PDF RGB, più una prova colore a video (CMYK riportato in sRGB) per ogni lato.
# Uso:  esporta-stampa.sh [-o export/stampa] [-n volantino-a6] lavoro/fronte.pcraft lavoro/retro.pcraft
set -euo pipefail
QUI="$(cd "$(dirname "$0")/.." && pwd)"
OUT=export/stampa; NOME=volantino
while getopts "o:n:" opt; do case $opt in o) OUT=$OPTARG;; n) NOME=$OPTARG;; esac; done; shift $((OPTIND-1))
[ $# -ge 1 ] || { echo "uso: $0 [-o cartella] [-n nome] lato1.pcraft [lato2.pcraft ...]"; exit 2; }
mkdir -p "$OUT/alternative"
PROFILO="$QUI/assets/profili/craft-coated-fogra39.icc"
CMYK='{"profile":"'$PROFILO'","intent":"relative","bpc":true}'
PDFS=()
for src in "$@"; do
  lato=$(basename "${src%.*}")
  photocraft-cli run "$src" --cmd layer.flattenImage --cmd image.mode.cmyk --params "$CMYK" --out "$OUT/$NOME-$lato.pdf" 2>/dev/null >/dev/null
  photocraft-cli run "$src" --cmd layer.flattenImage --cmd image.mode.cmyk --params "$CMYK" --out "$OUT/alternative/$NOME-$lato-cmyk.tif" 2>/dev/null >/dev/null
  photocraft-cli convert "$src" "$OUT/alternative/$NOME-$lato-rgb.pdf" 2>/dev/null >/dev/null
  PDFS+=("$OUT/$NOME-$lato.pdf")
done
python3 - "$OUT" "$NOME" "${PDFS[@]}" <<'PY'
import sys, io, os
out, nome, pdfs = sys.argv[1], sys.argv[2], sys.argv[3:]
try:
    from pypdf import PdfWriter, PdfReader
    if len(pdfs) > 1:
        w = PdfWriter()
        for f in pdfs:
            for p in PdfReader(f).pages: w.add_page(p)
        w.write(f"{out}/{nome}-completo.pdf"); print(f"{out}/{nome}-completo.pdf: {len(pdfs)} pagine")
except ImportError:
    print("pypdf non installato (pip install pypdf): salto il PDF unico a più pagine")
try:
    from PIL import Image, ImageCms
    for f in pdfs:
        lato = os.path.basename(f)[len(nome) + 1:-4]
        im = Image.open(f"{out}/alternative/{nome}-{lato}-cmyk.tif")
        src = ImageCms.ImageCmsProfile(io.BytesIO(im.info["icc_profile"]))
        rgb = ImageCms.profileToProfile(im, src, ImageCms.createProfile("sRGB"), outputMode="RGB",
                                        renderingIntent=ImageCms.Intent.RELATIVE_COLORIMETRIC)
        rgb.save(f"{out}/prova-colore-{lato}.png", dpi=(300, 300))
except ImportError:
    print("Pillow non installato: salto le prove colore")
PY
cat > "$OUT/LEGGIMI.txt" <<TXT
File per la stampa ($NOME)
- Un PDF per lato, 1 pagina ciascuno, alla misura del formato + 3 mm di abbondanza per lato. Nessun crocino.
- 300 dpi, immagine senza perdita. Colore CMYK, profilo Coated FOGRA39 (equivalente a ISO Coated v2) incorporato.
- $NOME-completo.pdf: tutti i lati in un unico PDF, una pagina per lato, nell'ordine dato.
- alternative/: TIFF CMYK 300 dpi con profilo e PDF in RGB (sRGB), se la tipografia li preferisce.
- prova-colore-*.png: resa a video del CMYK, per controllo; non sono file di stampa.
TXT
ls -la "$OUT"
