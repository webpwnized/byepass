#!/usr/bin/env bash

# package-files-for-push.sh - Compress password list and practice hashes using ZIP
set -euo pipefail
IFS=$'\n\t'

log() { echo "[*] $1"; }
err() { echo "[!] $1" >&2; }

cd "$(dirname "$0")/.." || { err "Cannot find repo root"; exit 1; }

# --- Package password list ---
pw_dir="res/passwords"
john_pot="/opt/JohnTheRipper/run/john.pot"
pw_file="$pw_dir/passwords-hailmary.txt"

if [[ -f "$pw_file" ]]; then
  log "Processing $pw_file"

  if [[ -f "$john_pot" ]]; then
    log "Extracting cracked passwords from john.pot"
    cut -f2 -d: "$john_pot" > /tmp/john-pot.txt
    log "Merging with $pw_file"
    sort -u /tmp/john-pot.txt "$pw_file" > /tmp/merged.txt
    mv /tmp/merged.txt "$pw_file"
    rm /tmp/john-pot.txt
  else
    log "john.pot not found — skipping merge"
  fi

  log "Compressing password file"
  zip -q "$pw_dir/passwords-hailmary.txt.zip" "$pw_file"

  log "Splitting into 5 parts"
  split -n 5 "$pw_dir/passwords-hailmary.txt.zip" "$pw_dir/passwords-hailmary-"
  for i in {a..e}; do
    mv "$pw_dir/passwords-hailmary-a$i" "$pw_dir/passwords-hailmary-$(( $(printf '%d' "'$i") - 96 )).txt.zip"
  done

  log "Cleaning up intermediate zip"
  rm "$pw_dir/passwords-hailmary.txt.zip"

  count=$(wc -l < "$pw_file")
  log "$(basename "$pw_file") contains $count lines"

  log "Password packaging complete:"
  ls -lh "$pw_dir"/passwords-hailmary-*.txt.zip
else
  log "No password file found to package."
fi

# --- Zip hash files ---
hash_dir="data/hashes"
if [[ -d $hash_dir ]]; then
  log "Zipping hash files in $hash_dir"
  for f in "$hash_dir"/*.txt; do
    [[ -f "$f" ]] || continue
    zipf="${f}.zip"

    if [[ -f "$zipf" ]]; then
      log "$(basename "$zipf") already exists — skipping"
    else
      log "Zipping $(basename "$f")"
      zip -q "$zipf" "$f" || { err "Failed to zip $f"; exit 1; }
    fi

    count=$(wc -l < "$f")
    log "$(basename "$f") contains $count lines"
    rm "$f"
  done

  log "Zipped hash files:"
  ls -lh "$hash_dir"/*.txt.zip
else
  err "Hash directory not found"
fi

log "All packaging complete."
