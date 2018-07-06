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

from argparse import RawTextHelpFormatter
from pwstats import PasswordStats
from enum import Enum
import config as Config
import argparse
import subprocess
import os.path
import time
import re

# GLOBALS
masks_already_brute_forced = []

#METHODS
def print_example_usage():
    print("""
Attempt to crack linked-in hashes using base words linkedin and linked\n
\tpython3 byepass.py --verbose --hash-format=Raw-SHA1 --basewords=linkedin,linked --input-file=linkedin-1.hashes
\tpython3 byepass.py -v -f Raw-SHA1 -w linkedin,linked -i linkedin-1.hashes\n
Attempt to brute force words from 3 to 5 characters in length\n
\tpython3 byepass.py --verbose --hash-format=Raw-MD5 --brute-force=3,5 --input-file=hashes.txt
\tpython3 byepass.py -f Raw-MD5 -j="--fork=4" -v -t 0 -r 3,5 -i hashes.txt\n
Attempt to crack password hashes found in input file "password.hashes" using default techniques level 1\n
\tpython3 byepass.py --verbose --hash-format=descrypt --input-file=password.hashes
\tpython3 byepass.py -v -f descrypt -i password.hashes\n
Be more aggressive by using techniques level 2 in attempt to crack password hashes found in input file "password.hashes"\n
\tpython3 byepass.py --verbose --techniques=2 --hash-format=descrypt --input-file=password.hashes
\tpython3 byepass.py -v -a 2 -f descrypt -i password.hashes\n
Go bonkers and try all techniques. Start with technique level 1 and proceed to level 13 in attempt to crack password hashes found in input file "password.hashes"\n
\tpython3 byepass.py --verbose --techniques=1,2,3,4,5,6,7,8,9,10,11,12,13 --hash-format=descrypt --input-file=password.hashes
\tpython3 byepass.py -v -a 1,2,3,4 -f descrypt -i password.hashes\n
Only try first two techniques. Start with technique level 1 and proceed to level 2 in attempt to crack password hashes found in input file "password.hashes"\n
\tpython3 byepass.py --verbose --techniques=1,2 --hash-format=descrypt --input-file=password.hashes
\tpython3 byepass.py -v -a 1,2 -f descrypt -i password.hashes\n
Attempt to crack password hashes found in input file "password.hashes", then run statistical analysis to determine masks needed to crack 50 percent of passwords, and try to crack again using the masks.\n
\tpython3 byepass.py --verbose --hash-format=descrypt --stat-crack --percentile=0.50 --input-file=password.hashes
\tpython3 byepass.py -v -f descrypt -s -p 0.50 -i password.hashes\n
\"Real life\" example attempting to crack 25 percent of the linked-in hash set\n
\tpython3 byepass.py --verbose --hash-format=Raw-SHA1 --stat-crack --percentile=0.25 --input-file=linkedin.hashes
\tpython3 byepass.py -v -f Raw-SHA1 -s -f 0.25 -i linkedin.hashes\n
Attempt to crack linked-in hashes using base words linkedin and linked\n
\tpython3 byepass.py --verbose --hash-format=Raw-SHA1 --basewords=linkedin,linked --input-file=linkedin-1.hashes
\tpython3 byepass.py -v -f -w linkedin,linked -i linkedin-1.hashes\n
Do not run prayer mode. Only run statistical analysis to determine masks needed to crack 50 percent of passwords, and try to crack using the masks.\n
\tpython3 byepass.py -v --techniques=0 --hash-format=descrypt --stat-crack --percentile=0.50 --input-file=password.hashes
\tpython3 byepass.py -v -a 0 -f descrypt -s -p 0.50 -i password.hashes\n
Use pass-through to pass fork command to JTR\n
\tpython3 byepass.py --verbose --pass-through="--fork=4" --hash-format=descrypt --input-file=password.hashes
\tpython3 byepass.py -v -j="--fork=4" -f descrypt -i password.hashes
""")


def parse_arg_percentile(pArgPercentile: float) -> float:

    if pArgPercentile:
        if not 0.0 <= pArgPercentile <= 1.00:
            raise ValueError('The percentile provided must be between 0.0 and 1.0.')
        return pArgPercentile
    else:
        return 1.0


def parse_arg_debug(pArgDebug: bool) -> bool:
    if pArgDebug:
        return pArgDebug
    else:
        return DEBUG


def parse_arg_hash_format(pArgHashFormat: str) -> str:
    if pArgHashFormat is not None:
        return lArgs.hash_format
    else:
        return ""


def parse_arg_techniques(pArgTechniques: str) -> list:
    lTechniques = [1]

    if lArgs.techniques is not None:

        lErrorMessage = 'Techniques must be supplied as a comma-separated list of integers between 0 and 13'

        try:
            lTechniques = list(map(int, pArgTechniques.split(",")))
        except:
            raise ValueError(lErrorMessage)

        lObservedTechniques = []
        for lTechnique in lTechniques:
            if 0 <= lTechnique <= 13:
                if lTechnique in lObservedTechniques:
                    raise ValueError('Duplicate technique specified: {} '.format(lTechnique) + lErrorMessage)
                lObservedTechniques.append(lTechnique)
            else:
                raise ValueError(lErrorMessage)

        lTechniques.sort()

    return lTechniques


def parse_arg_brute_force(pArgBruteForce: str) -> tuple:

    lSyntaxErrorMessage = 'Amount of characters to bruce-force must be a comma-separated pair of positive integer greater than 0. The MIN must be less than or equal to the MAX.'
    lValueErrorMessage = 'For amount of characters to bruce-force, the MIN must be less than or equal to the MAX.'

    try:
        lParameters = [x.strip() for x in pArgBruteForce.split(',')]
        lMinCharactersToBruteForce = int(lParameters[0])
        lMaxCharactersToBruteForce = int(lParameters[1])

        if lMinCharactersToBruteForce < 1:
            raise ValueError(lSyntaxErrorMessage)
        if lMaxCharactersToBruteForce < 1:
            raise ValueError(lSyntaxErrorMessage)
        if lMaxCharactersToBruteForce < lMinCharactersToBruteForce:
            raise ValueError(lValueErrorMessage)
        return lMinCharactersToBruteForce, lMaxCharactersToBruteForce
    except:
        raise ValueError(lSyntaxErrorMessage)


