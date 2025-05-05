#!/usr/bin/env bash

# setup.sh - Unpack password list and unzip hash files after install
set -euo pipefail
IFS=$'\n\t'

log() { echo "[*] $1"; }
err() { echo "[!] $1" >&2; }

cd "$(dirname "$0")/.." || { err "Cannot find repo root"; exit 1; }

# --- Reassemble and unzip password wordlist ---
pw_dir="res/passwords"
pw_file="$pw_dir/passwords-hailmary.txt"

if [[ ! -f "$pw_file" ]]; then
  log "Reconstructing password file from zip parts"

  # Validate parts exist
  for i in {1..5}; do
    part="$pw_dir/passwords-hailmary-${i}.txt.zip"
    [[ -f "$part" ]] || { err "Missing part: $part"; exit 1; }
  done

  log "Combining and unzipping..."
  cat "$pw_dir"/passwords-hailmary-{1..5}.txt.zip > "$pw_dir/passwords-hailmary.txt.zip"

  if unzip -q "$pw_dir/passwords-hailmary.txt.zip" -d "$pw_dir"; then
    rm "$pw_dir"/passwords-hailmary-{1..5}.txt.zip
    rm "$pw_dir/passwords-hailmary.txt.zip"
    if [[ -f "$pw_file" ]]; then
      count=$(wc -l < "$pw_file")
      log "$(basename "$pw_file") contains $count lines"
    else
      err "Expected file missing after unzip: $pw_file"
      exit 1
    fi
  else
    err "Failed to unzip combined password archive"
    exit 1
  fi
else
  log "$pw_file already exists — skipping reassembly"
fi

# --- Unzip hash files ---
hash_dir="data/hashes"
if [[ ! -d "$hash_dir" ]]; then
  err "Hash directory not found: $hash_dir"
  exit 1
fi

log "Unzipping hash files in $hash_dir"

shopt -s nullglob
for zipf in "$hash_dir"/*.txt.zip; do
  txt="${zipf%.zip}"

  if [[ -f "$txt" ]]; then
    log "$(basename "$txt") already exists — skipping"
    continue
  fi

  contents=$(unzip -Z1 "$zipf" 2>/dev/null || true)
  if [[ "$contents" != "$(basename "$txt")" ]]; then
    err "Unexpected contents in $(basename "$zipf"): $contents"
    exit 1
  fi

  log "Unzipping $(basename "$zipf")"
  if unzip -q "$zipf" -d "$hash_dir"; then
    rm "$zipf" || { err "Failed to delete $zipf after extraction"; exit 1; }
    if [[ -f "$txt" ]]; then
      count=$(wc -l < "$txt")
      log "$(basename "$txt") contains $count lines"
    else
      err "Expected file missing after unzip: $txt"
      exit 1
    fi
  else
    err "Failed to unzip $zipf"
    exit 1
  fi
done
shopt -u nullglob

log "Unzipped hash files:"
ls -lh "$hash_dir"/*.txt

log "Setup complete."
