#!/usr/bin/env python3
"""Crea il file base di un volantino: formato + abbondanza, 300 dpi, fondo bianco, guide di rifilo (rosse)
e di area sicura (verdi).  Stampa anche le misure in px da usare nelle ricette.

Uso:  python3 nuova_base.py --formato A6 --out lavoro/base-a6.pcraft
      python3 nuova_base.py --mm 100x210 --abbondanza 3 --sicurezza 5 --dpi 300 --out lavoro/base-dl.pcraft
      python3 nuova_base.py --formato A5 --sfondo '#000000' --out lavoro/base.pcraft"""
import argparse, json, subprocess, sys

FORMATI = {"A7": (74, 105), "A6": (105, 148), "A5": (148, 210), "A4": (210, 297), "DL": (99, 210),
           "10x15": (100, 150), "biglietto": (85, 55)}

def px(mm, dpi): return round(mm / 25.4 * dpi)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--formato", help="|".join(FORMATI))
    ap.add_argument("--mm", help="larghezza x altezza del formato rifilato, es. 105x148")
    ap.add_argument("--abbondanza", type=float, default=3, help="mm per lato (default 3)")
    ap.add_argument("--sicurezza", type=float, default=5, help="mm dal rifilo per testi e loghi (default 5)")
    ap.add_argument("--dpi", type=int, default=300)
    ap.add_argument("--sfondo", default="white", help="white | black | transparent | #rrggbb")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    if a.mm: w_mm, h_mm = (float(v) for v in a.mm.lower().split("x"))
    elif a.formato: w_mm, h_mm = FORMATI[a.formato.upper() if a.formato.upper() in FORMATI else a.formato]
    else: ap.error("indica --formato o --mm")
    W, H = px(w_mm + 2 * a.abbondanza, a.dpi), px(h_mm + 2 * a.abbondanza, a.dpi)
    ab, sic = px(a.abbondanza, a.dpi), px(a.abbondanza + a.sicurezza, a.dpi)
    cmd = ["photocraft-cli", "run", "--new", json.dumps({"width": W, "height": H, "background": a.sfondo, "resolution": a.dpi})]
    for o, p, c in [("vertical", ab, "lightRed"), ("vertical", W - ab, "lightRed"), ("horizontal", ab, "lightRed"), ("horizontal", H - ab, "lightRed"),
                    ("vertical", sic, "green"), ("vertical", W - sic, "green"), ("horizontal", sic, "green"), ("horizontal", H - sic, "green")]:
        cmd += ["--cmd", "view.newGuide", "--params", json.dumps({"orientation": o, "position": p, "color": c})]
    cmd += ["--out", a.out]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL)
    print(f"{a.out}: {W} x {H} px a {a.dpi} dpi ({w_mm + 2*a.abbondanza:g} x {h_mm + 2*a.abbondanza:g} mm con abbondanza)")
    print(f"rifilo a {ab} px dal bordo; area sicura per testi e loghi: x {sic}..{W - sic}, y {sic}..{H - sic}")
    print(f"centro pagina: ({W/2:g}, {H/2:g});  1 mm = {a.dpi/25.4:.2f} px;  1 cm = {px(10, a.dpi)} px")

if __name__ == "__main__": main()