def print_closing_message(pNumberHashes: int, pNumberPasswordsPOTFileAtStart: int,
                          pStartTime: float, pEndTime: float) -> None:

        lNumberPasswords = count_passwords_in_jtr_pot_file() - pNumberPasswordsPOTFileAtStart
        lElaspsedTime = time.gmtime(pEndTime - pStartTime)
        lDurationSeconds = pEndTime - pStartTime
        lNumberPasswordsCrackedPerSecond = lNumberPasswords // lDurationSeconds

        try:
            lPercent = round(lNumberPasswords / pNumberHashes * 100, 2)
        except:
            lPercent = 0

        print("[*] Duration: {}".format(time.strftime("%H:%M:%S", lElaspsedTime)))
        print("[*] Passwords cracked (estimated): {} out of {} ({}%)".format(lNumberPasswords, pNumberHashes, lPercent))
        print("[*] Passwords cracked per second (estimated): {}".format(lNumberPasswordsCrackedPerSecond))
        print()
        print("[*] Cracking attempt complete. Use john --show to see cracked passwords.")
        print("[*] The command should be something like {}{}{} --show {}".format(JTR_EXE_FILE_PATH, " --format=" if lHashFormat else "", lHashFormat, lHashFile))
        print()
        print("[*] Keep cracking with incremental mode")
        print("[*] The command should be something like {}{}{} --incremental {}".format(JTR_EXE_FILE_PATH, " --format=" if lHashFormat else "", lHashFormat, lHashFile))


def parse_jtr_show(pHashFile: str, pHashFormat:str, pVerbose: bool, pDebug: bool) -> None:

    lCmdArgs = [JTR_EXE_FILE_PATH]
    lCmdArgs.append("--show")
    if pHashFormat: lCmdArgs.append("--format={}".format(pHashFormat))
    lCmdArgs.append(pHashFile)
    lCompletedProcess = subprocess.run(lCmdArgs, stdout=subprocess.PIPE)
    lCrackedPasswords = lCompletedProcess.stdout.split(b'\n')
    for lCrackedPassword in lCrackedPasswords:
        try: print(lCrackedPassword.decode("utf-8"))
        except: pass


def parse_jtr_pot(pVerbose: bool, pDebug: bool) -> list:

    lListOfPasswords = []
    if pVerbose: print("[*] Reading input file " + JTR_POT_FILE_PATH)
    with open(JTR_POT_FILE_PATH, READ_BYTES) as lFile:
        lPotFile = lFile.readlines()
    if pVerbose: print("[*] Finished reading input file " + JTR_POT_FILE_PATH)

    if pVerbose: print("[*] Processing input file " + JTR_POT_FILE_PATH)
    for lLine in lPotFile:
        #LANMAN passwords are case-insensitive so they throw off statistical analysis
        #For LANMAN, we assume lowercase (most popular choice) but errors will be inherent
        if not lLine[0:3] == b'$LM':
            lPassword = lLine.strip().split(b':')[1]
        else:
            lPassword = lLine.strip().split(b':')[1].lower()
        lListOfPasswords.append(lPassword)
    if pVerbose: print("[*] Finished processing input file " + JTR_POT_FILE_PATH)

    return lListOfPasswords


def count_hashes_in_input_file(pHashFile: str) -> int:

        lLines = 0
        for lLine in open(pHashFile):
            lLines += 1
        return lLines


def count_passwords_in_jtr_pot_file() -> int:

    lLines = 0
    try:
        if os.path.exists(JTR_POT_FILE_PATH):
            for lLine in open(JTR_POT_FILE_PATH):
                lLines += 1
    except:
        lLines = 0
    return lLines


def rm_jtr_pot_file() -> None:

    if os.path.exists(JTR_POT_FILE_PATH):
        lCompletedProcess = subprocess.run(["rm", JTR_POT_FILE_PATH], stdout=subprocess.PIPE)
        print("[*] Deleted file {}".format(JTR_POT_FILE_PATH))
        time.sleep(1)


def run_jtr_baseword_mode(pHashFile: str, pBaseWords: str, pHashFormat: str,
                          pVerbose: bool, pDebug: bool, pPassThrough: str,
                          pNumberHashes: int) -> None:

    if pVerbose: print("[*] Starting mode: Baseword with words {}".format(pBaseWords))

    lBaseWords = list(pBaseWords.split(","))
    lBaseWordsFileName = 'basewords/basewords.txt'
    lBaseWordsDirectory = os.path.dirname(lBaseWordsFileName)
    if not os.path.exists(lBaseWordsDirectory): os.makedirs(lBaseWordsDirectory)
    lBaseWordsFile = open(lBaseWordsFileName, 'w')
    for lWord in lBaseWords:
        lBaseWordsFile.write("%s\n" % lWord)
    lBaseWordsFile.flush()
    lBaseWordsFile.close()
    run_jtr_wordlist_mode(pHashFile=pHashFile, pWordlist="basewords/basewords.txt", pRule="Best126",
                          pHashFormat=pHashFormat, pVerbose=pVerbose, pDebug=pDebug,
                          pPassThrough=pPassThrough, pNumberHashes=pNumberHashes)
    run_jtr_wordlist_mode(pHashFile=pHashFile, pWordlist="basewords/basewords.txt", pRule="OneRuleToRuleThemAll",
                          pHashFormat=pHashFormat, pVerbose=pVerbose, pDebug=pDebug,
                          pPassThrough=pPassThrough, pNumberHashes=pNumberHashes)
    run_jtr_wordlist_mode(pHashFile=pHashFile, pWordlist="basewords/basewords.txt", pRule="All",
                          pHashFormat=pHashFormat, pVerbose=pVerbose, pDebug=pDebug,
                          pPassThrough=pPassThrough, pNumberHashes=pNumberHashes)
    os.remove(lBaseWordsFileName)

    if pVerbose: print("[*] Finished Baseword Mode")


