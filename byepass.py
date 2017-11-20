# JTR Mask Mode: https://github.com/magnumripper/JohnTheRipper/blob/bleeding-jumbo/doc/MASK

# - Static letters.
# - Ranges in [aouei] or [a-z] syntax. Or both, [0-9abcdef] is the same as
#      [0-9a-f].
# - Placeholders that are just a short form for ranges, like ?l which is
#      100% equivalent to [a-z].
# - ?l lower-case ASCII letters
# - ?u upper-case ASCII letters
# - ?d digits
# - ?s specials (all printable ASCII characters not in ?l, ?u or ?d)
# - ?a full 'printable' ASCII. Note that for formats that don't recognize case
#      (eg. LM), this only includes lower-case characters which is a tremendous
#      reduction of keyspace for the win.
# - ?B all 8-bit (0x80-0xff)
# - ?b all (0x01-0xff) (the NULL character is currently not supported by core).
# - ?h lower-case HEX digits (0-9, a-f)
# - ?H upper-case HEX digits (0-9, A-F)
# - ?L lower-case non-ASCII letters
# - ?U upper-case non-ASCII letters
# - ?D non-ASCII "digits"
# - ?S non-ASCII "specials"
# - ?A all valid characters in the current code page (including ASCII). Note
#      that for formats that don't recognize case (eg. LM), this only includes
#      lower-case characters which is a tremendous reduction of keyspace.
# - Placeholders that are custom defined, so we can e.g. define ?1 to mean [?u?l]
#   ?1 .. ?9 user-defined place-holder 1 .. 9
# - Placeholders for Hybrid Mask mode:
#   ?w is a placeholder for the original word produced by the parent mode in
#      Hybrid Mask mode.
#   ?W is just like ?w except the original word is case toggled (so PassWord
#      becomes pASSwORD).

import argparse, subprocess
from argparse import RawTextHelpFormatter
from pwstats import PasswordStats
import time

JTR_POT_FILE_PATH = "/opt/john/run/john.pot"
JTR_FILE_PATH = "/opt/john/run/john"


def parse_jtr_show(pVerbose: bool, pDebug: bool) -> None:

    lCompletedProcess = subprocess.run([JTR_FILE_PATH, "--show", "--format=descrypt", lHashFile], stdout=subprocess.PIPE)
    lCrackedPasswords = lCompletedProcess.stdout.split(b'\n')
    for lCrackedPassword in lCrackedPasswords:
        try:
            print(lCrackedPassword.decode("utf-8"))
        except:
            # do nothing
            print()


def parse_jtr_pot(pVerbose: bool, pDebug: bool) -> list:

    lPotFile = []
    lListOfPasswords = []
    if pVerbose:
        print()
        print("[*] Reading input file " + JTR_POT_FILE_PATH)
    with open(JTR_POT_FILE_PATH, READ_BYTES) as lFile:
        lPotFile = lFile.readlines()
    if pVerbose: print("[*] Finished reading input file " + JTR_POT_FILE_PATH)

    for lLine in lPotFile:
        if not lLine[0:3] == b'$LM':
            lPassword = lLine.strip().split(b':')[1]
            if not lPassword in lListOfPasswords:
                lListOfPasswords.append(lPassword)

    return lListOfPasswords


