#!/usr/bin/env bash

# package-files-for-push.sh - Prepare password list and hashes for GitHub
set -euo pipefail
IFS=$'\n\t'

log() { echo "[*] $1"; }
err() { echo "[!] $1" >&2; }

cd "$(dirname "$0")/.." || { err "Cannot find repo root"; exit 1; }

pw_dir="res/passwords"
hash_dir="data/hashes"
john_pot="/opt/JohnTheRipper/run/john.pot"
pw_file="$pw_dir/passwords-hailmary.txt"

# --- Package HailMary password list ---
if [[ -f "$pw_file" ]]; then
  log "Preparing password file: $(basename "$pw_file")"
  if [[ -f "$john_pot" ]]; then
    log "Merging cracked passwords from $john_pot"
    cut -f2 -d: "$john_pot" > /tmp/byepass-john-pot.txt
    sort -u /tmp/byepass-john-pot.txt "$pw_file" > /tmp/byepass-merged.txt
    mv /tmp/byepass-merged.txt "$pw_file"
    rm /tmp/byepass-john-pot.txt
  elif
    log "$john_pot was not found. Cracked passwords will not be added to $pw_file."
  fi

  zip_path="$pw_dir/passwords-hailmary.txt.zip"
  log "Compressing password list"
  if zip -j -q "$zip_path" "$pw_file"; then
    rm "$pw_file"
    split -n 5 "$zip_path" "$pw_dir/passwords-hailmary-"
    for i in {a..e}; do
      part="$pw_dir/passwords-hailmary-a$i"
      target="$pw_dir/passwords-hailmary-$(( $(printf '%d' "'$i") - 96 )).txt.zip"
      [[ -f "$part" ]] && mv "$part" "$target" || { err "Missing split part $part"; break; }
    done
    rm "$zip_path"
    log "Password packaging complete"
    ls -lh "$pw_dir"/passwords-hailmary-*.txt.zip
  else
    err "Failed to zip $pw_file"
  fi
else
  log "$pw_file not found — skipping HailMary packaging"
fi

# --- Package worst-50000-passwords.txt ---
worst_pw_file="$pw_dir/worst-50000-passwords.txt"
worst_zip="$worst_pw_file.zip"
if [[ -f "$worst_pw_file" ]]; then
  log "Compressing worst password file"
  if zip -j -q "$worst_zip" "$worst_pw_file"; then
    rm "$worst_pw_file"
  else
    err "Failed to zip $worst_pw_file"
  fi
else
  log "$worst_pw_file not found — skipping"
fi

# --- Zip hash files ---
if [[ -d "$hash_dir" ]]; then
  log "Zipping hash files in $hash_dir"
  shopt -s nullglob
  for f in "$hash_dir"/*.txt; do
    zipf="$f.zip"
    [[ -f "$zipf" ]] && { log "$(basename "$zipf") already exists — skipping"; continue; }
    log "Zipping $(basename "$f")"
    if zip -j -q "$zipf" "$f"; then
      rm "$f"
    else
      err "Failed to zip $f"
    fi
  done
  shopt -u nullglob
else
  err "Hash directory not found: $hash_dir"
fi

log "Packaging complete."
