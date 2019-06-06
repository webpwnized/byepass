# JTR Mask Mode: https://github.com/magnumripper/JohnTheRipper/blob/bleeding-jumbo/doc/MASK

from argparse import RawTextHelpFormatter
from pwstats import PasswordStats
from techniques import Techniques
from watcher import Watcher
from reporter import Reporter
from jtr import JohnTheRipper
import config as Config
import subprocess
import os.path
import time
import re
import argparse

# GLOBALS
gMasksAlreadyBruteForced = []
gReporter = Reporter()

#METHODS
def print_example_usage():
    print("""
Attempt to crack hashes using JTR Single Crack Mode\n
\tpython3 byepass.py --verbose --hash-format=Raw-SHA1 --jtr-single-crack --input-file=linkedin-1.hashes
\tpython3 byepass.py -v -f Raw-SHA1 -u -i linkedin-1.hashes\n
Attempt to crack linked-in hashes using base words linkedin and linked\n
\tpython3 byepass.py --verbose --hash-format=Raw-SHA1 --basewords=linkedin,linked --input-file=linkedin-1.hashes
\tpython3 byepass.py -v -f Raw-SHA1 -w linkedin,linked -i linkedin-1.hashes\n
Attempt to brute force words from 3 to 5 characters in length\n
\tpython3 byepass.py --verbose --hash-format=Raw-MD5 --brute-force=3,5 --input-file=hashes.txt
\tpython3 byepass.py -f Raw-MD5 -j="--fork=4" -v -b 3,5 -i hashes.txt\n
Attempt to crack password hashes found in input file "password.hashes" using default techniques\n
\tpython3 byepass.py --verbose --hash-format=descrypt --input-file=password.hashes
\tpython3 byepass.py -v -f descrypt -i password.hashes\n
Be more aggressive by using techniques level 4 in attempt to crack password hashes found in input file "password.hashes"\n
\tpython3 byepass.py --verbose --techniques=4 --hash-format=descrypt --input-file=password.hashes
\tpython3 byepass.py -v -t 4 -f descrypt -i password.hashes\n
Go bonkers and try all techniques. Start with technique level 1 and proceed to level 15 in attempt to crack password hashes found in input file "password.hashes"\n
\tpython3 byepass.py --verbose --techniques=1,2,3,4,5,6,7,8,9,10,11,12,13,14,15 --hash-format=descrypt --input-file=password.hashes
\tpython3 byepass.py -v -t 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15 -f descrypt -i password.hashes\n
Only try first two techniques. Start with technique level 1 and proceed to level 2 in attempt to crack password hashes found in input file "password.hashes"\n
\tpython3 byepass.py --verbose --techniques=1,2 --hash-format=descrypt --input-file=password.hashes
\tpython3 byepass.py -v -t 1,2 -f descrypt -i password.hashes\n
Attempt to crack password hashes found in input file "password.hashes", then run statistical analysis to determine masks needed to crack 50 percent of passwords, and try to crack again using the masks.\n
\tpython3 byepass.py --verbose --hash-format=descrypt --stat-crack --percentile=0.50 --input-file=password.hashes
\tpython3 byepass.py -v -f descrypt -s -p 0.50 -i password.hashes\n
\"Real life\" example attempting to crack 25 percent of the linked-in hash set\n
\tpython3 byepass.py --verbose --hash-format=Raw-SHA1 --stat-crack --percentile=0.25 --input-file=linkedin.hashes
\tpython3 byepass.py -v -f Raw-SHA1 -s -f 0.25 -i linkedin.hashes\n
Attempt to crack linked-in hashes using base words linkedin and linked\n
\tpython3 byepass.py --verbose --hash-format=Raw-SHA1 --basewords=linkedin,linked --input-file=linkedin-1.hashes
\tpython3 byepass.py -v -f -w linkedin,linked -i linkedin-1.hashes\n
Run statistical analysis to determine masks needed to crack 50 percent of passwords, and try to crack using the masks.\n
\tpython3 byepass.py -v --hash-format=descrypt --stat-crack --percentile=0.50 --input-file=password.hashes
\tpython3 byepass.py -v -f descrypt -s -p 0.50 -i password.hashes\n
Use recycle mode to try cracking remaining hashes using root words generated from already cracked passwords\n
\tpython3 byepass.py --verbose --hash-format=descrypt --recycle --input-file=password.hashes
\tpython3 byepass.py -v -f descrypt -r -i password.hashes\n
Use JTR prince mode with dictionary prince.txt\n
\tpython3 byepass.py --verbose --hash-format=descrypt --jtr-prince --input-file=password.hashes
\tpython3 byepass.py -v -f descrypt -c -i password.hashes\n
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


def parse_argTechniques(pArgTechniques: str) -> list:
    lTechniques = []

    if pArgTechniques is not None:

        lErrorMessage = 'Techniques must be supplied as a comma-separated list of integers between 0 and 15'

        try:
            lTechniques = list(map(int, pArgTechniques.split(",")))
        except:
            raise ValueError(lErrorMessage)

        lObservedTechniques = []
        for lTechnique in lTechniques:
            if 0 <= lTechnique <= 15:
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


def print_closing_message(pJTR: JohnTheRipper, pNumberHashes: int, pNumberPasswordsPOTFileAtStart: int,
                          pNumberPasswordsPOTFileAtEnd: int, pStartTime: float, pEndTime: float) -> None:

        lNumberPasswords = pNumberPasswordsPOTFileAtEnd - pNumberPasswordsPOTFileAtStart
        lElaspsedTime = time.gmtime(pEndTime - pStartTime)
        lDurationSeconds = pEndTime - pStartTime
        lNumberPasswordsCrackedPerSecond = lNumberPasswords // lDurationSeconds

        try:
            lPercent = round(lNumberPasswords / pNumberHashes * 100, 2)
        except:
            lPercent = 0

        print()
        print("[*] Techniques Attempted")
        gReporter.reportResults()
        print()
        print("[*] Duration: {}".format(time.strftime("%H:%M:%S", lElaspsedTime)))
        print("[*] Passwords cracked (estimated): {} out of {} ({}%)".format(lNumberPasswords, pNumberHashes, lPercent))
        print("[*] Passwords cracked per second (estimated): {}".format(lNumberPasswordsCrackedPerSecond))
        print()
        print("[*] Cracking attempt complete. Use john --show to see cracked passwords.")
        print("[*] The command should be something like {}{}{} --show {}".format(pJTR.jtr_executable_file_path, " --format=" if lHashFormat else "", lHashFormat, lHashFile))
        print()
        print("[*] Keep cracking with incremental mode")
        print("[*] The command should be something like {}{}{} --incremental {}".format(pJTR.jtr_executable_file_path, " --format=" if lHashFormat else "", lHashFormat, lHashFile))


def count_hashes_in_input_file(pHashFile: str) -> int:

        lLines = 0
        for lLine in open(pHashFile):
            lLines += 1
        return lLines


def do_run_jtr_mask_mode(pJTR: JohnTheRipper, pMask: str, pWordlist: str,
                      pVerbose: bool, pDebug: bool, pNumberHashes: int) -> None:

    # There are two modes that run brute force using masks. Keep track of masks
    # already checked in case the same mask would be tried twice.
    if pMask in gMasksAlreadyBruteForced:
        if pVerbose:
            print("[*] Mask {} has already been tested in this session. Moving on to next task.".format(pMask))
        return None
    else:
        gMasksAlreadyBruteForced.append(pMask)

    lCrackingMode = "Mask {}".format(pMask)
    if pWordlist: lCrackingMode += " using wordlist {}".format(pWordlist)

    lWatcher = Watcher(pCrackingMode=lCrackingMode, pNumberHashes=pNumberHashes, pVerbose=pVerbose,
                       pDebug=pDebug, pJTRPotFilePath=pJTR.jtr_pot_file_path)
    lWatcher.start_timer()
    lWatcher.print_mode_start_message()
    
    pJTR.run_mask_mode(pMask=pMask, pWordlist=pWordlist)

    lWatcher.stop_timer()
    lWatcher.print_mode_finsihed_message()

    gReporter.appendRecord(pMode=lCrackingMode, pMask=pMask, pWordlist=pWordlist, pRule="",
                           pNumberPasswordsCracked=lWatcher.number_passwords_cracked_by_this_mode,
                           pNumberPasswordsCrackedPerSecond=lWatcher.number_passwords_cracked_by_this_mode_per_second,
                           pPercentPasswordsCracked=lWatcher.percent_passwords_cracked_by_this_mode)


def run_jtr_wordlist_mode(pJTR: JohnTheRipper, pWordlist: str, pRule: str,
                          pVerbose: bool, pDebug: bool, pNumberHashes: int) -> None:

    lCrackingMode = "Wordlist {}".format(pWordlist)
    if pRule: lCrackingMode += " with rule {}".format(pRule)

    lWatcher = Watcher(pCrackingMode=lCrackingMode, pNumberHashes=pNumberHashes, pVerbose=pVerbose,
                       pDebug=pDebug, pJTRPotFilePath=pJTR.jtr_pot_file_path)
    lWatcher.start_timer()
    lWatcher.print_mode_start_message()

    pJTR.run_wordlist_mode(pWordlist=pWordlist, pRule=pRule)

    lWatcher.stop_timer()
    lWatcher.print_mode_finsihed_message()

    gReporter.appendRecord(pMode=lCrackingMode, pMask="", pWordlist=pWordlist, pRule=pRule,
                           pNumberPasswordsCracked=lWatcher.number_passwords_cracked_by_this_mode,
                           pNumberPasswordsCrackedPerSecond=lWatcher.number_passwords_cracked_by_this_mode_per_second,
                           pPercentPasswordsCracked=lWatcher.percent_passwords_cracked_by_this_mode)


def do_run_jtr_single_mode(pJTR: JohnTheRipper, pVerbose: bool, pDebug: bool, pNumberHashes: int) -> None:

    lCrackingMode = "John the Ripper (JTR) Single Crack"

    lWatcher = Watcher(pCrackingMode=lCrackingMode, pNumberHashes=pNumberHashes, pVerbose=pVerbose,
                       pDebug=pDebug, pJTRPotFilePath=pJTR.jtr_pot_file_path)
    lWatcher.start_timer()
    lWatcher.print_mode_start_message()

    pJTR.run_single_crack()

    lWatcher.stop_timer()
    lWatcher.print_mode_finsihed_message()

    gReporter.appendRecord(pMode=lCrackingMode, pMask="", pWordlist="", pRule="",
                           pNumberPasswordsCracked=lWatcher.number_passwords_cracked_by_this_mode,
                           pNumberPasswordsCrackedPerSecond=lWatcher.number_passwords_cracked_by_this_mode_per_second,
                           pPercentPasswordsCracked=lWatcher.percent_passwords_cracked_by_this_mode)


def do_run_jtr_prince_mode(pJTR: JohnTheRipper, pVerbose: bool, pDebug: bool, pNumberHashes: int) -> None:

    lCrackingMode = "John the Ripper (JTR) Prince Mode"

    lWatcher = Watcher(pCrackingMode=lCrackingMode, pNumberHashes=pNumberHashes, pVerbose=pVerbose,
                       pDebug=pDebug, pJTRPotFilePath=pJTR.jtr_pot_file_path)
    lWatcher.start_timer()
    lWatcher.print_mode_start_message()

    pJTR.prince_element_count_min = 2
    pJTR.prince_element_count_max = 3
    pJTR.path_to_wordlist = "dictionaries"
    pJTR.wordlist = "prince.txt"
    pJTR.run_prince_mode()

    pJTR.prince_element_count_min = 2
    pJTR.prince_element_count_max = 2
    pJTR.wordlist = "short-list.txt"
    pJTR.run_prince_mode()
    pJTR.run_prince_mode()

    pJTR.wordlist = "top-10000-english-words.txt"
    pJTR.run_prince_mode()
    pJTR.run_prince_mode()

    lWatcher.stop_timer()
    lWatcher.print_mode_finsihed_message()

    gReporter.appendRecord(pMode=lCrackingMode, pMask="", pWordlist="", pRule="",
                           pNumberPasswordsCracked=lWatcher.number_passwords_cracked_by_this_mode,
                           pNumberPasswordsCrackedPerSecond=lWatcher.number_passwords_cracked_by_this_mode_per_second,
                           pPercentPasswordsCracked=lWatcher.percent_passwords_cracked_by_this_mode)


def run_jtr_baseword_mode(pJTR: JohnTheRipper, pBaseWords: str, pVerbose: bool,
                          pDebug: bool, pNumberHashes: int) -> None:

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
    run_jtr_wordlist_mode(pJTR=pJTR, pWordlist=lBaseWordsFileName, pRule="Best126",
                          pVerbose=pVerbose, pDebug=pDebug, pNumberHashes=pNumberHashes)
    run_jtr_wordlist_mode(pJTR=pJTR, pWordlist=lBaseWordsFileName, pRule="OneRuleToRuleThemAll",
                          pVerbose=pVerbose, pDebug=pDebug, pNumberHashes=pNumberHashes)
    run_jtr_wordlist_mode(pJTR=pJTR, pWordlist=lBaseWordsFileName, pRule="All",
                          pVerbose=pVerbose, pDebug=pDebug, pNumberHashes=pNumberHashes)
    os.remove(lBaseWordsFileName)

    if pVerbose: print("[*] Finished Baseword Mode")


def run_jtr_recycle_mode(pJTR: JohnTheRipper, pVerbose: bool, pDebug: bool, pNumberHashes: int) -> None:

    if pVerbose: print("[*] Starting mode: Recycle")

    # The JTR POT file is the source of passwords
    lListOfPasswords = pJTR.parse_passwords_from_pot()

    lListOfBasewords =  [ "".join(re.findall("[a-z]+", lWord.decode("utf-8"))) for lWord in lListOfPasswords]
    lListOfWordsLess1 = [lWord.decode("utf-8")[:lWord.__len__()-1]  for lWord in lListOfPasswords]
    lListOfWordsLess2 = [lWord.decode("utf-8")[:lWord.__len__()-2]  for lWord in lListOfPasswords]
    lListOfWordsLess3 = [lWord.decode("utf-8")[:lWord.__len__()-3]  for lWord in lListOfPasswords]
    lListOfWordsLess4 = [lWord.decode("utf-8")[:lWord.__len__()-4]  for lWord in lListOfPasswords]
    lListOfWordsLess5 = [lWord.decode("utf-8")[:lWord.__len__()-5]  for lWord in lListOfPasswords]
    lListOfWordsLess6 = [lWord.decode("utf-8")[:lWord.__len__()-6]  for lWord in lListOfPasswords]

    lListOfBasewords.extend(lListOfWordsLess1)
    lListOfBasewords.extend(lListOfWordsLess2)
    lListOfBasewords.extend(lListOfWordsLess3)
    lListOfBasewords.extend(lListOfWordsLess4)
    lListOfBasewords.extend(lListOfWordsLess5)
    lListOfBasewords.extend(lListOfWordsLess6)
    lUniqueBasewordsPreserveCase = list(set(lListOfBasewords))

    lBasewordsLowerCase = [lWord.lower() for lWord in lUniqueBasewordsPreserveCase]
    lUniqueBasewordsLowerCase = list(set(lBasewordsLowerCase))

    lUniqueBasewordsPreserveCase.extend(lUniqueBasewordsLowerCase)
    lUniqueBasewords = list(set(lUniqueBasewordsPreserveCase))

    lRecycleFileName = 'basewords/recycle.txt'
    lRecycleDirectory = os.path.dirname(lRecycleFileName)
    if not os.path.exists(lRecycleDirectory): os.makedirs(lRecycleDirectory)
    lRecycleFile = open(lRecycleFileName, 'w')

    for lBaseword in lUniqueBasewords:
        lRecycleFile.write("{}\n".format(lBaseword))
    lRecycleFile.flush()
    lRecycleFile.close()

    if pVerbose:
        lCountPasswords = lUniqueBasewords.__len__()
        print("[*] Using {} unique words for recycle mode".format(str(lCountPasswords)))
        if lCountPasswords > 1000000: print("[*] That is a lot of words. Recycle mode may take a while.")

    run_jtr_wordlist_mode(pJTR=pJTR, pWordlist=lRecycleFileName, pRule="SlowHashesPhase1",
                          pVerbose=pVerbose, pDebug=pDebug, pNumberHashes=pNumberHashes)
    run_jtr_wordlist_mode(pJTR=pJTR, pWordlist=lRecycleFileName, pRule="Best126",
                          pVerbose=pVerbose, pDebug=pDebug, pNumberHashes=pNumberHashes)
    run_jtr_wordlist_mode(pJTR=pJTR, pWordlist=lRecycleFileName, pRule="SlowHashesPhase2",
                          pVerbose=pVerbose, pDebug=pDebug, pNumberHashes=pNumberHashes)
    run_jtr_wordlist_mode(pJTR=pJTR, pWordlist=lRecycleFileName, pRule="SlowHashesPhase3",
                          pVerbose=pVerbose, pDebug=pDebug, pNumberHashes=pNumberHashes)
    run_jtr_wordlist_mode(pJTR=pJTR, pWordlist=lRecycleFileName, pRule="OneRuleToRuleThemAll",
                          pVerbose=pVerbose, pDebug=pDebug, pNumberHashes=pNumberHashes)

    os.remove(lRecycleFileName)

    if pVerbose: print("[*] Finished  Mode: Recycle")


def run_statistical_crack_mode(pJTR: JohnTheRipper, pPercentile: float, pVerbose: bool,
                               pDebug: bool, pNumberHashes: int) -> None:

    # The JTR POT file is the source of passwords
    if pVerbose: print("[*] Parsing JTR POT file at {}".format(pJTR.jtr_pot_file_path))
    lListOfPasswords = pJTR.parse_passwords_from_pot()

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
            do_run_jtr_mask_mode(pJTR=pJTR, pMask=lMask, pWordlist=lWordlist,
                                pVerbose=pVerbose, pDebug=pDebug, pNumberHashes=pNumberHashes)
        else:

            # All lowercase letters
            if re.match('^(\?l)+$', lMask):
                lCountLetters = lMask.count('?l')
                if lCountLetters > MAX_CHARS_TO_BRUTEFORCE:
                    lWordlist = "dictionaries/{}-character-words.txt".format(str(lCountLetters))
                    lRule=""
                    run_jtr_wordlist_mode(pJTR=pJTR, pWordlist=lWordlist, pRule=lRule,
                                          pVerbose=pVerbose, pDebug=pDebug, pNumberHashes=pNumberHashes)

            # All uppercase
            elif re.match('^(\?u)+$', lMask):
                lCountLetters = lMask.count('?u')
                lWordlist = "dictionaries/{}-character-words.txt".format(str(lCountLetters))
                lRule = "uppercase"
                run_jtr_wordlist_mode(pJTR=pJTR, pWordlist=lWordlist, pRule=lRule,
                                      pVerbose=pVerbose, pDebug=pDebug, pNumberHashes=pNumberHashes)

            # Uppercase followed by lowercase (assume only leading letter is uppercase)
            elif re.match('^(\?u)(\?l)+$', lMask):
                lCountLetters = lMask.count('?u') + lMask.count('?l')
                lWordlist = "dictionaries/{}-character-words.txt".format(str(lCountLetters))
                lRule = "capitalize"
                run_jtr_wordlist_mode(pJTR=pJTR, pWordlist=lWordlist, pRule=lRule,
                                      pVerbose=pVerbose, pDebug=pDebug, pNumberHashes=pNumberHashes)

            # Lowercase ending with digits
            elif re.match('^(\?l)+(\?d)+$', lMask):
                lCountLetters = lMask.count('?l')
                lCountDigits = lMask.count('?d')
                lWordlist = "dictionaries/{}-character-words.txt".format(str(lCountLetters))
                lRule = "append{}digits".format(str(lCountDigits))
                run_jtr_wordlist_mode(pJTR=pJTR, pWordlist=lWordlist, pRule=lRule,
                                      pVerbose=pVerbose, pDebug=pDebug, pNumberHashes=pNumberHashes)

            # Uppercase followed by digits
            elif re.match('^(\?u)+(\?d)+$', lMask):
                lCountLetters = lMask.count('?u')
                lCountDigits = lMask.count('?d')
                lWordlist = "dictionaries/{}-character-words.txt".format(str(lCountLetters))
                lRule = "uppercaseappend{}digits".format(str(lCountDigits))
                run_jtr_wordlist_mode(pJTR=pJTR, pWordlist=lWordlist, pRule=lRule,
                                      pVerbose=pVerbose, pDebug=pDebug, pNumberHashes=pNumberHashes)

            # Uppercase, lowercase, then digits (assume only leading letter is uppercase)
            elif re.match('^(\?u)(\?l)+(\?d)+$', lMask):
                lCountLetters = lMask.count('?u') + lMask.count('?l')
                lCountDigits = lMask.count('?d')
                lWordlist = "dictionaries/{}-character-words.txt".format(str(lCountLetters))
                lRule = "capitalizeappend{}digits".format(str(lCountDigits))
                run_jtr_wordlist_mode(pJTR=pJTR, pWordlist=lWordlist, pRule=lRule,
                                      pVerbose=pVerbose, pDebug=pDebug, pNumberHashes=pNumberHashes)

            # Low number of digits. We do not cover large numbers of digits because
            # precomputing dictionary files would be huge and running mask mode takes a long time.
            # Right now we support 4-6 digits only. Recall we cover 4 and 6 digits specifically in
            # "prayer" mode so we do not repeat those two masks here.
            elif re.match('^(\?d)+$', lMask):
                lCountDigits = lMask.count('?d')
                if lCountDigits == 5:
                    lWordlist = "dictionaries/{}-digit-numbers.txt".format(str(lCountDigits))
                    lRule =""
                    run_jtr_wordlist_mode(pJTR=pJTR, pWordlist=lWordlist, pRule=lRule,
                                          pVerbose=pVerbose, pDebug=pDebug, pNumberHashes=pNumberHashes)
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
                    do_run_jtr_mask_mode(pJTR=pJTR, pMask=lMaskParam, pWordlist=lWordlist,
                                      pVerbose=pVerbose, pDebug=pDebug, pNumberHashes=pNumberHashes)
                else:
                    print("[*] WARNING: Did not process mask {} because it is out of policy".format(lMask))

            else:
                lUndefinedMasks.append(lMask)
                print("[*] WARNING: No policy defined for mask {}".format(lMask))

    # List masks that did not match a pattern so that a pattern can be added
    if lUndefinedMasks: print(
        "[*] WARNING: There was no policy defined for the following masks: {}".format(lUndefinedMasks))


def run_jtr_brute_force_mode(pJTR: JohnTheRipper, pMinCharactersToBruteForce: int,
                             pMaxCharactersToBruteForce: int,
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

        # Make additional masks by replacing last character of each mask with a symbol.
        # This will create duplicates (i.e. ?l?l?l and ?l?l?d both become ?l?l?s)
        lSymbolMasks = []
        for lMask in lMasks:
            lSymbolMasks.append(lMask[:lMask.__len__()-2] + "?s")

        # Remove duplicates from symbol masks and add to list of masks
        lMasks.extend(list(set(lSymbolMasks)))

        for lMask in lMasks:
            do_run_jtr_mask_mode(pJTR=pJTR, pMask=lMask, pWordlist=None,
                                 pVerbose=pVerbose, pDebug=pDebug, pNumberHashes=pNumberHashes)


def run_jtr_single_mode(pJTR: JohnTheRipper, pVerbose: bool, pDebug: bool, pNumberHashes: int) -> None:
    """
    :rtype: None
    """
    # Hard to say how many mangles but will be proportional to number of hashes
    do_run_jtr_single_mode(pJTR=pJTR, pVerbose=pVerbose,
                           pDebug=pDebug, pNumberHashes=pNumberHashes)


def run_jtr_prince_mode(pJTR: JohnTheRipper, pVerbose: bool, pDebug: bool, pNumberHashes: int) -> None:
    """
    :rtype: None
    """
    # Hard to say how many mangles but will be proportional to number of hashes
    do_run_jtr_prince_mode(pJTR=pJTR, pVerbose=pVerbose,
                           pDebug=pDebug, pNumberHashes=pNumberHashes)


def run_jtr_prayer_mode(pJTR: JohnTheRipper, pMethod: int, pVerbose: bool,
                        pDebug: bool, pNumberHashes: int) -> None:

    lTechniques = Techniques()
    lFolder, lDictionaries, lRules = lTechniques.get_technique(pMethod)

    # Run the wordlist and rule
    for lDictionary in lDictionaries:
        for lRule in lRules:
            run_jtr_wordlist_mode(pJTR=pJTR, pWordlist=lFolder + "/" + lDictionary, pRule=lRule,
                                  pVerbose=pVerbose, pDebug=pDebug, pNumberHashes=pNumberHashes)


if __name__ == '__main__':

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
                            help="Comma-separated list of integers between 0-15 that determines what password cracking techniques are attempted. Default is level 1,2 and 3. Example of running levels 1 and 2 --techniques=1,2\n\n1: Common Passwords\n2: Small Dictionaries. Small Rulesets\n3: Calendar Related\n4: Medium Dictionaries. Small Rulesets\n5: Small Dictionaries. Medium Rulesets\n6: Medium Dictionaries. Medium Rulesets\n7: Large Password List. Custom Ruleset\n8: Medium-Large Dictionaries. Small Rulesets\n9: Small Dictionaries. Large Rulesets\n10: Medium Dictionaries. Large Rulesets\n11: Medium-Large Dictionaries. Medium Rulesets\n12: Large Dictionaries. Small Rulesets\n13: Medium-Large Dictionaries. Large Rulesets\n14: Large Dictionaries. Medium Rulesets\n15: Large Dictionaries. Large Rulesets\n\n",
                            action='store')
    lArgParser.add_argument('-u', '--jtr-single-crack',
                            help='Run John the Ripper''s Single Crack mode. This mode uses information in the user account metadata to generate guesses. This mode is most effective when the hashes are formatted to include GECOS fields.',
                            action='store_true')
    lArgParser.add_argument('-r', '--recycle',
                            help='After all cracking attempts are finished, use the root words of already cracked passwords to create a new dictionary. Try to crack more passwords with the new dictionary.',
                            action='store_true')
    lArgParser.add_argument('-c', '--jtr-prince',
                            help='Run John the Ripper''s Prince mode. This mode combines words within a dicitonary to generate guesses.',
                            action='store_true')
    lArgParser.add_argument('-s', '--stat-crack',
                            help="Enable statistical cracking. Byepass will run relatively fast cracking strategies in hopes of cracking enough passwords to induce a pattern and create \"high probability\" masks. Byepass will use the masks in an attempt to crack more passwords.\n\n",
                            action='store_true')
    lArgParser.add_argument('-p', '--percentile',
                            type=float,
                            help="Based on statistical analysis of the passwords cracked during initial phase, use only the masks statistically likely to be needed to crack at least the given percent of passwords. For example, if a value of 0.25 provided, only use the relatively few masks needed to crack 25 passwords of the passwords. Note that password cracking effort follows an exponential distribution, so cracking a few more passwords takes a lot more effort (relatively speaking). A good starting value if completely unsure is 25 percent (0.25).\n\n",
                            action='store')
    lArgParser.add_argument('-a', '--all',
                             help="Shortcut equivalent to -t 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15 -s -p 0.9 -u -c -r",
                             action='store_true')
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

    if lArgs.all:
        lArgs.techniques = "1,2,3,4,5,6,7,8,9,10,11,12,13,14,15"
        lArgs.jtr_single_crack = True
        lArgs.jtr_prince = True
        lArgs.recycle = True
        lArgs.stat_crack = True
        lArgs.percentile = 0.90

    # Parse and validate input parameters
    lHashFormat = parse_arg_hash_format(lArgs.hash_format)
    lBasewords = lArgs.basewords
    lBruteForce = lArgs.brute_force
    lStatCrack = lArgs.stat_crack
    lHashFile = lArgs.input_file
    lVerbose = lArgs.verbose
    lRunSingleCrack = lArgs.jtr_single_crack
    lRecyclePasswords = lArgs.recycle
    lRunPrince = lArgs.jtr_prince
    lDebug = parse_arg_debug(lArgs.debug)
    lTechniques = parse_argTechniques(lArgs.techniques)
    lPassThrough = lArgs.pass_through

    lRunDefaultTechniques = not lRunSingleCrack and not lBasewords and \
                            not lBruteForce and not lArgs.techniques and \
                            not lStatCrack and not lRecyclePasswords and \
                            not lRunPrince

    lJTR = JohnTheRipper(pJTRExecutableFilePath = Config.JTR_EXECUTABLE_FILE_PATH, pJTRPotFilePath = Config.JTR_POT_FILE_PATH,
                         pHashFilePath=lHashFile, pHashFormat=lHashFormat, pPassThrough=lPassThrough,
                         pVerbose=lVerbose, pDebug=lDebug)

    lNumberHashes = count_hashes_in_input_file(pHashFile=lHashFile)
    lNumberPasswordsPOTFileAtStart = lJTR.count_passwords_in_pot()

    if lVerbose:
        lStartTime = time.time()
        print("[*] Working on input file {} ({} lines)".format(lHashFile, lNumberHashes))

    # If user did not specify any technique, run default technique
    if lRunDefaultTechniques:
        # Run technique 1,2 and 3 by default
        lTechniques = [1,2,3]
        print("[*] WARNING: No technique specified. Running techniques 1,2 and 3")

    # Hopefully user has some knowledge of system to give good base words
    if lBasewords:
        run_jtr_baseword_mode(pJTR=lJTR, pBaseWords=lArgs.basewords, pVerbose=lVerbose,
                              pDebug=lDebug, pNumberHashes=lNumberHashes)

    # John the Ripper Single Crack mode
    if lRunSingleCrack:
        run_jtr_single_mode(pJTR=lJTR, pVerbose=lVerbose, pDebug=lDebug, pNumberHashes=lNumberHashes)

    # Smart brute-force
    if lBruteForce:
        lMinCharactersToBruteForce, lMaxCharactersToBruteForce = parse_arg_brute_force(lArgs.brute_force)
        run_jtr_brute_force_mode(pJTR=lJTR, pMinCharactersToBruteForce=lMinCharactersToBruteForce,
                                 pMaxCharactersToBruteForce=lMaxCharactersToBruteForce,
                                 pVerbose=lVerbose, pDebug=lDebug, pNumberHashes=lNumberHashes)

    # Try to crack passwords using the techniques specified
    for i in lTechniques:
        run_jtr_prayer_mode(pJTR=lJTR, pMethod=i, pVerbose=lVerbose, pDebug=lDebug,
                            pNumberHashes=lNumberHashes)

    # John the Ripper Single Crack mode
    if lRunPrince:
        run_jtr_prince_mode(pJTR=lJTR, pVerbose=lVerbose, pDebug=lDebug, pNumberHashes=lNumberHashes)

    # If the user chooses -s option, begin statistical analysis to aid targeted cracking routines
    if lStatCrack:
        lPercentile = parse_arg_percentile(lArgs.percentile)
        run_statistical_crack_mode(pJTR=lJTR, pPercentile=lPercentile, pVerbose=lVerbose,
                                   pDebug=lDebug, pNumberHashes=lNumberHashes)

    if lRecyclePasswords:
        run_jtr_recycle_mode(pJTR=lJTR, pVerbose=lVerbose,
                             pDebug=lDebug, pNumberHashes=lNumberHashes)

    if lVerbose:
        lEndTime = time.time()
        lNumberPasswordsPOTFileAtEnd = lJTR.count_passwords_in_pot()
        print_closing_message(pJTR=lJTR, pNumberHashes=lNumberHashes,
                              pNumberPasswordsPOTFileAtStart=lNumberPasswordsPOTFileAtStart,
                              pNumberPasswordsPOTFileAtEnd=lNumberPasswordsPOTFileAtEnd,
                              pStartTime=lStartTime, pEndTime=lEndTime)