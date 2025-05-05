#!/usr/bin/env bash

# setup.sh - Unpack password list and unzip hash files after install
set -euo pipefail
IFS=$'\n\t'

log() { echo "[*] $1"; }
err() { echo "[!] $1" >&2; }

cd "$(dirname "$0")/.." || { err "Cannot find repo root"; exit 1; }

# --- Reassemble and unzip password file ---
pw_dir="res/passwords"
pw_file="$pw_dir/passwords-hailmary.txt"

if [[ ! -f "$pw_file" ]]; then
  log "Reconstructing password file from zip parts"

  for i in {1..5}; do
    part="$pw_dir/passwords-hailmary-${i}.txt.zip"
    [[ -f "$part" ]] || { err "Missing part: $part"; exit 1; }
  done

  cat "$pw_dir"/passwords-hailmary-{1..5}.txt.zip > "$pw_dir/passwords-hailmary.txt.zip"
  unzip -q "$pw_dir/passwords-hailmary.txt.zip" -d "$pw_dir"
  rm "$pw_dir/passwords-hailmary.txt.zip"

  count=$(wc -l < "$pw_file")
  log "$(basename "$pw_file") contains $count lines"
else
  log "$pw_file already exists — skipping reassembly"
fi

# --- Unzip hash files ---
hash_dir="data/hashes"
if [[ -d $hash_dir ]]; then
  log "Unzipping hash files in $hash_dir"
  for zipf in "$hash_dir"/*.txt.zip; do
    txt="${zipf%.zip}"
    if [[ -f "$txt" ]]; then
      log "$(basename "$txt") already exists — skipping"
    else
      unzip -q "$zipf" -d "$hash_dir" || { err "Failed to unzip $zipf"; exit 1; }
    fi

    count=$(wc -l < "$txt")
    log "$(basename "$txt") contains $count lines"
  done

  log "Unzipped hash files:"
  ls -lh "$hash_dir"/*.txt
else
  err "Hash directory not found"
fi

log "Setup complete."
