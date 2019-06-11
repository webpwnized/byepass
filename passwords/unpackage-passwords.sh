#!/usr/bin/env bash
cat passwords-hailmary-1.txt.zip passwords-hailmary-2.txt.zip passwords-hailmary-3.txt.zip > passwords-hailmary.txt.zip
unzip passwords-hailmary.txt.zip
rm passwords-hailmary.txt.zip
rm passwords-hailmary-1.txt.zip
rm passwords-hailmary-2.txt.zip
rm passwords-hailmary-3.txt.zip
ls -lah
