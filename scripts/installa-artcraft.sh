#!/usr/bin/env bash
# Installa le CLI delle app ArtCraft (con il loro server MCP) compilandole dal sorgente.
# Serve nelle sessioni cloud, dove i download diretti delle release GitHub sono bloccati
# ma git clone dei repo pubblici e crates.io funzionano.
#
# Uso:  scripts/installa-artcraft.sh               -> installa photocraft
#       APPS="photocraft gridcraft" scripts/installa-artcraft.sh
#
# Ogni app sta in github.com/storytold/<app> e produce il binario <app>-cli.
# Testato solo con photocraft (v0.11.1, ~7 minuti su 4 core).
set -euo pipefail

APPS="${APPS:-photocraft}"
SRC_DIR="${ARTCRAFT_SRC:-/opt/artcraft}"
BIN_DIR="${ARTCRAFT_BIN:-/usr/local/bin}"

export PATH="$HOME/.cargo/bin:$PATH"
command -v cargo >/dev/null || { echo "cargo non trovato: serve Rust" >&2; exit 1; }

mkdir -p "$SRC_DIR"
for app in $APPS; do
  if command -v "$app-cli" >/dev/null; then
    echo "$app-cli già installato: $("$app-cli" --version)"
    continue
  fi
  echo "==> $app: clone"
  if [ ! -d "$SRC_DIR/$app/.git" ]; then
    GIT_LFS_SKIP_SMUDGE=1 git clone --depth 1 "https://github.com/storytold/$app" "$SRC_DIR/$app"
  fi
  echo "==> $app: compilazione (alcuni minuti)"
  cargo build --release --locked --manifest-path "$SRC_DIR/$app/Cargo.toml" -p "$app-cli"
  install -m 755 "$SRC_DIR/$app/target/release/$app-cli" "$BIN_DIR/$app-cli"
  echo "==> $app: installato $("$BIN_DIR/$app-cli" --version)"
done
