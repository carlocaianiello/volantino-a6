# Immagini generate dall'IA: come chiederle e come usarle

Le immagini le genera l'utente (Higgsfield, o un altro generatore) a partire da prompt che scrivi tu, e te le
incolla in chat. Se nella sessione locale esiste un connettore di generazione già autorizzato, usalo tu, ma
senza scaricare immagini da link esterni se la rete non lo consente: fattele allegare.

Scrivi i prompt in inglese (i modelli rispondono meglio), in un blocco di codice pronto da copiare, e dì sempre
all'utente formato (3:4 o 4:5 verticale per A6/A5), risoluzione (la massima) e cosa controllare nel risultato.

## Tecnica 1 — Figure da ritagliare: fondo piatto, non "trasparente"

Chiedere "transparent background" non funziona: molti modelli lo ignorano. Chiedi un fondo piatto di un colore
assente dal soggetto (blu puro per una persona con top verde e leggings bianchi, verde puro per un atleta in
pantaloncini scuri), figura intera, niente ombra a terra, niente oggetti tagliati dal bordo, luce coerente con
lo sfondo del volantino. Poi in PhotoCraft: `select.subject` (preciso su fondo uniforme) → `layer.layerMask.revealSelection`
→ `image.adjustments.hueSaturation` per gamma (blues/cyans/magentas o greens) per spostare il colore residuo sui
bordi verso i toni del soggetto. La selezione per gamma di colore (`select.colorRange`) lascia invece il soggetto
semitrasparente: non usarla per le persone.

```
Full-body studio photo of a fit young woman in a yoga tree pose, smiling, hands in prayer position, light green sports top and white leggings, long hair blowing in the wind, warm golden backlight as in morning sun, healthy glowing skin, whole body visible including bare feet, isolated on a solid flat pure blue background (#0000FF), no shadow on the background, no floor, sharp focus, ultra high definition, vertical 3:4
```

## Tecnica 2 — Composizione intera con il volantino come riferimento (la più efficace)

Quando il layout a livelli è pronto senza figure, esporta il PNG e fallo usare come immagine di riferimento
(image-to-image). Il modello aggiunge le figure fuse con luci e sfondi in modo più credibile di qualsiasi
montaggio. Poi scegli: (a) usare l'immagine generata così com'è, adattata al formato con abbondanza
(ridimensiona, estendi i bordi con `edit.contentAwareFill`, rifai il footer con i loghi veri sopra), oppure
(b) estrarre solo le figure (`image.crop` attorno alla figura → `select.subject` → cancella nella maschera con
`select.lasso` + `edit.fill black target=mask` i pezzi di volantino rimasti) e montarle sul file a livelli,
che mantiene scritte e loghi nitidi. L'utente ha preferito (a) per il fronte: è legittimo, purché loghi e testi
piccoli vengano rimessi veri.

```
Use the attached flyer as the exact reference: keep its layout, colors, gradients, white diagonal, logos and all lettering exactly as they are, do not redraw, move or alter any text or logo. Add two photorealistic characters in the empty areas only. In the upper green area, on the right side next to the slogan, <descrizione figura 1>, standing just above the white diagonal, with a soft blurred glow behind that melts into the flyer gradient. In the lower red area, on the left side next to the slogan, <descrizione figura 2>, legs disappearing behind the white footer, with a soft blurred dark glow behind that melts into the flyer gradient. Both characters sharp and in focus, lighting consistent with the backgrounds, no extra text, no watermarks, no new logos, no borders.
```

## Tecnica 3 — Scena vuota + prodotti veri

Per mostrare prodotti con etichette leggibili non farli disegnare: le scritte escono sbagliate. Fai generare la
scena vuota (bancone, scaffali sfocati, fasce libere per logo, testi e QR) e appoggia i PNG ufficiali dei
prodotti con `prodotti_su_piano()` in proporzione reale (chiedi le altezze in cm). Se una prima versione con i
prodotti disegnati piace come composizione, chiedi comunque la rigenerazione "solo bancone": cancellare i
prodotti generati lascia sempre tracce.

```
Photorealistic advertising scene inside a large modern supplement hangar. In the center, an empty brushed stainless steel table seen slightly from above, nothing on it, with soft realistic reflections on the steel. On the left and right, tall industrial shelves filled with supplement jars and boxes, extremely out of focus with very shallow depth of field, so they read only as soft colored shapes and bokeh, never legible. The top 20% of the frame is a clean, uniform, dark industrial wall with no objects, for a logo; the bottom 25% of the frame is a smooth uniform dark floor or table front in shadow with no objects, for text and a QR code. Cinematic industrial lighting, neutral cool tones with a warm golden accent light on the table, high contrast, ultra high definition, no people, no products on the table, no text, no watermarks, vertical 3:4.
```

## Sfondi sfocati da foto con soggetto

Se hai solo una foto con il soggetto e vuoi usarne lo sfondo: `select.object` o `select.subject` sul soggetto →
`select.modify.expand` 30 → `select.modify.feather` 40 → riempi con `paint.gradient` nei colori campionati
accanto (`colore_medio()`), oppure `edit.deleteAndFillSelection` quando lo sfondo è uniforme → `select.deselect`
→ `filter.blur.gaussianBlur` 30-60. Poi `foto_sfondo()` la estende sulla zona e la vela nei colori del marchio.

## Cosa dire all'utente di controllare

- Etichette e scritte: se compaiono, sono inventate; vanno coperte con i file veri.
- Mani, piedi, bilancieri: i punti dove i modelli sbagliano; rigenerare costa meno che ritoccare.
- Il soggetto deve stare nel lato previsto e lasciare libera la fascia del testo.