def run_jtr_wordlist_mode(pHashFile: str, pWordlist: str, pRule: str, pHashFormat:str,
                          pVerbose: bool, pDebug: bool, pPassThrough: str,
                          pNumberHashes: int) -> None:

    lStartTime = time.time()

    if pDebug: rm_jtr_pot_file()

    lCmdArgs = [JTR_EXE_FILE_PATH]
    if pHashFormat: lCmdArgs.append("--format={}".format(pHashFormat))
    lCmdArgs.append("--wordlist={}".format(pWordlist))
    if pRule: lCmdArgs.append("--rule={}".format(pRule))
    if pPassThrough: lCmdArgs.append(pPassThrough)
    lCmdArgs.append(pHashFile)

    if pVerbose:
        print("[*] Starting wordlist mode: {}".format(pWordlist))
        if pRule: print("[*] Using rule: {}".format(pRule))

    # Determine number of passwords cracked before trying this method
    lNumberPasswordsAlreadyCracked = count_passwords_in_jtr_pot_file()

    if pVerbose:
        print("[*] Passwords cracked before using wordlist {}: {}".format(pWordlist, lNumberPasswordsAlreadyCracked))

    lCompletedProcess = subprocess.run(lCmdArgs, stdout=subprocess.PIPE)
    time.sleep(1)

    # Determine number of passwords cracked after trying this method
    lNumberPasswordsCracked = count_passwords_in_jtr_pot_file()

    lNumberPasswordsCrackedByThisMethod = lNumberPasswordsCracked - lNumberPasswordsAlreadyCracked
    lPercentPasswordsCracked = round(lNumberPasswordsCrackedByThisMethod / pNumberHashes * 100, 2)
    print("[*] Passwords cracked using wordlist {}: {} ({} percent)".format(pWordlist, lNumberPasswordsCrackedByThisMethod, lPercentPasswordsCracked))

    if pVerbose:
        print("[*] Finished wordlist mode: {}".format(pWordlist))
        if pRule: print("\tUsed rule: {}".format(pRule))
        print("\tCommand: {}".format(lCompletedProcess.args))
        #print(lCompletedProcess.stdout)
        print("\tPasswords cracked: {} ({} percent)".format(lNumberPasswordsCrackedByThisMethod, lPercentPasswordsCracked))

    if pDebug:
        lRunTime = time.time() - lStartTime
        lPasswordsCrackedPerSecond = lNumberPasswordsCrackedByThisMethod // lRunTime
        print("[*] Duration: {}".format(lRunTime))
        print("[*] Passwords cracked per second: {}".format(lPasswordsCrackedPerSecond))


def run_jtr_mask_mode(pHashFile: str, pMask: str, pWordlist: str, pHashFormat:str,
                      pVerbose: bool, pDebug: bool, pPassThrough: str,
                      pNumberHashes: int) -> None:

    # There are two modes that run brute force using masks. Keep track of masks
    # already checked in case the same mask would be tried twice.

    #Note: masks_already_brute_forced is a global variable
    if pMask in masks_already_brute_forced:
        if pVerbose:
            print("[*] Mask {} has already been tested in this session. Moving on to next task.".format(pMask))
        return None
    else:
        masks_already_brute_forced.append(pMask)

    lStartTime = time.time()

    if pDebug: rm_jtr_pot_file()

    lCmdArgs = [JTR_EXE_FILE_PATH]
    if pHashFormat: lCmdArgs.append("--format={}".format(pHashFormat))
    lCmdArgs.append("--mask={}".format(pMask))
    if pWordlist: lCmdArgs.append("--wordlist={}".format(pWordlist))
    if pPassThrough: lCmdArgs.append(pPassThrough)
    lCmdArgs.append(pHashFile)

    if pVerbose:
        print("[*] Starting mask mode: {}".format(pMask))
        if pWordlist: print("[*] Using wordlist: {}".format(pWordlist))

    # Determine number of passwords cracked before trying this method
    lNumberPasswordsAlreadyCracked = count_passwords_in_jtr_pot_file()

    if pVerbose:
        print("[*] Passwords cracked before using mask {}: {}".format(pMask, lNumberPasswordsAlreadyCracked))

    lCompletedProcess = subprocess.run(lCmdArgs, stdout=subprocess.PIPE)
    time.sleep(1)

    # Determine number of passwords cracked after trying this method
    lNumberPasswordsCracked = count_passwords_in_jtr_pot_file()

    lNumberPasswordsCrackedByThisMethod = lNumberPasswordsCracked - lNumberPasswordsAlreadyCracked
    lPercentPasswordsCracked = round(lNumberPasswordsCrackedByThisMethod / pNumberHashes * 100, 2)
    print("[*] Passwords cracked using mask {}: {} ({} percent)".format(pMask, lNumberPasswordsCrackedByThisMethod, lPercentPasswordsCracked))

    if pVerbose:
        print("[*] Finished mask mode: {}".format(pMask))
        print("\tCommand: {}".format(lCompletedProcess.args))
        print("\tPasswords cracked: {} ({} percent)".format(lNumberPasswordsCrackedByThisMethod, lPercentPasswordsCracked))

    if pDebug:
        lRunTime = time.time() - lStartTime
        lPasswordsCrackedPerSecond = lNumberPasswordsCrackedByThisMethod // lRunTime
        print("[*] Duration: {}".format(lRunTime))
        print("[*] Passwords cracked per second: {}".format(lPasswordsCrackedPerSecond))


