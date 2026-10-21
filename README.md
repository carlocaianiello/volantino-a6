# Volantino A6

Volantino in formato A6 realizzato con le app open source della suite
[ArtCraft](https://github.com/storytold) (PhotoCraft & co.), pilotate da Claude
tramite i loro server MCP in modalità headless (senza interfaccia grafica).
Funziona sia in locale sia nelle sessioni cloud di Claude Code.

## Specifiche di stampa

| | mm | px a 300 dpi |
|---|---|---|
| Formato rifilato A6 | 105 × 148 | 1240 × 1748 |
| Con abbondanza 3 mm per lato | 111 × 154 | 1311 × 1819 |
| Margine di sicurezza (testi) | 5 mm dal rifilo, 8 mm dal bordo esterno | ~95 px dal bordo del file |

- Risoluzione: 300 dpi
- Lavorazione in RGB; conversione in CMYK da concordare con la tipografia
- Fronte e retro: due file separati

## Struttura

```
risorse/   immagini, loghi, font e testi forniti
lavoro/    file sorgente modificabili (.pcraft / .psd)
export/    file finali per la stampa (PDF/TIFF/PNG) e anteprime
scripts/   installa-artcraft.sh: compila e installa le CLI ArtCraft
           installa-font.sh: installa i font di risorse/font per PhotoCraft
           pc.py: esegue una lista di passi JSON su `photocraft-cli serve`
           fronte.json: ricetta che ricostruisce lavoro/fronte.pcraft da lavoro/base-a6.pcraft
.mcp.json  registra il server MCP di PhotoCraft per Claude Code
```

## Preparare l'ambiente

### Sessione cloud di Claude Code

Nelle impostazioni dell'ambiente cloud (menu dell'ambiente nella barra del
titolo → Edit → **Setup script**) incollare il contenuto di
`scripts/installa-artcraft.sh` (non dipende dal repo, quindi funziona anche se è privato).

In alternativa, con il repo già nella sessione, eseguire una volta
`bash scripts/installa-artcraft.sh` e poi aprire una **nuova sessione**: i server
MCP vengono caricati solo all'avvio.

### In locale

Scaricare PhotoCraft (comprende `photocraft-cli`) dalle
[release](https://github.com/storytold/photocraft/releases) oppure usare lo
script qui sopra, poi aprire Claude Code nella cartella del repo.

## Comandi utili

```bash
# nuovo documento A6 con abbondanza, fondo bianco, 300 dpi
photocraft-cli run --new '{"width":1311,"height":1819,"background":"white","resolution":300}' --out lavoro/fronte.pcraft

# informazioni su un file (dimensioni, livelli)
photocraft-cli info lavoro/fronte.pcraft --compact

# esportare
photocraft-cli convert lavoro/fronte.pcraft export/fronte.png

# ricostruire il fronte dalla ricetta (apre la base, crea livelli, salva sorgente e anteprima)
python3 scripts/pc.py scripts/fronte.json
```
