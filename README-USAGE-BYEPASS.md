# Usage

Video tutorials that explain how to use ByePass are 
available at the following links. For written instructions, refer to the next section.

* [Using ByePass: Basic Usage](https://www.youtube.com/watch?v=cFQjbpQUtJU)
* [Using ByePass: Using Fork for Faster Cracking](https://www.youtube.com/watch?v=xNSbFu7hLDc)
* [Using ByePass: More Aggressive Techniques](https://www.youtube.com/watch?v=WlxQ11uYH-U)
* [Using ByePass: Base Words Technique](https://www.youtube.com/watch?v=5vlW5_iiOPE)
* [Using ByePass: Statistical Cracking Technique](https://www.youtube.com/watch?v=7McTDayHJs4)
* [Using ByePass: Brute-Force Technique](https://www.youtube.com/watch?v=U6LDeFZhIu0)

If you would like more help, please see the video 
tutorials in the following playlist

* [Complete Guide to ByePass](https://www.youtube.com/playlist?list=PLZOToVAK85Mqfcbufx1_lQHZ4pltV8nAm)

## Using ByePass

**Automate the most common password cracking tasks**

**Usage**: byepass.py [-h] [-f HASH_FORMAT] [-w BASEWORDS] [-b BRUTE_FORCE]
                  [-t TECHNIQUES] [-s] [-p PERCENTILE] [-j PASS_THROUGH] [-v]
                  [-d] (-e | -i INPUT_FILE)

**Optional arguments:**

      -h, --help            show this help message and exit
      -f HASH_FORMAT, --hash-format HASH_FORMAT
                            The hash algorithm used to hash the password(s). This value must be one of the values supported by John the Ripper. To see formats supported by JTR, use command "john --list=formats". It is strongly recommended to provide an optimal value. If no value is provided, John the Ripper will guess.
                            
      -w BASEWORDS, --basewords BASEWORDS
                            Supply a comma-separated list of lowercase, unmangled base words thought to be good candidates. For example, if Wiley Coyote is cracking hashes from Acme Inc., Wiley might provide the word "acme". Be careful how many words are supplied as Byepass will apply many mangling rules. Up to several should run reasonably fast.
                            
      -b BRUTE_FORCE, --brute-force BRUTE_FORCE
                            Bruce force common patterns with at least MIN characters up to MAX characters. Provide minimum and maxiumum number of characters as comma-separated, positive integers (i.e. 4,6 means 4 characters to 6 characters).
                            
      -t TECHNIQUES, --techniques TECHNIQUES
                            Comma-separated list of integers between 0-13 that determines what password cracking techniques are attempted. Default is level 1. Example of running levels 1 and 2 --techniques=1,2
                            
                            0: Skip prayer mode entirely
                            1: Small Dictionaries. Small Rulesets
                            2: Medium Dictionaries. Small Rulesets
                            3: Small Dictionaries. Medium Rulesets
                            4: Medium Dictionaries. Medium Rulesets
                            5: Large Password List. Custom Ruleset
                            6: Medium-Large Dictionaries. Small Rulesets
                            7: Small Dictionaries. Large Rulesets
                            8: Medium Dictionaries. Large Rulesets
                            9: Medium-Large Dictionaries. Medium Rulesets
                            10: Large Dictionaries. Small Rulesets
                            11: Medium-Large Dictionaries. Large Rulesets
                            12: Large Dictionaries. Medium Rulesets
                            13: Large Dictionaries. Large Rulesets
                            
      -s, --stat-crack      Enable statistical cracking. Byepass will run relatively fast cracking strategies in hopes of cracking enough passwords to induce a pattern and create "high probability" masks. Byepass will use the masks in an attempt to crack more passwords.
                            
      -p PERCENTILE, --percentile PERCENTILE
                            Based on statistical analysis of the passwords cracked during initial phase, use only the masks statistically likely to be needed to crack at least the given percent of passwords. For example, if a value of 0.25 provided, only use the relatively few masks needed to crack 25 passwords of the passwords. Note that password cracking effort follows an exponential distribution, so cracking a few more passwords takes a lot more effort (relatively speaking). A good starting value if completely unsure is 25 percent (0.25).
                            
      -j PASS_THROUGH, --pass-through PASS_THROUGH
                            Pass-through the raw parameter to John the Ripper. Example: --pass-through="--fork=2"
                            
      -v, --verbose         Enable verbose output such as current progress and duration
      -d, --debug           Enable debug mode
      -e, --examples        Show example usage
  
**Required arguments:**

      -i INPUT_FILE, --input-file INPUT_FILE
                            Path to file containing password hashes to attempt to crack

## Examples:

### Using Base Words Mode

Attempt to crack linked-in hashes using base words linkedin and linked

	python3 byepass.py --verbose --hash-format=Raw-SHA1 --base-words=linkedin,linked --input-file=linkedin-1.hashes

	python3 byepass.py -v -f Raw-SHA1 -w linkedin,linked -i linkedin-1.hashes

### Using Brute Force Mode

Attempt to brute force words from 3 to 5 characters in length

	python3 byepass.py --verbose --hash-format=Raw-MD5 --brute-force=3,5 --input-file=hashes.txt

    python3 byepass.py -f Raw-MD5 -j="--fork=4" -v -t 0 -b 3,5 -i hashes.txt

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