def perform_statistical_cracking(pHashFile: str, pPercentile: float, pHashFormat: str,
                                 pVerbose: bool, pDebug: bool, pPassThrough: str,
                                 pNumberHashes: int) -> None:

    # The JTR POT file is the source of passwords
    if pVerbose: print("[*] Parsing JTR POT file at {}".format(JTR_POT_FILE_PATH))
    lListOfPasswords = parse_jtr_pot(pVerbose, True)

    if pVerbose:
        lCountPasswords = lListOfPasswords.__len__()
        print("[*] Using {} passwords in statistical analysis: ".format(str(lCountPasswords)))
        if lCountPasswords > 1000000: print("[*] That is a lot of passwords. Statistical analysis may take a while.")

    # Let PasswordStats class analyze most likely masks
    if pVerbose: print("[*] Beginning statistical analysis")
    lPasswordStats = PasswordStats(lListOfPasswords)
    if pVerbose: print(
        "[*] Parsed {} passwords into {} masks".format(lPasswordStats.count_passwords, lPasswordStats.count_masks))

    # Calculate masks most likely need to crack X% of the password hashes
    lMasks = lPasswordStats.get_popular_masks(lPercentile)
    if pVerbose: print("[*] Password masks ({} percentile): {}".format(pPercentile, lMasks))

    # For each mask, try high probability guesses
    lUndefinedMasks = []
    for lMask in lMasks:
        if pVerbose: print("[*] Processing mask: {}".format(lMask))

        # If the number of characters in the mask is "small" as defined by
        # MAX_CHARS_TO_BRUTEFORCE, then use brute-force on the pattern.
        # If there are more characters than the limit, use "smart brute-force"
        # which is a hybrid between dictionary and mask mode.
        lCountCharacters = int(len(lMask) / 2)
        if lCountCharacters <= MAX_CHARS_TO_BRUTEFORCE:
            lWordlist = ""
            run_jtr_mask_mode(pHashFile=pHashFile, pMask=lMask, pWordlist=lWordlist,
                              pHashFormat=pHashFormat, pVerbose=pVerbose, pDebug=pDebug,
                              pPassThrough=pPassThrough, pNumberHashes=pNumberHashes)
        else:

            # All lowercase letters
            if re.match('^(\?l)+$', lMask):
                lCountLetters = lMask.count('?l')
                if lCountLetters > MAX_CHARS_TO_BRUTEFORCE:
                    lWordlist = "dictionaries/{}-character-words.txt".format(str(lCountLetters))
                    lRule=""
                    run_jtr_wordlist_mode(pHashFile=pHashFile, pWordlist=lWordlist, pRule=lRule, pHashFormat=pHashFormat,
                                          pVerbose=pVerbose, pDebug=pDebug, pPassThrough=pPassThrough,
                                          pNumberHashes=pNumberHashes)

            # All uppercase
            elif re.match('^(\?u)+$', lMask):
                lCountLetters = lMask.count('?u')
                lWordlist = "dictionaries/{}-character-words.txt".format(str(lCountLetters))
                lRule = "uppercase"
                run_jtr_wordlist_mode(pHashFile=pHashFile, pWordlist=lWordlist, pRule=lRule, pHashFormat=pHashFormat,
                                      pVerbose=pVerbose, pDebug=pDebug, pPassThrough=pPassThrough,
                                      pNumberHashes=pNumberHashes)

            # Uppercase followed by lowercase (assume only leading letter is uppercase)
            elif re.match('^(\?u)(\?l)+$', lMask):
                lCountLetters = lMask.count('?u') + lMask.count('?l')
                lWordlist = "dictionaries/{}-character-words.txt".format(str(lCountLetters))
                lRule = "capitalize"
                run_jtr_wordlist_mode(pHashFile=pHashFile, pWordlist=lWordlist, pRule=lRule, pHashFormat=pHashFormat,
                                      pVerbose=pVerbose, pDebug=pDebug, pPassThrough=pPassThrough,
                                      pNumberHashes=pNumberHashes)

            # Lowercase ending with digits
            elif re.match('^(\?l)+(\?d)+$', lMask):
                lCountLetters = lMask.count('?l')
                lCountDigits = lMask.count('?d')
                lWordlist = "dictionaries/{}-character-words.txt".format(str(lCountLetters))
                lRule = "append{}digits".format(str(lCountDigits))
                run_jtr_wordlist_mode(pHashFile=pHashFile, pWordlist=lWordlist, pRule=lRule, pHashFormat=pHashFormat,
                                      pVerbose=pVerbose, pDebug=pDebug, pPassThrough=pPassThrough,
                                      pNumberHashes=pNumberHashes)

            # Uppercase followed by digits
            elif re.match('^(\?u)+(\?d)+$', lMask):
                lCountLetters = lMask.count('?u')
                lCountDigits = lMask.count('?d')
                lWordlist = "dictionaries/{}-character-words.txt".format(str(lCountLetters))
                lRule = "uppercaseappend{}digits".format(str(lCountDigits))
                run_jtr_wordlist_mode(pHashFile=pHashFile, pWordlist=lWordlist, pRule=lRule, pHashFormat=pHashFormat,
                                      pVerbose=pVerbose, pDebug=pDebug, pPassThrough=pPassThrough,
                                      pNumberHashes=pNumberHashes)

            # Uppercase, lowercase, then digits (assume only leading letter is uppercase)
            elif re.match('^(\?u)(\?l)+(\?d)+$', lMask):
                lCountLetters = lMask.count('?u') + lMask.count('?l')
                lCountDigits = lMask.count('?d')
                lWordlist = "dictionaries/{}-character-words.txt".format(str(lCountLetters))
                lRule = "capitalizeappend{}digits".format(str(lCountDigits))
                run_jtr_wordlist_mode(pHashFile=pHashFile, pWordlist=lWordlist, pRule=lRule, pHashFormat=pHashFormat,
                                      pVerbose=pVerbose, pDebug=pDebug, pPassThrough=pPassThrough,
                                      pNumberHashes=pNumberHashes)

            # Low number of digits. We do not cover large numbers of digits because
            # precomputing dictionary files would be huge and running mask mode takes a long time.
            # Right now we support 4-6 digits only. Recall we cover 4 and 6 digits specifically in
            # "prayer" mode so we do not repeat those two masks here.
            elif re.match('^(\?d)+$', lMask):
                lCountDigits = lMask.count('?d')
                if lCountDigits == 5:
                    lWordlist = "dictionaries/{}-digit-numbers.txt".format(str(lCountDigits))
                    run_jtr_wordlist_mode(pHashFile=pHashFile, pWordlist=lWordlist, pRule="", pHashFormat=pHashFormat,
                                          pVerbose=pVerbose, pDebug=pDebug, pPassThrough=pPassThrough,
                                          pNumberHashes=pNumberHashes)
                else:
                    print("[*] WARNING: Did not process mask {} because it is out of policy".format(lMask))

            # Lowercase ending with something other than the masks already accounted for. If the
            # ending pattern is longer than 4 characters, we do not try because it takes a long time
            # to test that many hashes
            elif re.match('^(\?l)+', lMask):
                lPrefix = re.search('^(\?l)+', lMask).group()
                lCountLetters = lPrefix.count("?l")
                lSuffix = lMask[lCountLetters * 2:]
                if len(lSuffix) <= 4:
                    lWordlist = "dictionaries/{}-character-words.txt".format(str(lCountLetters))
                    lMaskParam = "--mask=?w{}".format(lSuffix)
                    run_jtr_mask_mode(pHashFile=pHashFile, pMask=lMaskParam, pWordlist=lWordlist, pHashFormat=pHashFormat,
                                      pVerbose=pVerbose, pDebug=pDebug, pPassThrough=pPassThrough,
                                      pNumberHashes=pNumberHashes)
                else:
                    print("[*] WARNING: Did not process mask {} because it is out of policy".format(lMask))

            else:
                lUndefinedMasks.append(lMask)
                print("[*] WARNING: No policy defined for mask {}".format(lMask))

    # List masks that did not match a pattern so that a pattern can be added
    if lUndefinedMasks: print(
        "[*] WARNING: There was no policy defined for the following masks: {}".format(lUndefinedMasks))

