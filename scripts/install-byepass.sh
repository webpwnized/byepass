#!/bin/bash

# We assume we are in the directory in which byepass resides
echo "[*] Backing up current installation"
mv byepass byepass.bak
echo "[*] Unzipping byepass to current directory"
unzip byepass-master.zip
mv byepass-master byepass
echo "[*] Setting up password lists"
cd byepass/passwords
./unpackage-passwords.sh
