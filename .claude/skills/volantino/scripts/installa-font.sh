#!/usr/bin/env bash
# Installa per l'utente corrente i font della skill (assets/font/**/*.ttf) così PhotoCraft li vede in type.fonts.
# Linux: ~/.local/share/fonts + fc-cache.  macOS: ~/Library/Fonts.
set -euo pipefail
QUI="$(cd "$(dirname "$0")/.." && pwd)"
case "$(uname -s)" in
  Darwin) DEST="$HOME/Library/Fonts" ;;
  *)      DEST="$HOME/.local/share/fonts" ;;
esac
mkdir -p "$DEST"
cp -f "$QUI"/assets/font/*/*.ttf "$DEST"/
command -v fc-cache >/dev/null 2>&1 && fc-cache -f >/dev/null 2>&1 || true
echo "Font installati in $DEST: $(ls "$QUI"/assets/font/*/*.ttf | wc -l | tr -d ' ') file"
echo "Famiglie: Anton, Bebas Neue, Cinzel, Inter, Kaushan Script, Montserrat"
echo "Verifica: photocraft-cli run --new '{\"width\":10,\"height\":10}' --cmd type.fonts --params '{\"family\":\"Anton\"}'"
