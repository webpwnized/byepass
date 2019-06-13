#!/usr/bin/env bash
echo '[*] Concatenating files'
cat passwords-hailmary-1.txt.zip passwords-hailmary-2.txt.zip passwords-hailmary-3.txt.zip passwords-hailmary-4.txt.zip > passwords-hailmary.txt.zip
echo '[*] Unzipping passwords-hailmary.txt'
unzip passwords-hailmary.txt.zip
echo '[*] Deleting temporary work files'
rm passwords-hailmary.txt.zip
ls -lah