def run_jtr(pMethod: int, pVerbose: bool, pDebug: bool) -> None:

    lStartTime = 0
    lEndTime = 0

    if pVerbose:
        lStartTime = time.time()
        print("[*] Working on file {}".format(lHashFile))

    if pDebug:
        lCompletedProcess = subprocess.run(["rm", JTR_POT_FILE_PATH], stdout=subprocess.PIPE)
        print("[*] Deleted file {}".format(JTR_POT_FILE_PATH))
        time.sleep(1)

    if pMethod == 1:
        if pVerbose: print("[*] Starting mode: Wordlist passwords-hailmary.txt")
        lCompletedProcess = subprocess.run([JTR_FILE_PATH, "--format=descrypt", "--wordlist=passwords/passwords-hailmary.txt", lHashFile], stdout=subprocess.PIPE)
    elif pMethod == 2:
        if pVerbose: print("[*] Starting mode: Wordlist top-10000-english-words.txt Rule best64")
        lCompletedProcess = subprocess.run([JTR_FILE_PATH, "--format=descrypt", "--wordlist=dictionaries/top-10000-english-words.txt", "--rules=best64", lHashFile], stdout=subprocess.PIPE)
    elif pMethod == 3:
        if pVerbose: print("[*] Starting mode: Wordlist worst-10000-passwords.txt Rule best64")
        lCompletedProcess = subprocess.run([JTR_FILE_PATH, "--format=descrypt", "--wordlist=passwords/worst-10000-passwords.txt", "--rules=best64", lHashFile], stdout=subprocess.PIPE)
    elif pMethod == 4:
        if pVerbose: print("[*] Starting mode: Wordlist hob0-short-crack.txt Rule best64")
        lCompletedProcess = subprocess.run([JTR_FILE_PATH, "--format=descrypt", "--wordlist=dictionaries/hob0-short-crack.txt", "--rules=best64", lHashFile], stdout=subprocess.PIPE)
    elif pMethod == 5:
        if pVerbose: print("[*] Starting mode: Wordlist other-base-words.txt Rule best64")
        lCompletedProcess = subprocess.run([JTR_FILE_PATH, "--format=descrypt", "--wordlist=dictionaries/other-base-words.txt", "--rules=best64", lHashFile], stdout=subprocess.PIPE)
    elif pMethod == 6:
        if pVerbose: print("[*] Starting mode: Wordlist sports-related-words.txt Rule best64")
        lCompletedProcess = subprocess.run([JTR_FILE_PATH, "--format=descrypt", "--wordlist=dictionaries/sports-related-words.txt", "--rules=best64", lHashFile], stdout=subprocess.PIPE)
    elif pMethod == 7:
        if pVerbose: print("[*] Starting mode: Wordlist female-given-names.txt Rule best64")
        lCompletedProcess = subprocess.run([JTR_FILE_PATH, "--format=descrypt", "--wordlist=dictionaries/female-given-names.txt", "--rules=best64", lHashFile], stdout=subprocess.PIPE)

    elif pMethod == 8:
        if pVerbose: print("[*] Starting mode: Wordlist top-10000-english-words.txt Rule korelogic")
        lCompletedProcess = subprocess.run([JTR_FILE_PATH, "--format=descrypt", "--wordlist=dictionaries/top-10000-english-words.txt", "--rules=korelogic", lHashFile], stdout=subprocess.PIPE)

    elif pMethod == 9:
        if pVerbose: print("[*] Starting mode: Wordlist top-10000-english-words.txt Rule d3adhob0")
        lCompletedProcess = subprocess.run([JTR_FILE_PATH, "--format=descrypt", "--wordlist=dictionaries/top-10000-english-words.txt", "--rules=d3adhob0", lHashFile], stdout=subprocess.PIPE)



    #print(lCompletedProcess.stdout)
    time.sleep(1)

    if pVerbose:
        lEndTime = time.time()
        lListOfPasswords = parse_jtr_pot(True, True)
        print("[*] Finished")
        print("Duration: {}".format(lEndTime - lStartTime))
        print("[*] Passwords cracked: " + str(lListOfPasswords.__len__()))

    time.sleep(1)

if __name__ == '__main__':

    READ_BYTES = 'rb'
    READ_LINES = 'r'
    JTR_POT_FILE_PATH = "/opt/john/run/john.pot"

    lArgParser = argparse.ArgumentParser(description='ByePass: Automate the most common password cracking tasks',
                                         epilog='',
                                         formatter_class=RawTextHelpFormatter)
    lArgParser.add_argument('-s', '--stat-crack',
                            help='Enable smart crack. Byepass will run relatively fast cracking strategies in hopes of cracking enough passwords to induce a pattern and create "high probability" masks. Byepass will use the masks in an attempt to crack more passwords.',
                            action='store_true')
    lArgParser.add_argument('-v', '--verbose',
                            help='Enable verbose output',
                            action='store_true')
    lArgParser.add_argument('-i', '--input-file',
                            help='Path to file containing hashes',
                            action='store', required=True)
    lArgs = lArgParser.parse_args()

    # john --single
    # Specific dictionaries and rules
    # Specific masks
    # General wordlists

    lHashFile = lArgs.input_file

    #for i in range(1,8,1):
    run_jtr(8, True, True)
    time.sleep(1)
    run_jtr(9, True, True)
    time.sleep(1)

    if lArgs.stat_crack:

        lListOfPasswords = parse_jtr_pot(True, True)

        if lArgs.verbose:
            lCountPasswords = lListOfPasswords.__len__()
            print("[*] Passwords imported: " + str(lCountPasswords))
            if lCountPasswords > 1000000: print("[*] That is a lot of passwords. Parsing may take a while.")

        if lArgs.verbose: print("[*] Parsing input file " + JTR_POT_FILE_PATH)
        lPasswordStats = PasswordStats(lListOfPasswords)
        if lArgs.verbose:
            print("[*] Finished parsing input file " + JTR_POT_FILE_PATH)
            print("[*] Parsed {} passwords into {} masks".format(lPasswordStats.count_passwords, lPasswordStats.count_masks))

        if lArgs.verbose: print("[*] Password masks ({} percentile):".format(lArgs.percentile), end='')
        print(lPasswordStats.masks)