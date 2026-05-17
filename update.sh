#!/bin/bash
set -e
cd "$(dirname "$0")" || exit 1
echo "Menunggu aplikasi ditutup untuk memulai pembaruan..."
sleep 2

BASE_DIR="$(pwd)"
ZIP_URL="https://github.com/tiomultazem/kipapp-helper-v3/archive/refs/heads/main.zip"
WORK_DIR="$(mktemp -d)"
ZIP_PATH="$WORK_DIR/update.zip"
EXTRACT_DIR="$WORK_DIR/extract"

cleanup() {
  rm -rf "$WORK_DIR"
}
trap cleanup EXIT

mkdir -p "$EXTRACT_DIR"

echo "Download update..."
if command -v curl >/dev/null 2>&1; then
  curl -L "$ZIP_URL" -o "$ZIP_PATH"
else
  wget -O "$ZIP_PATH" "$ZIP_URL"
fi

echo "Unzip update..."
unzip -q "$ZIP_PATH" -d "$EXTRACT_DIR"

SRC_DIR="$(find "$EXTRACT_DIR" -mindepth 1 -maxdepth 1 -type d | head -n 1)"
if [ ! -f "$SRC_DIR/main.py" ]; then
  echo "ZIP update tidak valid."
  exit 1
fi

echo "Replace file aplikasi..."
if command -v rsync >/dev/null 2>&1; then
  rsync -a --delete "$SRC_DIR"/ "$BASE_DIR"/
else
  find "$BASE_DIR" -mindepth 1 -maxdepth 1 -exec rm -rf {} +
  cp -a "$SRC_DIR"/. "$BASE_DIR"/
fi

echo "Menjalankan ulang aplikasi..."
cd "$BASE_DIR"
python3 main.py &