def run_jtr_brute_force_mode(pHashFile: str, pMinCharactersToBruteForce: int,
                             pMaxCharactersToBruteForce: int,
                             pHashFormat: str, pPassThrough: str,
                             pVerbose: bool, pDebug: bool, pNumberHashes: int) -> None:

    for i in range(pMinCharactersToBruteForce, pMaxCharactersToBruteForce + 1):
        lLowersMask = "?l" * i
        lUppersMask = "?u" * i
        lDigitsMask = "?d" * i
        lMasks = [lLowersMask, lUppersMask, lDigitsMask]

        # UpperLower pattern requires at least 2 characters
        if i > 1:
            lUpperLowersMask = "?u" + "?l" * (i - 1)
            lMasks.append(lUpperLowersMask)

        #From 1 digit up to i-1 digits where i is length of pattern
        for j in range(1, i):
            lLowerDigitMask = "?l" * (i-j) + "?d" * j
            lUpperDigitMask = "?u" * (i-j) + "?d" * j
            lMasks.append(lLowerDigitMask)
            lMasks.append(lUpperDigitMask)

            # Only generate capitalized if pattern at least 3 characters (i > 2)
            # long and starts with at least an upper and a lower (i - j >= 2)
            if (i > 2) and (i - j >= 2):
                lUpperLowerDigitMask = "?u" + "?l" * (i-j-1) + "?d" * j
                lMasks.append(lUpperLowerDigitMask)

        for lMask in lMasks:
            run_jtr_mask_mode(pHashFile=pHashFile, pMask=lMask, pWordlist=None,
                              pHashFormat=pHashFormat, pPassThrough=pPassThrough,
                              pVerbose=pVerbose, pDebug=pDebug, pNumberHashes=pNumberHashes)


