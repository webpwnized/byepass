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

import config as Config
import argparse, subprocess
from argparse import RawTextHelpFormatter
from pwstats import PasswordStats
import os.path
import time
import re


def parse_jtr_show(pVerbose: bool, pDebug: bool) -> None:

    lCompletedProcess = subprocess.run([JTR_EXE_FILE_PATH, "--show", "--format=descrypt", lHashFile], stdout=subprocess.PIPE)
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

    for lLine in lPotFile:
        if not lLine[0:3] == b'$LM':
            lPassword = lLine.strip().split(b':')[1]
            if not lPassword in lListOfPasswords:
                lListOfPasswords.append(lPassword)

    return lListOfPasswords


def rm_jtr_pot_file() -> None:

    if os.path.exists(JTR_POT_FILE_PATH):
        lCompletedProcess = subprocess.run(["rm", JTR_POT_FILE_PATH], stdout=subprocess.PIPE)
        print("[*] Deleted file {}".format(JTR_POT_FILE_PATH))
        time.sleep(1)


def run_jtr_wordlist_mode(pWordlist: str, pRule: str, pHashFormat:str,  pVerbose: bool, pDebug: bool) -> None:

    lStartTime = time.time()

    if pDebug: rm_jtr_pot_file()

    lCmdArgs = [JTR_EXE_FILE_PATH]
    if pHashFormat: lCmdArgs.append("--format={}".format(pHashFormat))
    lCmdArgs.append("--wordlist={}".format(pWordlist))
    if pRule: lCmdArgs.append("--rule={}".format(pRule))
    lCmdArgs.append(lHashFile)

    if pVerbose:
        print("[*] Starting wordlist mode: {}".format(pWordlist))
        if pRule: print("[*] Using rule: {}".format(pRule))

    # Determine number of passwords cracked before trying this method
    try:
        lListOfPasswords = parse_jtr_pot(pVerbose=pVerbose, pDebug=pDebug)
        lNumberPasswordsAlreadyCracked = lListOfPasswords.__len__()
    except:
        lNumberPasswordsAlreadyCracked = 0

    if pVerbose:
        print("[*] Finished")
        print("[*] Passwords cracked before using wordlist {}: {}".format(pWordlist, lNumberPasswordsAlreadyCracked))

    lCompletedProcess = subprocess.run(lCmdArgs, stdout=subprocess.PIPE)
    time.sleep(1)

    # Determine number of passwords cracked after trying this method
    try:
        lListOfPasswords = parse_jtr_pot(pVerbose=pVerbose, pDebug=pDebug)
        lNumberPasswordsCracked = lListOfPasswords.__len__()
    except:
        lNumberPasswordsCracked = 0

    lNumberPasswordsCrackedByThisMethod = lNumberPasswordsCracked - lNumberPasswordsAlreadyCracked
    print("[*] Passwords cracked using wordlist {}: {}".format(pWordlist, lNumberPasswordsCrackedByThisMethod))

    if pVerbose:
        print("[*] Command: {}".format(lCompletedProcess.args))
        #print(lCompletedProcess.stdout)
        print("[*] Finished")
        print("[*] Passwords cracked: {}".format(lNumberPasswordsCrackedByThisMethod))

    if pDebug:
        lRunTime = time.time() - lStartTime
        print("[*] Duration: {}".format(lRunTime))
        print("[*] Passwords cracked per second: {}".format(lNumberPasswordsCrackedByThisMethod // lRunTime))


def run_jtr_mask_mode(pMask: str, pWordlist: str, pHashFormat:str, pVerbose: bool, pDebug: bool) -> None:

    lStartTime = time.time()

    if pDebug: rm_jtr_pot_file()

    lCmdArgs = [JTR_EXE_FILE_PATH]
    if pHashFormat: lCmdArgs.append("--format={}".format(pHashFormat))
    lCmdArgs.append(pMask)
    if pWordlist: lCmdArgs.append("--wordlist={}".format(pWordlist))
    lCmdArgs.append(lHashFile)

    if pVerbose:
        print("[*] Starting mask mode: {}".format(pMask))
        if pWordlist: print("[*] Using wordlist: {}".format(pWordlist))

    # Determine number of passwords cracked before trying this method
    try:
        lListOfPasswords = parse_jtr_pot(pVerbose=pVerbose, pDebug=pDebug)
        lNumberPasswordsAlreadyCracked = lListOfPasswords.__len__()
    except:
        lNumberPasswordsAlreadyCracked = 0

    if pVerbose:
        print("[*] Finished")
        print("[*] Passwords cracked before using mask {}: {}".format(pMask, lNumberPasswordsAlreadyCracked))

    lCompletedProcess = subprocess.run(lCmdArgs, stdout=subprocess.PIPE)
    time.sleep(1)

    # Determine number of passwords cracked after trying this method
    try:
        lListOfPasswords = parse_jtr_pot(pVerbose=pVerbose, pDebug=pDebug)
        lNumberPasswordsCracked = lListOfPasswords.__len__()
    except:
        lNumberPasswordsCracked = 0

    lNumberPasswordsCrackedByThisMethod = lNumberPasswordsCracked - lNumberPasswordsAlreadyCracked
    print("[*] Passwords cracked using mask {}: {}".format(pMask, lNumberPasswordsCrackedByThisMethod))

    if pVerbose:
        print("[*] Command: {}".format(lCompletedProcess.args))
        #print(lCompletedProcess.stdout)
        print("[*] Finished")
        print("[*] Passwords cracked: {}".format(lNumberPasswordsCrackedByThisMethod))

    if pDebug:
        lRunTime = time.time() - lStartTime
        print("[*] Duration: {}".format(lRunTime))
        print("[*] Passwords cracked per second: {}".format(lNumberPasswordsCrackedByThisMethod // lRunTime))


def run_jtr_baseword_mode(pBaseWords: str, pHashFormat: str, pVerbose: bool, pDebug: bool) -> None:

    if pVerbose: print("[*] Starting mode: Baseword with words {}", pBaseWords)

    lBaseWords = list(pBaseWords.split(","))
    lBaseWordsFileName = 'basewords/basewords.txt'
    lBaseWordsFile = open(lBaseWordsFileName, 'w')
    for lWord in lBaseWords:
        lBaseWordsFile.write("%s\n" % lWord)
    lBaseWordsFile.flush()
    lBaseWordsFile.close()
    run_jtr_wordlist_mode(pWordlist="basewords/basewords.txt", pRule="All", pHashFormat=pHashFormat,
                          pVerbose=pVerbose, pDebug=pDebug)
    os.remove(lBaseWordsFileName)

    if pVerbose: print("[*] Finished Baseword Mode")


def run_jtr_prayer_mode(pMethod: int, pHashFormat: str, pVerbose: bool, pDebug: bool) -> None:
    # Note: subprocess.run() accepts the command to run as a list of arguments.
    # lCmdArgs is this list.

    lStartTime = time.time()

    if pDebug: rm_jtr_pot_file()

    lCmdArgs = [JTR_EXE_FILE_PATH]
    if pHashFormat: lCmdArgs.append("--format={}".format(pHashFormat))

    if pMethod == 1:
        if pVerbose: print("[*] Starting mode: Wordlist hob0-short-crack.txt Rule best126")
        lCmdArgs.append("--wordlist=dictionaries/hob0-short-crack.txt")
        lCmdArgs.append("--rules=best126")
    elif pMethod == 2:
        if pVerbose: print("[*] Starting mode: Wordlist worst-95000-passwords.txt Rule best126")
        lCmdArgs.append("--wordlist=passwords/worst-95000-passwords.txt")
        lCmdArgs.append("--rules=best126")
    elif pMethod == 3:
        if pVerbose: print("[*] Starting mode: Wordlist passwords-hailmary.txt")
        lCmdArgs.append("--wordlist=passwords/passwords-hailmary.txt")
        lCmdArgs.append("--rules=HailMary")
    elif pMethod == 4:
        if pVerbose: print("[*] Starting mode: Wordlist top-10000-english-words.txt Rule best126")
        lCmdArgs.append("--wordlist=dictionaries/top-10000-english-words.txt")
        lCmdArgs.append("--rules=best126")
    elif pMethod == 5:
        if pVerbose: print("[*] Starting mode: Wordlist top-10000-spanish-words.txt Rule best126")
        lCmdArgs.append("--wordlist=dictionaries/top-10000-spanish-words.txt")
        lCmdArgs.append("--rules=best126")
    elif pMethod == 6:
        if pVerbose: print("[*] Starting mode: Wordlist persons-names.txt Rule best126")
        lCmdArgs.append("--wordlist=dictionaries/persons-names.txt")
        lCmdArgs.append("--rules=best126")
    elif pMethod == 7:
        if pVerbose: print("[*] Starting mode: Wordlist sports-related-words.txt Rule best126")
        lCmdArgs.append("--wordlist=dictionaries/sports-related-words.txt")
        lCmdArgs.append("--rules=best126")
    elif pMethod == 8:
        if pVerbose: print("[*] Starting mode: Wordlist other-base-words.txt Rule best126")
        lCmdArgs.append("--wordlist=dictionaries/other-base-words.txt")
        lCmdArgs.append("--rules=best126")
    elif pMethod == 9:
        if pVerbose: print("[*] Starting mode: Wordlist places.txt Rule best126")
        lCmdArgs.append("--wordlist=dictionaries/places.txt")
        lCmdArgs.append("--rules=best126")
    elif pMethod == 10:
        if pVerbose: print("[*] Starting mode: Wordlist 4-digit-numbers.txt Rule best126")
        lCmdArgs.append("--wordlist=dictionaries/4-digit-numbers.txt")
        lCmdArgs.append("--rules=best126")
    elif pMethod == 11:
        if pVerbose: print("[*] Starting mode: Wordlist calendar.txt Rule BPAppendYears")
        lCmdArgs.append("--wordlist=dictionaries/calendar.txt")
        lCmdArgs.append("--rules=bpappendyears")
    elif pMethod == 12:
        if pVerbose: print("[*] Starting mode: Wordlist 6-digit-numbers.txt")
        lCmdArgs.append("--wordlist=dictionaries/6-digit-numbers.txt")
        lCmdArgs.append("--rules=best126")
    elif pMethod == 13:
        if pVerbose: print("[*] Starting mode: Wordlist keyboard-patterns.txt")
        lCmdArgs.append("--wordlist=dictionaries/keyboard-patterns.txt")
    elif pMethod == 14:
        if pVerbose: print("[*] Starting mode: JTR single crack")
        lCmdArgs.append("--single")

    # Determine number of passwords cracked before trying this method
    try:
        lListOfPasswords = parse_jtr_pot(pVerbose=pVerbose, pDebug=pDebug)
        lNumberPasswordsAlreadyCracked = lListOfPasswords.__len__()
    except:
        lNumberPasswordsAlreadyCracked = 0

    if pVerbose:
        print("[*] Finished")
        print("[*] Passwords cracked at start of prayer mode {}: {}".format(pMethod, lNumberPasswordsAlreadyCracked))

    lCmdArgs.append(lHashFile)
    lCompletedProcess = subprocess.run(lCmdArgs, stdout=subprocess.PIPE)
    time.sleep(0.5)

    # Determine number of passwords cracked after trying this method
    try:
        lListOfPasswords = parse_jtr_pot(pVerbose=pVerbose, pDebug=pDebug)
        lNumberPasswordsCracked = lListOfPasswords.__len__()
    except:
        lNumberPasswordsCracked = 0

    if pVerbose:
        print("[*] Command: {}".format(lCompletedProcess.args))
        #print(lCompletedProcess.stdout)
        print("[*] Finished")
        print("[*] Passwords cracked at end of prayer mode {}: {}".format(pMethod, lNumberPasswordsCracked))

    lNumberPasswordsCrackedByThisMethod = lNumberPasswordsCracked - lNumberPasswordsAlreadyCracked
    print("[*] Passwords cracked by prayer mode {}: {}".format(pMethod, lNumberPasswordsCrackedByThisMethod))

    if pDebug:
        lRunTime = time.time() - lStartTime
        print("[*] Duration: {}".format(lRunTime))
        print("[*] Passwords cracked per second: {}".format(lNumberPasswordsCrackedByThisMethod // lRunTime))


def perform_statistical_cracking(pPercentile: float, pHashFormat: str, pVerbose: bool, pDebug: bool) -> None:

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

        # All lowercase letters
        if re.match('^(\?l)+$', lMask):
            lCountLetters = lMask.count('?l')
            lWordlist = "dictionaries/{}-character-english-words.txt".format(str(lCountLetters))
            run_jtr_wordlist_mode(pWordlist=lWordlist, pRule="best126", pHashFormat=pHashFormat,
                                  pVerbose=pVerbose, pDebug=pDebug)

        # All uppercase
        elif re.match('^(\?u)+$', lMask):
            lCountLetters = lMask.count('?u')
            lWordlist = "dictionaries/{}-character-english-words.txt".format(str(lCountLetters))
            lRule = "uppercase"
            run_jtr_wordlist_mode(pWordlist=lWordlist, pRule=lRule, pHashFormat=pHashFormat,
                                  pVerbose=pVerbose, pDebug=pDebug)

        # Uppercase followed by lowercase (assume only leading letter is uppercase)
        elif re.match('^(\?u)(\?l)+$', lMask):
            lCountLetters = lMask.count('?u') + lMask.count('?l')
            lWordlist = "dictionaries/{}-character-english-words.txt".format(str(lCountLetters))
            lRule = "capitalize"
            run_jtr_wordlist_mode(pWordlist=lWordlist, pRule=lRule, pHashFormat=pHashFormat,
                                  pVerbose=pVerbose, pDebug=pDebug)

        # Lowercase ending with digits
        elif re.match('^(\?l)+(\?d)+$', lMask):
            lCountLetters = lMask.count('?l')
            lCountDigits = lMask.count('?d')
            lWordlist = "dictionaries/{}-character-english-words.txt".format(str(lCountLetters))
            lRule = "append{}digits".format(str(lCountDigits))
            run_jtr_wordlist_mode(pWordlist=lWordlist, pRule=lRule, pHashFormat=pHashFormat,
                                  pVerbose=pVerbose, pDebug=pDebug)

        # Uppercase followed by digits
        elif re.match('^(\?u)+(\?d)+$', lMask):
            lCountLetters = lMask.count('?u')
            lCountDigits = lMask.count('?d')
            lWordlist = "dictionaries/{}-character-english-words.txt".format(str(lCountLetters))
            lRule = "uppercaseappend{}digits".format(str(lCountDigits))
            run_jtr_wordlist_mode(pWordlist=lWordlist, pRule=lRule, pHashFormat=pHashFormat,
                                  pVerbose=pVerbose, pDebug=pDebug)

        # Uppercase, lowercase, then digits (assume only leading letter is uppercase)
        elif re.match('^(\?u)(\?l)+(\?d)+$', lMask):
            lCountLetters = lMask.count('?u') + lMask.count('?l')
            lCountDigits = lMask.count('?d')
            lWordlist = "dictionaries/{}-character-english-words.txt".format(str(lCountLetters))
            lRule = "capitalizeappend{}digits".format(str(lCountDigits))
            run_jtr_wordlist_mode(pWordlist=lWordlist, pRule=lRule, pHashFormat=pHashFormat,
                                  pVerbose=pVerbose, pDebug=pDebug)

        # Low number of digits. We do not cover large numbers of digits because
        # precomputing dictionary files would be huge and running mask mode takes a long time.
        # Right now we support 4-6 digits only. Recall we cover 4 and 6 digits specifically in
        # "prayer" mode so we do not repeat those two masks here.
        elif re.match('^(\?d)+$', lMask):
            lCountDigits = lMask.count('?d')
            if lCountDigits == 5:
                lWordlist = "dictionaries/{}-digit-numbers.txt".format(str(lCountDigits))
                run_jtr_wordlist_mode(pWordlist=lWordlist, pRule="", pHashFormat=pHashFormat,
                                      pVerbose=pVerbose, pDebug=pDebug)
            else:
                print("[*] WARNING: Did not process mask {} because it is out of policy".format(lMask))

        # Lowercase ending with something other than the masks already accounted for. If the
        # ending pattern is longer than 2 characters, we do not try because it takes a long time
        # to test that many hashes
        elif re.match('^(\?l)+', lMask):
            lPrefix = re.search('^(\?l)+', lMask).group()
            lCountLetters = lPrefix.count("?l")
            lSuffix = lMask[lCountLetters * 2:]
            if len(lSuffix) <= 4:
                lWordlist = "dictionaries/{}-character-english-words.txt".format(str(lCountLetters))
                lMaskParam = "--mask=?w{}".format(lSuffix)
                run_jtr_mask_mode(pMask=lMaskParam, pWordlist=lWordlist, pHashFormat=pHashFormat,
                                  pVerbose=pVerbose, pDebug=pDebug)
            else:
                print("[*] WARNING: Did not process mask {} because it is out of policy".format(lMask))

        else:
            lUndefinedMasks.append(lMask)
            print("[*] WARNING: No policy defined for mask {}".format(lMask))

    # List masks that did not match a pattern so that a pattern can be added
    if lUndefinedMasks: print(
        "[*] WARNING: There was no policy defined for the following masks: {}".format(lUndefinedMasks))


if __name__ == '__main__':

    READ_BYTES = 'rb'
    READ_LINES = 'r'
    JTR_POT_FILE_PATH = Config.JTR_POT_FILE_PATH
    JTR_EXE_FILE_PATH = Config.JTR_EXECUTABLE_FILE_PATH
    DEBUG = Config.DEBUG

    lArgParser = argparse.ArgumentParser(description='ByePass: Automate the most common password cracking tasks',
                                         epilog="""
Examples:\n\n
Attempt to crack password hashes found in input file "password.hashes"\n\n
\tpython3 byepass.py -v --hash-format=descrypt --input-file=password.hashes\n\n
Attempt to crack password hashes found in input file "password.hashes", then run statistical analysis to determine masks needed to crack 50 percent of passwords, and try to crack again using the masks.\n\n
\tpython3 byepass.py --verbose --hash-format=descrypt --stat-crack --percentile=0.50 --input-file=password.hashes\n\n
\"Real life\" example attempting to crack 25 percent of the linked-in hash set\n\n
\tpython3 byepass.py --verbose --hash-format=Raw-SHA1 --stat-crack --percentile=0.25 --input-file=linkedin.hashes\n\n
Attempt to crack linked-in hashes using base words linkedin and linked\n\n
\tpython3 byepass.py --hash-format=Raw-SHA1 --base-words=linkedin,linked --input-file=linkedin-1.hashes
                                         """,
                                         formatter_class=RawTextHelpFormatter)
    lArgParser.add_argument('-f', '--hash-format',
                            type=str,
                            help="The hash algorithm used to hash the password(s). This value must be one of the values supported by John the Ripper. To see formats supported by JTR, use command \"john --list=formats\". It is strongly recommended to provide an optimal value. If no value is provided, John the Ripper will guess.",
                            action='store')
    lArgParser.add_argument('-s', '--stat-crack',
                            help="Enable statistical cracking. Byepass will run relatively fast cracking strategies in hopes of cracking enough passwords to induce a pattern and create \"high probability\" masks. Byepass will use the masks in an attempt to crack more passwords.",
                            action='store_true')
    lArgParser.add_argument('-b', '--basewords',
                            type=str,
                            help="Supply a comma-separated list of lowercase, unmangled base words thought to be good candidates. For example, if Wiley Coyote is cracking hashes from Acme Inc., Wiley might provide the word \"acme\". Be careful how many words are supplied as Byepass will apply many mangling rules. Up to several dozen should run reasonably fast.",
                            action='store')
    lArgParser.add_argument('-p', '--percentile',
                            type=float,
                            help="Based on statistical analysis of the passwords cracked during initial phase, use only the masks statistically likely to be needed to crack at least the given percent of passwords. For example, if a value of 0.25 provided, only use the relatively few masks needed to crack 25 passwords of the passwords. Note that password cracking effort follows an exponential distribution, so cracking a few more passwords takes a lot more effort (relatively speaking). A good starting value if completely unsure is 25 percent (0.25).",
                            action='store')
    lArgParser.add_argument('-v', '--verbose',
                            help='Enable verbose output such as current progress and duration',
                            action='store_true')
    lArgParser.add_argument('-d', '--debug',
                            help='Enable debug mode',
                            action='store_true')
    requiredAguments = lArgParser.add_argument_group('required arguments')
    requiredAguments.add_argument('-i', '--input-file',
                                  type=str,
                                  help='Path to file containing password hashes to attempt to crack',
                                  action='store',required=True)
    lArgs = lArgParser.parse_args()

    # Input parameter validation
    if lArgs.percentile and not lArgs.stat_crack:
        print("[*] WARNING: Argument 'percentile' provided without argument 'stat_crack'. Percentile will be ignored")

    lHashFile = lArgs.input_file
    lVerbose = lArgs.verbose

    if lArgs.debug:
        lDebug = lArgs.debug
    else:
        lDebug = DEBUG

    try:
        lHashFormat = lArgs.hash_format
    except:
        lHashFormat = ""

    if lVerbose:
        lStartTime = time.time()
        print("[*] Working on input file {}".format(lHashFile))

    if lArgs.basewords:
        run_jtr_baseword_mode(pBaseWords=lArgs.basewords, pHashFormat=lHashFormat,
                              pVerbose=lVerbose, pDebug=lDebug)

    # Try to crack a relatively few passwords as quickly as possible.
    # These can be used in statistical analysis
    for i in range(1,15,1):
        run_jtr_prayer_mode(pMethod=i, pHashFormat=lHashFormat, pVerbose=lVerbose, pDebug=lDebug)

    # If the user chooses, begin statistical analysis to aid targeted cracking routines
    if lArgs.stat_crack:

        if lArgs.percentile:
            if not 0.0 <= lArgs.percentile <= 1.00:
                raise ValueError('The percentile provided must be between 0.0 and 1.0.')
            lPercentile = lArgs.percentile
        else:
            lPercentile = 1.0

        perform_statistical_cracking(pPercentile=lPercentile, pHashFormat=lHashFormat,
                                     pVerbose=lVerbose, pDebug=lDebug)

    if lVerbose:
        lEndTime = time.time()
        lElaspsedTime = time.gmtime(lEndTime - lStartTime)
        print("[*] Duration: {}".format(time.strftime("%H:%M:%S", lElaspsedTime)))
        print("[*] Cracking attempt complete. Use john --show to see cracked passwords.")
        print("[*] The command should be something like {}{}{} --show {}".format(JTR_EXE_FILE_PATH, " --format=" if lHashFormat else "", lHashFormat, lHashFile))
        print("[*] Keep cracking with incremental mode")
        print("[*] The command should be something like {}{}{} --incremental {}".format(JTR_EXE_FILE_PATH, " --format=" if lHashFormat else "", lHashFormat, lHashFile))