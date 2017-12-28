# Setup

**Step 1: Change into desired directory, clone the project and decompress passwords-hailmary.txt.zip.**

**Example:**

    git clone https://github.com/webpwnized/byepass.git
    cd bypass/passwords
    cat passwords-hailmary-1.txt.zip passwords-hailmary-2.txt.zip passwords-hailmary-3.txt.zip passwords-hailmary-4.txt.zip passwords-hailmary-5.txt.zip passwords-hailmary-6.txt.zip > passwords-hailmary.txt.zip
    unzip passwords-hailmary.txt.zip

**Step 2: Verify config.py is properly configured.** 

**JTR_FILE_PATH**: Install path for John the Ripper. This is
 system and situation dependent. On Kali Linux, the default 
 path is "/usr/share/john". When john is compiled natively,
 the path may be "/opt/john/run/" but the user who installed
 JTR could put it in others directories.

**JTR_EXECUTABLE_FILENAME**: Filename of the john executable. By default, this is 
"john" and should not need to be changed. On Windows it is john.exe by default.

**JTR_POT_FILENAME**: Filename of the john.pot file. By default, this is 
"john.pot" and should not need to be changed

If unsure of location of John the Ripper, try 

    locate john

**Example:**

if locate finds john installed in /opt/john/run/

    locate john
    /opt/john/run/

Then the config.py should contain the following

    JTR_FILE_PATH = "/opt/john/run/"
    JTR_EXECUTABLE_FILENAME = "john"
    JTR_POT_FILENAME = "john.pot"

# Usage

Usage for passtime and byepass

# PassTime

**Automate statistical analysis of passwords in support of password cracking tasks**

**Usage**: passtime.py [-h] [-v] [-l] [-p PERCENTILE] [-a] -i INPUT_FILE

**Optional arguments:**

      -h, --help            show this help message and exit
      -v, --verbose         Enable verbose output
      -l, --list-masks      List password masks for the passwords provided in the INPUT FILE
      -p PERCENTILE, --percentile PERCENTILE
                            Based on statistical analysis of the passwords provided, only list masks matching the given PERCENTILE percent of passwords. For example, if a value of 0.25 provided, only lists the relatively few masks needed to crack 25 percent of the passwords. Ideally, these would be the only masks needed to crack the same percentage of the remaining, uncracked passwords. However, the prediction is only as good as the sample passwords provided in the INPUT FILE. The more closely the provided passwords match the target passwords, the better the prediction.
      -a, --analyze-passwords
                            Perform analysis on the password provided in the INPUT FILE. A probability density function (PDF) will be displayed with the masks matching PERCENTILE percent of passwords. The marginal and cummulative percentages represented by each mask are provided with the number of passwords matched by the mask.
      -i INPUT_FILE, --input-file INPUT_FILE
                            Path to file containing passwords to analyze

**Examples**:

List masks representing 75 percent of the passwords in input file worst-10000-passwords.txt

    python3 passtime.py -l -p 0.75 -i worst-10000-passwords.txt


Generate probability density function (PDF), masks, marginal percentile (MP), cummulative percentile (CP) and count of passwords representing 75 percent of the passwords in input file worst-10000-passwords.txt

    python3 passtime.py -a -p 0.75 -i worst-10000-passwords.txt

# ByePass

**Automate the most common password cracking tasks**

**Usage**: byepass.py [-h] [-f HASH_FORMAT] [-s] [-p PERCENTILE] [-v] [-d] -i
                  INPUT_FILE

**Optional arguments:**

      -h, --help            show this help message and exit
      -f HASH_FORMAT, --hash-format HASH_FORMAT
                            The hash algorithm used to hash the password(s). This value must be one of the values supported by John the Ripper. To see formats supported by JTR, use command "john --list=formats". It is strongly recommended to provide an optimal value. If no value is provided, John the Ripper will guess.
      -s, --stat-crack      Enable statistical cracking. Byepass will run relatively fast cracking strategies in hopes of cracking enough passwords to induce a pattern and create "high probability" masks. Byepass will use the masks in an attempt to crack more passwords.
      -p PERCENTILE, --percentile PERCENTILE
                            Based on statistical analysis of the passwords cracked during initial phase, use only the masks statistically likely to be needed to crack at least the given percent of passwords. For example, if a value of 0.25 provided, only use the relatively few masks needed to crack 25 passwords of the passwords. Note that password cracking effort follows an exponential distribution, so cracking a few more passwords takes a lot more effort (relatively speaking). A good starting value if completely unsure is 25 percent (0.25).
      -v, --verbose         Enable verbose output such as current progress and duration
      -d, --debug           Enable debug mode

**Required arguments:**

      -i INPUT_FILE, --input-file INPUT_FILE
                            Path to file containing password hashes to attempt to crack

**Examples**:

Attempt to crack password hashes found in input file "password.hashes"

	python3 byepass.py -v --hash-format=descrypt --input-file=password.hashes

Attempt to crack password hashes found in input file "password.hashes", then run statistical analysis to determine masks needed to crack 50 percent of passwords, and try to crack again using the masks.

	python3 byepass.py --verbose --hash-format=descrypt --stat-crack --percentile=0.50 --input-file=password.hashes
                                         
# Hashes and Password Lists

These resources host hashes and the resulting passwords. These can be helpful for practice.

**Adeptus Mechanicus**: http://www.adeptus-mechanicus.com/codex/hashpass/hashpass.php

**Hashes.org**: https://hashes.org/leaks.php

**CrackStation's Password Cracking Dictionary**: https://crackstation.net/buy-crackstation-wordlist-password-cracking-dictionary.htm

# Educational Resources

**John the Ripper's cracking modes**: http://www.openwall.com/john/doc/MODES.shtml

**John the Ripper usage examples**: http://www.openwall.com/john/doc/EXAMPLES.shtml

**Luis Rocha's John the Ripper Cheat Sheet**: https://countuponsecurity.files.wordpress.com/2016/09/jtr-cheat-sheet.pdf