def run_jtr_prayer_mode(pHashFile: str, pMethod: int, pHashFormat: str,
                           pPassThrough: str, pVerbose: bool, pDebug: bool,
                           pNumberHashes: int) -> None:

    if pMethod == 1:
        # Dictionaries have less than 10,000 words
        # Rules have up to about 1,000 mangles
        # Factor: <10,000,000
        lFolder = "dictionaries"
        lDictionaries = ["calendar.txt", "short-list.txt", "brands.txt","movie-characters.txt",
                         "animals.txt","astrology.txt","songs.txt"]
        lRules = ["SlowHashesPhase1", "Best126", "SlowHashesPhase2"]

        # <1,000 words and <10,000 mangles
        # Factor: <100,000
        do_run_jtr_prayer_mode(pHashFile=pHashFile, pDictionary="dictionaries/calendar.txt",
                               pRule="Calendar", pHashFormat=pHashFormat,
                               pPassThrough=pPassThrough, pVerbose=pVerbose,
                               pDebug=pDebug, pNumberHashes=pNumberHashes)

        # Hard to say how many mangles but will be proportional to number of hashes
        do_run_jtr_single_mode(pHashFile=pHashFile, pHashFormat=pHashFormat,
                               pPassThrough=pPassThrough, pVerbose=pVerbose,
                               pDebug=pDebug, pNumberHashes=pNumberHashes)

    elif pMethod == 2:
        # Dictionaries have about 10,000 words
        # Rules have up to about 1,000 mangles
        # Factor: 10,000,000
        lFolder = "dictionaries"
        lDictionaries = ["sports-related-words.txt","bible.txt","top-10000-english-words.txt",
                         "top-10000-spanish-words.txt","top-10000-german-words.txt"]
        lRules = ["SlowHashesPhase1", "Best126", "SlowHashesPhase2"]

    elif pMethod == 3:
        # Dictionaries have less than 10,000 words
        # Rules have up to about 6,500 mangles
        # Factor: <65,000,000

        lFolder = "dictionaries"
        lDictionaries = ["calendar.txt", "short-list.txt", "brands.txt","movie-characters.txt",
                         "animals.txt","astrology.txt","songs.txt"]
        lRules = ["SlowHashesPhase3"]

    elif pMethod == 4:
        # Dictionaries have about 10,000 words
        # Rules have up to about 6,500 mangles
        # Factor: 65,000,000
        lFolder = "dictionaries"
        lDictionaries = ["sports-related-words.txt","bible.txt","top-10000-english-words.txt",
                         "top-10000-spanish-words.txt","top-10000-german-words.txt"]
        lRules = ["SlowHashesPhase3"]

    elif pMethod == 5:
        # Dictionaries has 40,000,000 words
        # Rules has 1 mangles
        # Factor: 80,000,000
        lFolder = "passwords"
        lDictionaries = ["passwords-hailmary.txt"]
        lRules = ["Hailmary"]

    elif pMethod == 6:
        # Dictionaries has 50,000 words
        # Rules have up to about 1,000 mangles
        # Factor: 50,000,000
        lRules = ["SlowHashesPhase1", "Best126", "SlowHashesPhase2"]
        for lRule in lRules:
            do_run_jtr_prayer_mode(pHashFile=pHashFile, pDictionary="passwords/worst-50000-passwords.txt",
                                   pRule=lRule, pHashFormat=pHashFormat,
                                   pPassThrough=pPassThrough, pVerbose=pVerbose,
                                   pDebug=pDebug, pNumberHashes=pNumberHashes)

        # Dictionaries have 50,000 - 180,000 words
        # Rules have up to about 1,000 mangles
        # Factor: 180,000,000
        lFolder = "dictionaries"
        lDictionaries = ["persons-names.txt","other-base-words.txt","places.txt"]
        lRules = ["SlowHashesPhase1", "Best126", "SlowHashesPhase2"]

    elif pMethod == 7:
        # Dictionaries have less than 10,000 words
        # Rules have up to about 50,000 mangles
        # Factor: <500,000,000
        lFolder = "dictionaries"
        lDictionaries = ["calendar.txt", "short-list.txt", "brands.txt","movie-characters.txt",
                         "animals.txt","astrology.txt","songs.txt"]
        lRules = ["OneRuleToRuleThemAll"]

    elif pMethod == 8:
        # Dictionaries have about 10,000 words
        # Rules have up to about 50,000 mangles
        # Factor: 500,000,000
        lFolder = "dictionaries"
        lDictionaries = ["sports-related-words.txt","bible.txt","top-10000-english-words.txt",
                         "top-10000-spanish-words.txt","top-10000-german-words.txt"]
        lRules = ["OneRuleToRuleThemAll"]

    elif pMethod == 9:
        # Dictionaries have ~150,000 words
        # Rules have up to about 6,500 mangles
        # Factor: 975,000,000
        lFolder = "dictionaries"
        lDictionaries = ["persons-names.txt","other-base-words.txt","places.txt"]
        lRules = ["SlowHashesPhase3"]

    elif pMethod == 10:
        # Dictionaries have up to ~2,000,000 words
        # Rules have up to about 1,000 mangles
        # Factor: 2,000,000,000
        lFolder = "dictionaries"
        lDictionaries = ["all-english-words.txt","all-spanish-words.txt",
                         "all-french-words.txt","all-german-words.txt"]
        lRules = ["SlowHashesPhase1", "Best126", "SlowHashesPhase2"]

    elif pMethod == 11:
        # Dictionaries have ~150,000 words
        # Rules have up to about 50,000 mangles
        # Factor: 7,500,000,000
        lFolder = "dictionaries"
        lDictionaries = ["persons-names.txt","other-base-words.txt","places.txt"]
        lRules = ["OneRuleToRuleThemAll"]

    elif pMethod == 12:
        # Dictionaries have up to ~2,000,000 words
        # Rules have up to about 6,500 mangles
        # Factor: 13,000,000,000
        lFolder = "dictionaries"
        lDictionaries = ["all-english-words.txt","all-spanish-words.txt",
                         "all-french-words.txt","all-german-words.txt"]
        lRules = ["SlowHashesPhase3"]

    elif pMethod == 13:
        # Dictionaries have up to ~2,000,000 words
        # Rules have up to about 50,000 mangles
        # Factor: 100,000,000,000
        lFolder = "dictionaries"
        lDictionaries = ["all-english-words.txt","all-spanish-words.txt",
                         "all-french-words.txt","all-german-words.txt"]
        lRules = ["OneRuleToRuleThemAll"]

    # Run the wordlist and rule
    for lDictionary in lDictionaries:
        for lRule in lRules:
            do_run_jtr_prayer_mode(pHashFile=pHashFile, pDictionary=lFolder + "/" + lDictionary,
                                   pRule=lRule, pHashFormat=pHashFormat,
                                   pPassThrough=pPassThrough, pVerbose=pVerbose,
                                   pDebug=pDebug, pNumberHashes=pNumberHashes)


