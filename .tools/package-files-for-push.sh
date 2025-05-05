#!/usr/bin/env bash

# package-files-for-push.sh - Prepare password list and hashes for GitHub
set -euo pipefail
IFS=$'\n\t'

log() { echo "[*] $1"; }
err() { echo "[!] $1" >&2; }

cd "$(dirname "$0")/.." || { err "Cannot find repo root"; exit 1; }

# --- Prepare password wordlist ---
pw_dir="res/passwords"
pw_file="$pw_dir/passwords-hailmary.txt"
john_pot="/opt/JohnTheRipper/run/john.pot"

if [[ ! -f "$pw_file" ]]; then
  err "Password list not found: $pw_file"
  exit 1
fi

log "Preparing password file: $(basename "$pw_file")"

# Merge john.pot if available
if [[ -f "$john_pot" ]]; then
  log "Merging cracked passwords from $john_pot"
  cut -f2 -d: "$john_pot" > /tmp/byepass-john-pot.txt
  sort -u /tmp/byepass-john-pot.txt "$pw_file" > /tmp/byepass-merged.txt
  mv /tmp/byepass-merged.txt "$pw_file"
  rm /tmp/byepass-john-pot.txt
else
  log "john.pot not found — skipping merge"
fi

# Zip the password list (in place)
zip_path="$pw_dir/passwords-hailmary.txt.zip"
log "Compressing password list to: $(basename "$zip_path")"
zip -j -q "$zip_path" "$pw_file" || { err "Failed to zip $pw_file"; exit 1; }
rm "$pw_file" || { err "Failed to delete $pw_file after zipping"; exit 1; }

# Split into 5 parts
log "Splitting zip into 5 parts"
split -n 5 "$zip_path" "$pw_dir/passwords-hailmary-"

# Rename parts to numbered suffix
for i in {a..e}; do
  part="$pw_dir/passwords-hailmary-a$i"
  target="$pw_dir/passwords-hailmary-$(( $(printf '%d' "'$i") - 96 )).txt.zip"
  if [[ -f "$part" ]]; then
    mv "$part" "$target"
  else
    err "Expected split part missing: $part"
    exit 1
  fi
done

rm "$zip_path"

log "Password packaging complete:"
ls -lh "$pw_dir"/passwords-hailmary-*.txt.zip

# --- Zip hash files individually ---
hash_dir="data/hashes"
if [[ ! -d "$hash_dir" ]]; then
  err "Hash directory not found: $hash_dir"
  exit 1
fi

log "Zipping hash files in $hash_dir"

shopt -s nullglob
for f in "$hash_dir"/*.txt; do
  zipf="$f.zip"
  if [[ -f "$zipf" ]]; then
    log "$(basename "$zipf") already exists — skipping"
    continue
  fi

  log "Zipping $(basename "$f")"
  zip -j -q "$zipf" "$f" || { err "Failed to zip $f"; exit 1; }
  rm "$f" || { err "Failed to delete $f after zipping"; exit 1; }

  log "Zipped $(basename "$zipf")"
done
shopt -u nullglob

log "Packaging complete."
