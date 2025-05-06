#!/usr/bin/env bash

# setup.sh - Unpack password list and unzip hash files after install
set -euo pipefail
IFS=$'\n\t'

log() { echo "[*] $1"; }
err() { echo "[!] $1" >&2; }

cd "$(dirname "$0")/.." || { err "Cannot find repo root"; exit 1; }

pw_dir="res/passwords"
hash_dir="data/hashes"

# --- HailMary password reconstruction ---
rebuild_hailmary() {
  local pw_file="$pw_dir/passwords-hailmary.txt"
  log "Checking for $pw_file"
  [[ -f "$pw_file" ]] && { log "$pw_file already exists — skipping reassembly"; return; }

  log "Reconstructing password file from zip parts"
  for i in {1..5}; do
    part="$pw_dir/passwords-hailmary-${i}.txt.zip"
    [[ -f "$part" ]] || { err "Missing part: $part"; return; }
  done

  cat "$pw_dir"/passwords-hailmary-{1..5}.txt.zip > "$pw_dir/passwords-hailmary.txt.zip"

  if unzip -q "$pw_dir/passwords-hailmary.txt.zip" -d "$pw_dir"; then
    rm "$pw_dir"/passwords-hailmary-{1..5}.txt.zip "$pw_dir/passwords-hailmary.txt.zip"
    [[ -f "$pw_file" ]] && count=$(wc -l < "$pw_file") && log "$(basename "$pw_file") contains $count lines"
  else
    err "Failed to unzip combined password archive"
  fi
}

# --- Worst passwords unpack ---
unpack_worst_passwords() {
  local worst_zip="$pw_dir/worst-50000-passwords.txt.zip"
  local worst_txt="${worst_zip%.zip}"

  if [[ -f "$worst_txt" ]]; then
    log "$worst_txt already exists — skipping"
    return
  elif [[ ! -f "$worst_zip" ]]; then
    log "$worst_zip not found — skipping"
    return
  fi

  log "Unzipping worst-50000-passwords.txt"
  contents=$(unzip -Z1 "$worst_zip" 2>/dev/null || true)
  if [[ "$contents" != "$(basename "$worst_txt")" ]]; then
    err "Unexpected contents in $(basename "$worst_zip"): $contents"
    return
  fi

  if unzip -q "$worst_zip" -d "$pw_dir"; then
    rm "$worst_zip" || err "Failed to delete $worst_zip after extraction"
    [[ -f "$worst_txt" ]] && count=$(wc -l < "$worst_txt") && log "$(basename "$worst_txt") contains $count lines"
  else
    err "Failed to unzip $worst_zip"
  fi
}

# --- Hash unzip ---
unpack_hashes() {
  if [[ ! -d "$hash_dir" ]]; then
    err "Hash directory not found: $hash_dir"
    return
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
      continue
    fi

    log "Unzipping $(basename "$zipf")"
    if unzip -q "$zipf" -d "$hash_dir"; then
      rm "$zipf" || err "Failed to delete $zipf after extraction"
      [[ -f "$txt" ]] && count=$(wc -l < "$txt") && log "$(basename "$txt") contains $count lines"
    else
      err "Failed to unzip $zipf"
    fi
  done
  shopt -u nullglob
}

# Run all unpack tasks
rebuild_hailmary || log "HailMary password list step failed"
unpack_worst_passwords || log "Worst passwords step failed"
unpack_hashes || log "Hash unzip step failed"

log "Setup complete."
