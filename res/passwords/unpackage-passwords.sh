#!/usr/bin/env bash
echo '[*] Current directory contents'
ls -lah
cc=`wc -l passwords-hailmary.txt`
echo "[*] Current password count $cc"
echo '[*] Concatenating files'
cat passwords-hailmary-1.txt.zip passwords-hailmary-2.txt.zip passwords-hailmary-3.txt.zip passwords-hailmary-4.txt.zip passwords-hailmary-5.txt.zip > passwords-hailmary.txt.zip
echo '[*] Unzipping passwords-hailmary.txt'
unzip passwords-hailmary.txt.zip
echo '[*] Deleting temporary work files'
rm passwords-hailmary.txt.zip
cc=`wc -l passwords-hailmary.txt`
echo "[*] New password count $cc"
echo '[*] New directory contents'
ls -lah