def do_run_jtr_prayer_mode(pHashFile: str, pDictionary: str, pRule: str,
                           pHashFormat: str, pPassThrough: str,
                           pVerbose: bool, pDebug: bool, pNumberHashes: int) -> None:

    # Note: subprocess.run() accepts the command to run as a list of arguments.
    # lCmdArgs is this list.

    lStartTime = time.time()

    if pDebug: rm_jtr_pot_file()

    lCmdArgs = [JTR_EXE_FILE_PATH]
    if pHashFormat: lCmdArgs.append("--format={}".format(pHashFormat))
    if pDictionary: lCmdArgs.append("--wordlist={}".format(pDictionary))
    if pRule: lCmdArgs.append("--rules={}".format(pRule))
    if pPassThrough: lCmdArgs.append(pPassThrough)

    if pVerbose:
        print("[*] Starting mode: Wordlist {}".format(pDictionary), end="")
        if pRule: print(" with Rule {}".format(pRule))

    # Determine number of passwords cracked before trying this method
    lNumberPasswordsAlreadyCracked = count_passwords_in_jtr_pot_file()

    if pVerbose:
        print("[*] Passwords cracked at start of prayer mode: {}".format(lNumberPasswordsAlreadyCracked))

    lCmdArgs.append(pHashFile)
    lCompletedProcess = subprocess.run(lCmdArgs, stdout=subprocess.PIPE)
    time.sleep(0.5)

    # Determine number of passwords cracked after trying this method
    lNumberPasswordsCracked = count_passwords_in_jtr_pot_file()

    lNumberPasswordsCrackedByThisMethod = lNumberPasswordsCracked - lNumberPasswordsAlreadyCracked
    lPercentPasswordsCracked = round(lNumberPasswordsCrackedByThisMethod / pNumberHashes * 100, 2)

    if pVerbose:
        print("[*] Finished prayer mode: Wordlist {}".format(pDictionary), end="")
        if pRule:
            print(" with Rule {}".format(pRule))
        else:
            print()
        print("\tCommand was: {}".format(lCompletedProcess.args))
        print("\tPasswords cracked at end of run: {}".format(lNumberPasswordsCracked))

    print("\tPasswords cracked by mode: {} ({} percent)".format(lNumberPasswordsCrackedByThisMethod, lPercentPasswordsCracked))

    if pDebug:
        lRunTime = time.time() - lStartTime
        lPasswordsCrackedPerSecond = lNumberPasswordsCrackedByThisMethod // lRunTime
        print("\tDuration: {}".format(lRunTime))
        print("\tPasswords cracked per second: {}".format(lPasswordsCrackedPerSecond))


def do_run_jtr_single_mode(pHashFile: str, pHashFormat: str, pPassThrough: str,
                           pVerbose: bool, pDebug: bool, pNumberHashes: int) -> None:

    # Note: subprocess.run() accepts the command to run as a list of arguments.
    # lCmdArgs is this list.

    lStartTime = time.time()

    if pDebug: rm_jtr_pot_file()

    lCmdArgs = [JTR_EXE_FILE_PATH]
    lCmdArgs.append("--single")
    if pHashFormat: lCmdArgs.append("--format={}".format(pHashFormat))
    if pPassThrough: lCmdArgs.append(pPassThrough)

    if pVerbose:
        print("[*] Starting mode: JTR Single Crack")

    # Determine number of passwords cracked before trying this method
    lNumberPasswordsAlreadyCracked = count_passwords_in_jtr_pot_file()

    if pVerbose:
        print("[*] Passwords cracked at start of single crack mode: {}".format(lNumberPasswordsAlreadyCracked))

    lCmdArgs.append(pHashFile)
    lCompletedProcess = subprocess.run(lCmdArgs, stdout=subprocess.PIPE)
    time.sleep(0.5)

    # Determine number of passwords cracked after trying this method
    lNumberPasswordsCracked = count_passwords_in_jtr_pot_file()

    lNumberPasswordsCrackedByThisMethod = lNumberPasswordsCracked - lNumberPasswordsAlreadyCracked
    lPercentPasswordsCracked = round(lNumberPasswordsCrackedByThisMethod / pNumberHashes * 100, 2)

    if pVerbose:
        print("[*] Finished single crack mode")
        print("\tCommand was: {}".format(lCompletedProcess.args))
        print("\tPasswords cracked at end of run: {}".format(lNumberPasswordsCracked))

    print("\tPasswords cracked by mode: {} ({} percent)".format(lNumberPasswordsCrackedByThisMethod, lPercentPasswordsCracked))

    if pDebug:
        lRunTime = time.time() - lStartTime
        lPasswordsCrackedPerSecond = lNumberPasswordsCrackedByThisMethod // lRunTime
        print("\tDuration: {}".format(lRunTime))
        print("\tPasswords cracked per second: {}".format(lPasswordsCrackedPerSecond))


