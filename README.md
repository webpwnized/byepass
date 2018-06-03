# Important

You should use ByePass with the latest build of John the Ripper. You may use ByePass with the
default version of JTR, but many formats and rules will not work. The default version of JTR
does not include these features. This video tutorial explains how to installl John the Ripper.

### How to install John the Ripper on Kali Linux Rolling

A video tutorial is available on the webpwnized YouTube channel at the following link.

[How to Install John the Ripper (YouTube)](https://www.youtube.com/watch?v=7R10QN_uCh0)

# Setup - Video Tutorials

Video tutorials are available at the following links. They explain how to install John the Ripper 
and ByePass respectively. For written instructions, refer to the next section

[How to Install John the Ripper (YouTube)](https://www.youtube.com/watch?v=7R10QN_uCh0)

[How to Install ByePass Automated Password Auditor](https://www.youtube.com/watch?v=aQwoJh6cyH8)

# Setup - Written Instructions

#### Step 1: Install John the Ripper

A video tutorial is available on the webpwnized YouTube channel at the following link.

[How to Install John the Ripper (YouTube)](https://www.youtube.com/watch?v=7R10QN_uCh0)

#### Step 2: Change into desired directory, clone the project and decompress passwords-hailmary.txt.zip

**Example:**

    cd /opt
    git clone https://github.com/webpwnized/byepass.git
    cd bypass/passwords
    cat passwords-hailmary-1.txt.zip passwords-hailmary-2.txt.zip passwords-hailmary-3.txt.zip > passwords-hailmary.txt.zip
    unzip passwords-hailmary.txt.zip
    cd ..

#### Step 3: Verify config.py is properly configured 

##### NOTE: Read and understand the important note above labeled "Important"

Assuming John the Ripper is installed in the /opt directory, the values should be the following:

    JTR_EXECUTABLE_FILE_PATH = "/opt/JohnTheRipper/run/john"
    JTR_POT_FILE_PATH = "/opt/JohnTheRipper/run/john.pot"

**JTR_EXECUTABLE_FILE_PATH**: Filepath to the john executable. If john is
 compiled natively, this path is usually <install directory>/JohnTheRipper/run/john.

**JTR_POT_FILE_PATH**: Filepath of the john.pot file. If john is
 compiled natively, this path is usually <install directory>/JohnTheRipper/run/john.

If unsure of location of the John the Ripper executable and pot file, try 

    which john
    locate john.pot

**Example:**

if locate finds john installed in the following

    which john
    /opt/JohnTheRipper/run/john

    locate john.pot
    /opt/JohnTheRipper/run/john.pot

Then the config.py should contain the following

    JTR_EXECUTABLE_FILE_PATH = "/opt/JohnTheRipper/run/john"
    JTR_POT_FILE_PATH = "/opt/JohnTheRipper/run/john.pot"

#### Step 4: Tell john the location of byepass's word mangling rules 

The rule are located in <byepass directory>/rules/byepass.conf. To
tell john the location, add the following line to john.conf.

    .include "<location of bypass>/byepass/rules/byepass.conf"
    .include "<location of bypass>/byepass/rules/OneRuleToRuleThemAll.rule"
    .include "<location of bypass>/byepass/rules/Best126.rule"

where "location of bypass" is the location that byepass is installed.
For example, if byepass is installed in /opt, add the following line
into john.conf

    .include "/opt/byepass/rules/byepass.conf"
    .include "/opt/byepass/rules/OneRuleToRuleThemAll.rule"
    .include "/opt/byepass/rules/Best126.rule"

**Tips**: 
* To find a good location in john.conf to place the line, search
for ".include" and place the new include line near other include lines.
* The gedit
editor is easy to use.

# Usage

Usage for passtime and byepass

## PassTime

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

## Examples:

### Listing Masks

List masks representing 75 percent of the passwords in input file passwords.txt

    python3 passtime.py -l -p 0.75 -i passwords.txt

### Analyzing Passwords

Generate probability density function (PDF), masks, marginal percentile (MP), cummulative percentile (CP) and count of passwords representing 75 percent of the passwords in input file passwords.txt

    python3 passtime.py -a -p 0.75 -i passwords.txt

### Creating format suitable for import into spreadsheet

Output the number of passwords represented by each mask sorted by count descending. The first row labels the mask. The second row contains the raw counts per mask. The third row contains the cumulative counts per mask. Values are comma-separated.

    python3 passtime.py -v -d -i passwords.txt

These same values can be output to a file with the addition of the -o/--output-file argument

    python3 passtime.py -v -d -i passwords.txt -o raw-data.csv

## ByePass

**Automate the most common password cracking tasks**

**Usage**: byepass.py [-h] [-f HASH_FORMAT] [-s] [-b BASE_WORDS] [-p PERCENTILE]
                  [-v] [-d] -i INPUT_FILE

**Optional arguments:**

      -h, --help            show this help message and exit
      -f HASH_FORMAT, --hash-format HASH_FORMAT
                            The hash algorithm used to hash the password(s). This value must be one of the values supported by John the Ripper. To see formats supported by JTR, use command "john --list=formats". It is strongly recommended to provide an optimal value. If no value is provided, John the Ripper will guess.
                            
      -b BASEWORDS, --basewords BASEWORDS
                            Supply a comma-separated list of lowercase, unmangled base words thought to be good candidates. For example, if Wiley Coyote is cracking hashes from Acme Inc., Wiley might provide the word "acme". Be careful how many words are supplied as Byepass will apply many mangling rules. Up to several dozen should run reasonably fast.
                            
      -t TECHNIQUES, --techniques TECHNIQUES
                            Comma-separated list of integers between 0-4 that determines what password cracking techniques are attempted. Default is level 1. Example of running levels 1 and 2 --techniques=1,2
                            
                            0: Skip prayer mode entirely
                            1: Quickly try most likely techniques
                            2: Best dictionaries. All rules
                            3: Time is an illusion. Big dictionaries. Best Rules.
                            4: Go freaking nuts. Big dictionaries. All Rules.
                            
      -s, --stat-crack      Enable statistical cracking. Byepass will run relatively fast cracking strategies in hopes of cracking enough passwords to induce a pattern and create "high probability" masks. Byepass will use the masks in an attempt to crack more passwords.
                            
      -p PERCENTILE, --percentile PERCENTILE
                            Based on statistical analysis of the passwords cracked during initial phase, use only the masks statistically likely to be needed to crack at least the given percent of passwords. For example, if a value of 0.25 provided, only use the relatively few masks needed to crack 25 passwords of the passwords. Note that password cracking effort follows an exponential distribution, so cracking a few more passwords takes a lot more effort (relatively speaking). A good starting value if completely unsure is 25 percent (0.25).
                            
      -j PASS_THROUGH, --pass-through PASS_THROUGH
                            Pass-through the raw parameter to John the Ripper. Example: --pass-through="--fork=2"
                            
      -v, --verbose         Enable verbose output such as current progress and duration
      -d, --debug           Enable debug mode

**Required arguments:**

      -i INPUT_FILE, --input-file INPUT_FILE
                            Path to file containing password hashes to attempt to crack

## Examples:

### Using Base Words Mode

Attempt to crack linked-in hashes using base words linkedin and linked

	python3 byepass.py --verbose --hash-format=Raw-SHA1 --base-words=linkedin,linked --input-file=linkedin-1.hashes

	python3 byepass.py -v -f Raw-SHA1 -b linkedin,linked -i linkedin-1.hashes

### Using Prayer Mode

Attempt to crack password hashes found in input file "password.hashes" using default technique level 1

	python3 byepass.py --verbose --hash-format=descrypt --input-file=password.hashes

	python3 byepass.py -v -f descrypt -i password.hashes

Be more aggressive by using techniques level 2 in attempt to crack password hashes found in input file "password.hashes"

	python3 byepass.py --verbose --techniques=2 --hash-format=descrypt --input-file=password.hashes

	python3 byepass.py -v -a 2 -f descrypt -i password.hashes

Be even more aggressive by using techniques level 3 in attempt to crack password hashes found in input file "password.hashes"

	python3 byepass.py --verbose --techniques=3 --hash-format=descrypt --input-file=password.hashes

	python3 byepass.py -v -a 3 -f descrypt -i password.hashes

Maximum effort by using techniques level 4 in attempt to crack password hashes found in input file "password.hashes"

	python3 byepass.py --verbose --techniques=4 --hash-format=descrypt --input-file=password.hashes

	python3 byepass.py -v -a 4 -f descrypt -i password.hashes

Go bonkers and try all techniques. Start with technique level 1 and proceed to level 4 in attempt to crack password hashes found in input file "password.hashes"

	python3 byepass.py --verbose --techniques=1,2,3,4 --hash-format=descrypt --input-file=password.hashes

	python3 byepass.py -v -a 1,2,3,4 -f descrypt -i password.hashes

Only try first two techniques. Start with technique level 1 and proceed to level 2 in attempt to crack password hashes found in input file "password.hashes"

	python3 byepass.py --verbose --techniques=1,2 --hash-format=descrypt --input-file=password.hashes

	python3 byepass.py -v -a 1,2 -f descrypt -i password.hashes

### Using Statistical Analysis Mode

Attempt to crack password hashes found in input file "password.hashes", then run statistical analysis to determine masks needed to crack 50 percent of passwords, and try to crack again using the masks.

	python3 byepass.py --verbose --hash-format=descrypt --stat-crack --percentile=0.50 --input-file=password.hashes

	python3 byepass.py -v -f descrypt -s -p 0.50 -i password.hashes

"Real life" example attempting to crack 25 percent of the linked-in hash set

	python3 byepass.py --verbose --hash-format=Raw-SHA1 --stat-crack --percentile=0.25 --input-file=linkedin.hashes

	python3 byepass.py -v -f Raw-SHA1 -s -f 0.25 -i linkedin.hashes

Do not run prayer mode. Only run statistical analysis to determine masks needed to crack 50 percent of passwords, and try to crack using the masks.

	python3 byepass.py -v --techniques=0 --hash-format=descrypt --stat-crack --percentile=0.50 --input-file=password.hashes

	python3 byepass.py -v -a 0 -f descrypt -s -p 0.50 -i password.hashes

### Passing a switch to John the Ripper

Use pass-through to pass fork command to JTR

	python3 byepass.py --verbose --pass-through="--fork=4" --hash-format=descrypt --input-file=password.hashes

	python3 byepass.py -v -j="--fork=4" -f descrypt -i password.hashes

# Hashes and Password Lists

These resources host hashes and the resulting passwords. These can be helpful for practice.

**Adeptus Mechanicus**: http://www.adeptus-mechanicus.com/codex/hashpass/hashpass.php

**Hashes.org**: https://hashes.org/leaks.php

**CrackStation's Password Cracking Dictionary**: https://crackstation.net/buy-crackstation-wordlist-password-cracking-dictionary.htm

**Daniel Miessler's SecLists/Passwords**: https://github.com/danielmiessler/SecLists/tree/master/Passwords

**Lists of Words**: http://scrapmaker.com/home

# Educational Resources

**John the Ripper's cracking modes**: http://www.openwall.com/john/doc/MODES.shtml

**John the Ripper usage examples**: http://www.openwall.com/john/doc/EXAMPLES.shtml

**Luis Rocha's John the Ripper Cheat Sheet**: https://countuponsecurity.files.wordpress.com/2016/09/jtr-cheat-sheet.pdf

**Martin Bos's Thoughts**: https://www.trustedsec.com/2016/06/introduction-gpu-password-cracking-owning-linkedin-password-dump/

**One Rule to Rule them All**: https://github.com/NotSoSecure/password_cracking_rules