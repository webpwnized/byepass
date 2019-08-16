#!/usr/bin/env bash

echo '[*] Counting current password list'
cc=`wc -l passwords-hailmary.txt`
echo "[*] Current password count $cc"
echo '[*] Parsing /opt/JohnTheRipper/run/john.pot'
cut -f2 -d\: /opt/JohnTheRipper/run/john.pot > /tmp/j
echo '[*] Merging /opt/JohnTheRipper/run/john.pot with passwords-hailmary.txt'
sort -u /tmp/j ./passwords-hailmary.txt > /tmp/p
rm /tmp/j
mv /tmp/p passwords-hailmary.txt
echo '[*] Compressing passwords-hailmary.txt'
zip passwords-hailmary.txt.zip passwords-hailmary.txt
echo '[*] Splitting passwords-hailmary.txt.zip'
split -n 5 passwords-hailmary.txt.zip passwords-hailmary-
mv passwords-hailmary-aa passwords-hailmary-1.txt.zip
mv passwords-hailmary-ab passwords-hailmary-2.txt.zip
mv passwords-hailmary-ac passwords-hailmary-3.txt.zip
mv passwords-hailmary-ad passwords-hailmary-4.txt.zip
mv passwords-hailmary-ae passwords-hailmary-5.txt.zip
echo '[*] Deleting temporary working files'
rm passwords-hailmary.txt.zip
echo '[*] Passwords have been packaged for GitHub'
echo '[*] Counting new password list'
cc=`wc -l passwords-hailmary.txt`
echo "[*] New password count $cc"
ls -lah
