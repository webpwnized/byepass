# Byepass Test Cases

This document lists valid Byepass test cases with corrected paths and standardized options. Each command uses 4 CPU cores and fully qualified input paths.

---

## Default Mode

```bash
python3 /opt/byepass/src/byepass.py -f Raw-MD5 -j="--fork=4" -v -i /opt/byepass/data/hashes/byepass_md5_hashes.txt
```

---

## Prayer Mode Technique 4

```bash
python3 /opt/byepass/src/byepass.py -f Raw-MD5 -j="--fork=4" -t 4 -v -i /opt/byepass/data/hashes/byepass_md5_hashes.txt
```

---

## Prayer Mode Technique 1 (SHA1)

```bash
python3 /opt/byepass/src/byepass.py -f Raw-SHA1 -j="--fork=4" -t 1 -v -i /opt/byepass/data/hashes/byepass_md5_hashes.txt
```

---

## Wordlist Mode

```bash
python3 /opt/byepass/src/byepass.py -f Raw-MD5 -j="--fork=4" -w eharmony -v -i /opt/byepass/data/hashes/byepass_md5_hashes.txt
```

---

## Stat Crack Mode

```bash
python3 /opt/byepass/src/byepass.py -f Raw-MD5 -j="--fork=4" -s -p 0.5 -v -i /opt/byepass/data/hashes/byepass_md5_hashes.txt
```

---

## JTR Single Crack Mode

```bash
python3 /opt/byepass/src/byepass.py -f Raw-MD5 -j="--fork=4" -u -v -i /opt/byepass/data/hashes/byepass_md5_hashes.txt
```

---

## Brute Force Mode

```bash
python3 /opt/byepass/src/byepass.py -f Raw-MD5 -j="--fork=4" -b 8,8 -v -i /opt/byepass/data/hashes/byepass_md5_hashes.txt
```

---

## Recycle Mode

```bash
python3 /opt/byepass/src/byepass.py -f Raw-MD5 -j="--fork=4" -r -v -i /opt/byepass/data/hashes/byepass_md5_hashes.txt
```

---

## Prince Mode

```bash
python3 /opt/byepass/src/byepass.py -f Raw-MD5 -j="--fork=4" -c -v -i /opt/byepass/data/hashes/byepass_md5_hashes.txt
```

---

## Multimode

```bash
python3 /opt/byepass/src/byepass.py -f Raw-MD5 -j="--fork=4" -t 1,2,3,4,5,6,7,8,9,10,11,12,13,14 -s -p 0.9 -u -c -r -v -i /opt/byepass/data/hashes/byepass_md5_hashes.txt
```

---

## All Shortcut

```bash
python3 /opt/byepass/src/byepass.py -f Raw-MD5 -j="--fork=4" -a -v -i /opt/byepass/data/hashes/byepass_md5_hashes.txt
```

---

## Pathwell Mode

```bash
python3 /opt/byepass/src/byepass.py -f Raw-MD5 -j="--fork=4" -l 1,5 -v -i /opt/byepass/data/hashes/byepass_md5_hashes.txt
```

---

## Hailmary Mode

```bash
python3 /opt/byepass/src/byepass.py -f Raw-MD5 -j="--fork=4" -m -v -i /opt/byepass/data/hashes/byepass_md5_hashes.txt
```
