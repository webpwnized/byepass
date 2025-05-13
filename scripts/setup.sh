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
  local final_file="$pw_dir/passwords-hailmary.txt"
  log "Extracting and reassembling HailMary password file"

  > "$final_file"  # Clear target file

  for i in $(seq -w 1 20); do
    zipf="$pw_dir/passwords-hailmary-${i}.txt.zip"
    txtf="$pw_dir/passwords-hailmary-${i}.txt"

    if [[ ! -f "$txtf" ]]; then
      if [[ -f "$zipf" ]]; then
        log "Unzipping $(basename "$zipf")"
        unzip -q "$zipf" -d "$pw_dir" && rm "$zipf" || { err "Failed to unzip $zipf"; return 1; }
      else
        err "Missing archive: $(basename "$zipf")"
        return 1
      fi
    else
      log "$txtf already exists — skipping unzip"
    fi

    [[ -f "$txtf" ]] || { err "Expected $txtf not found"; return 1; }

    cat "$txtf" >> "$final_file"
  done

  if [[ -f "$final_file" ]]; then
    lines=$(wc -l < "$final_file")
    log "Reassembled $(basename "$final_file") with $lines lines"
  else
    err "Final password file was not created"
    return 1
  fi

  log "Cleaning up split parts"
  rm -f "$pw_dir"/passwords-hailmary-*.txt
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

  log "Unzipping $(basename "$worst_zip")"
  contents=$(unzip -Z1 "$worst_zip" 2>/dev/null || true)
  if [[ "$contents" != "$(basename "$worst_txt")" ]]; then
    err "Unexpected contents in $(basename "$worst_zip"): $contents"
    return
  fi

  if unzip -q "$worst_zip" -d "$pw_dir"; then
    rm "$worst_zip"
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
      rm "$zipf"
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