if __name__ == '__main__':

    READ_BYTES = 'rb'
    READ_LINES = 'r'
    JTR_POT_FILE_PATH = Config.JTR_POT_FILE_PATH
    JTR_EXE_FILE_PATH = Config.JTR_EXECUTABLE_FILE_PATH
    DEBUG = Config.DEBUG
    MAX_CHARS_TO_BRUTEFORCE = Config.MAX_CHARS_TO_BRUTEFORCE

    lArgParser = argparse.ArgumentParser(description="""
  ___          ___
 | _ )_  _ ___| _ \__ _ ______
 | _ \ || / -_)  _/ _` (_-<_-<
 |___/\_, \___|_| \__,_/__/__/
      |__/
 
 Automated password hash analysis
""", formatter_class=RawTextHelpFormatter)
    lArgParser.add_argument('-f', '--hash-format',
                            type=str,
                            help="The hash algorithm used to hash the password(s). This value must be one of the values supported by John the Ripper. To see formats supported by JTR, use command \"john --list=formats\". It is strongly recommended to provide an optimal value. If no value is provided, John the Ripper will guess.\n\n",
                            action='store')
    lArgParser.add_argument('-w', '--basewords',
                            type=str,
                            help="Supply a comma-separated list of lowercase, unmangled base words thought to be good candidates. For example, if Wiley Coyote is cracking hashes from Acme Inc., Wiley might provide the word \"acme\". Be careful how many words are supplied as Byepass will apply many mangling rules. Up to several should run reasonably fast.\n\n",
                            action='store')
    lArgParser.add_argument('-b', '--brute-force',
                            type=str,
                            help="Bruce force common patterns with at least MIN characters up to MAX characters. Provide minimum and maxiumum number of characters as comma-separated, positive integers (i.e. 4,6 means 4 characters to 6 characters).\n\n",
                            action='store')
    lArgParser.add_argument('-t', '--techniques',
                            type=str,
                            help="Comma-separated list of integers between 0-13 that determines what password cracking techniques are attempted. Default is level 1. Example of running levels 1 and 2 --techniques=1,2\n\n0: Skip prayer mode entirely\n1: Small Dictionaries. Small Rulesets\n2: Medium Dictionaries. Small Rulesets\n3: Small Dictionaries. Medium Rulesets\n4: Medium Dictionaries. Medium Rulesets\n5: Large Password List. Custom Ruleset\n6: Medium-Large Dictionaries. Small Rulesets\n7: Small Dictionaries. Large Rulesets\n8: Medium Dictionaries. Large Rulesets\n9: Medium-Large Dictionaries. Medium Rulesets\n10: Large Dictionaries. Small Rulesets\n11: Medium-Large Dictionaries. Large Rulesets\n12: Large Dictionaries. Medium Rulesets\n13: Large Dictionaries. Large Rulesets\n\n",
                            action='store')
    lArgParser.add_argument('-s', '--stat-crack',
                            help="Enable statistical cracking. Byepass will run relatively fast cracking strategies in hopes of cracking enough passwords to induce a pattern and create \"high probability\" masks. Byepass will use the masks in an attempt to crack more passwords.\n\n",
                            action='store_true')
    lArgParser.add_argument('-p', '--percentile',
                            type=float,
                            help="Based on statistical analysis of the passwords cracked during initial phase, use only the masks statistically likely to be needed to crack at least the given percent of passwords. For example, if a value of 0.25 provided, only use the relatively few masks needed to crack 25 passwords of the passwords. Note that password cracking effort follows an exponential distribution, so cracking a few more passwords takes a lot more effort (relatively speaking). A good starting value if completely unsure is 25 percent (0.25).\n\n",
                            action='store')
    lArgParser.add_argument('-j', '--pass-through',
                             type=str,
                             help="Pass-through the raw parameter to John the Ripper. Example: --pass-through=\"--fork=2\"\n\n",
                             action='store')
    lArgParser.add_argument('-v', '--verbose',
                            help='Enable verbose output such as current progress and duration',
                            action='store_true')
    lArgParser.add_argument('-d', '--debug',
                            help='Enable debug mode',
                            action='store_true')
    requiredAguments = lArgParser.add_mutually_exclusive_group(required=True)
    requiredAguments.add_argument('-e', '--examples',
                            help='Show example usage',
                            action='store_true')
    requiredAguments.add_argument('-i', '--input-file',
                                  type=str,
                                  help='Path to file containing password hashes to attempt to crack',
                                  action='store')
    lArgs = lArgParser.parse_args()

    if lArgs.examples:
        print_example_usage()
        exit(0)

    # Input parameter validation
    if lArgs.percentile and not lArgs.stat_crack:
        print("[*] WARNING: Argument 'percentile' provided without argument 'stat_crack'. Percentile will be ignored")

    # Parse and validate input parameters
    lHashFile = lArgs.input_file
    lVerbose = lArgs.verbose
    lDebug = parse_arg_debug(lArgs.debug)
    lHashFormat = parse_arg_hash_format(lArgs.hash_format)
    lTechniques = parse_arg_techniques(lArgs.techniques)

    lNumberHashes = count_hashes_in_input_file(pHashFile=lHashFile)
    lNumberPasswordsPOTFileAtStart = count_passwords_in_jtr_pot_file()

    if lVerbose:
        lStartTime = time.time()
        print("[*] Working on input file {} ({} lines)".format(lHashFile, lNumberHashes))

    # Hopefully user has some knowledge of system to give good base words
    if lArgs.basewords:
        run_jtr_baseword_mode(pHashFile=lHashFile, pBaseWords=lArgs.basewords, pHashFormat=lHashFormat,
                              pVerbose=lVerbose, pDebug=lDebug, pPassThrough=lArgs.pass_through,
                              pNumberHashes=lNumberHashes)
    # Smart brute-force
    if lArgs.brute_force:
        lMinCharactersToBruteForce, lMaxCharactersToBruteForce = parse_arg_brute_force(lArgs.brute_force)
        run_jtr_brute_force_mode(pHashFile=lHashFile, pMinCharactersToBruteForce=lMinCharactersToBruteForce,
                                 pMaxCharactersToBruteForce=lMaxCharactersToBruteForce,
                                 pHashFormat=lHashFormat, pVerbose=lVerbose,
                                 pDebug=lDebug, pPassThrough=lArgs.pass_through,
                                 pNumberHashes=lNumberHashes)

    # Try to crack some passwords as quickly as possible to use in statistical analysis
    # If no technique is given, default is 1. If 0 is given, this mode is skipped
    if 0 not in lTechniques:
        for i in lTechniques:
            run_jtr_prayer_mode(pHashFile=lHashFile, pMethod=i, pHashFormat=lHashFormat,
                                pVerbose=lVerbose, pDebug=lDebug, pPassThrough=lArgs.pass_through,
                                pNumberHashes=lNumberHashes)

    # If the user chooses -s option, begin statistical analysis to aid targeted cracking routines
    if lArgs.stat_crack:

        lPercentile = parse_arg_percentile(lArgs.percentile)
        perform_statistical_cracking(pHashFile=lHashFile, pPercentile=lPercentile, pHashFormat=lHashFormat,
                                     pVerbose=lVerbose, pDebug=lDebug, pPassThrough=lArgs.pass_through,
                                     pNumberHashes=lNumberHashes)

    if lVerbose:
        lEndTime = time.time()
        print_closing_message(pNumberHashes=lNumberHashes,
                              pNumberPasswordsPOTFileAtStart=lNumberPasswordsPOTFileAtStart,
                              pStartTime=lStartTime, pEndTime=lEndTime)