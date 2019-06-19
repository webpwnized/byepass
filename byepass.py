# JTR Mask Mode: https://github.com/magnumripper/JohnTheRipper/blob/bleeding-jumbo/doc/MASK

from argparse import RawTextHelpFormatter
from pwstats import PasswordStats
from techniques import Techniques
from watcher import Watcher
from reporter import Reporter
from jtr import JohnTheRipper
from printer import Printer,Level
from argparser import Parser
import config as Config
import os.path
import re
import argparse
import gc
import subprocess


#METHODS
def write_list_to_file(pLines: list, pFileName: str, pAppend: bool) -> None:

    WRITE = 'w'
    APPEND = 'a+'
    lMode = APPEND if pAppend else WRITE
    lDirectory = os.path.dirname(pFileName)
    if not os.path.exists(lDirectory): os.makedirs(lDirectory)
    gPrinter.print(pMessage="Writing to file {}".format(pFileName), pLevel=Level.INFO)
    lFile = open(pFileName, lMode)

    for lLine in pLines:
        lFile.write("{}\n".format(lLine))
    lFile.flush()
    lFile.close()
    gPrinter.print(pMessage="Finished writing to file {}".format(pFileName), pLevel=Level.INFO)


def do_run_jtr_mask_mode(pJTR: JohnTheRipper, pMask: str, pWordlist: str, pRule: str) -> None:

    lCrackingMode = "Mask {}".format(pMask)
    if pWordlist: lCrackingMode += " using wordlist {}".format(pWordlist)
    if pRule: lCrackingMode += " with rule {}".format(pWordlist)

    lWatcher = Watcher(pCrackingMode=lCrackingMode, pJTR=pJTR)
    lWatcher.start_timer()
    lWatcher.print_mode_start_message()
    
    pJTR.run_mask_mode(pMask=pMask, pWordlist=pWordlist, pRule=pRule)

    lWatcher.stop_timer()
    lWatcher.print_mode_finsihed_message()

    gReporter.appendRecord(pMode=lCrackingMode, pMask=pMask, pWordlist=pWordlist, pRule=pRule,
                           pNumberPasswordsCracked=lWatcher.number_passwords_cracked_by_this_mode,
                           pNumberPasswordsCrackedPerSecond=lWatcher.number_passwords_cracked_by_this_mode_per_second,
                           pPercentPasswordsCracked=lWatcher.percent_passwords_cracked_by_this_mode)


def do_run_jtr_wordlist_mode(pJTR: JohnTheRipper, pWordlist: str, pRule: str) -> None:

    lCrackingMode = "Wordlist {}".format(pWordlist)
    if pRule: lCrackingMode += " with rule {}".format(pRule)

    lWatcher = Watcher(pCrackingMode=lCrackingMode, pJTR=pJTR)
    lWatcher.start_timer()
    lWatcher.print_mode_start_message()

    pJTR.run_wordlist_mode(pWordlist=pWordlist, pRule=pRule)

    lWatcher.stop_timer()
    lWatcher.print_mode_finsihed_message()

    gReporter.appendRecord(pMode=lCrackingMode, pMask="", pWordlist=pWordlist, pRule=pRule,
                           pNumberPasswordsCracked=lWatcher.number_passwords_cracked_by_this_mode,
                           pNumberPasswordsCrackedPerSecond=lWatcher.number_passwords_cracked_by_this_mode_per_second,
                           pPercentPasswordsCracked=lWatcher.percent_passwords_cracked_by_this_mode)


def do_run_jtr_single_mode(pJTR: JohnTheRipper) -> None:

    lCrackingMode = "John the Ripper (JTR) Single Crack"

    lWatcher = Watcher(pCrackingMode=lCrackingMode, pJTR=pJTR)
    lWatcher.start_timer()
    lWatcher.print_mode_start_message()

    pJTR.run_single_crack()

    lWatcher.stop_timer()
    lWatcher.print_mode_finsihed_message()

    gReporter.appendRecord(pMode=lCrackingMode, pMask="", pWordlist="", pRule="",
                           pNumberPasswordsCracked=lWatcher.number_passwords_cracked_by_this_mode,
                           pNumberPasswordsCrackedPerSecond=lWatcher.number_passwords_cracked_by_this_mode_per_second,
                           pPercentPasswordsCracked=lWatcher.percent_passwords_cracked_by_this_mode)


def do_run_jtr_prince_mode(pJTR: JohnTheRipper) -> None:

    lCrackingMode = "John the Ripper (JTR) Prince Mode"

    lWatcher = Watcher(pCrackingMode=lCrackingMode, pJTR=pJTR)
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

    pJTR.wordlist = "top-10000-english-words.txt"
    pJTR.run_prince_mode()

    lWatcher.stop_timer()
    lWatcher.print_mode_finsihed_message()

    gReporter.appendRecord(pMode=lCrackingMode, pMask="", pWordlist="", pRule="",
                           pNumberPasswordsCracked=lWatcher.number_passwords_cracked_by_this_mode,
                           pNumberPasswordsCrackedPerSecond=lWatcher.number_passwords_cracked_by_this_mode_per_second,
                           pPercentPasswordsCracked=lWatcher.percent_passwords_cracked_by_this_mode)


def run_jtr_baseword_mode(pJTR: JohnTheRipper, pBaseWords: list) -> None:

    gPrinter.print("Starting mode: Baseword with words {}".format(pBaseWords), Level.INFO)

    lBaseWordsFileName = 'basewords/basewords.txt'
    write_list_to_file(pLines=pBaseWords, pFileName=lBaseWordsFileName, pAppend=False)

    do_run_jtr_wordlist_mode(pJTR=pJTR, pWordlist=lBaseWordsFileName, pRule="SlowHashesPhase1")
    do_run_jtr_wordlist_mode(pJTR=pJTR, pWordlist=lBaseWordsFileName, pRule="Best126")
    do_run_jtr_wordlist_mode(pJTR=pJTR, pWordlist=lBaseWordsFileName, pRule="SlowHashesPhase2")
    do_run_jtr_wordlist_mode(pJTR=pJTR, pWordlist=lBaseWordsFileName, pRule="SlowHashesPhase3")
    do_run_jtr_wordlist_mode(pJTR=pJTR, pWordlist=lBaseWordsFileName, pRule="OneRuleToRuleThemAll")
    do_run_jtr_wordlist_mode(pJTR=pJTR, pWordlist=lBaseWordsFileName, pRule="All")

    os.remove(lBaseWordsFileName)

    gPrinter.print("Finished Baseword Mode", Level.INFO)


def run_jtr_recycle_mode(pJTR: JohnTheRipper) -> None:

    gPrinter.print("Starting Recycle mode", Level.INFO)

    # The JTR POT file is the source of passwords
    lRecycleFileName = 'basewords/recycle.txt'

    # original password from pot file
    gPrinter.print("Working on original words", Level.INFO)
    lListOfPasswords=pJTR.parse_passwords_from_pot()
    write_list_to_file(pLines=lListOfPasswords, pFileName=lRecycleFileName, pAppend=False)

    # lowercase
    gPrinter.print("Working on lowercase version", Level.INFO)
    write_list_to_file(pLines=[lWord.lower() for lWord in lListOfPasswords], pFileName=lRecycleFileName, pAppend=True)
    gPrinter.print("Garbage collecting", Level.INFO)
    gc.collect()

    # root words
    gPrinter.print("Working on root words", Level.INFO)
    lListOfBasewords =  [ "".join(re.findall("[a-zA-Z]+", lWord.decode("utf-8"))) for lWord in lListOfPasswords]
    write_list_to_file(pLines=lListOfBasewords, pFileName=lRecycleFileName, pAppend=True)

    # lowercase
    gPrinter.print("Working on lowercase version", Level.INFO)
    write_list_to_file(pLines=[lWord.lower() for lWord in lListOfBasewords], pFileName=lRecycleFileName, pAppend=True)
    gPrinter.print("Garbage collecting", Level.INFO)
    gc.collect()

    # original passwords minus last character
    gPrinter.print("Working on original words minus last character", Level.INFO)
    lListOfBasewords = [lWord.decode("utf-8")[:lWord.__len__()-1]  for lWord in lListOfPasswords]
    write_list_to_file(pLines=lListOfBasewords, pFileName=lRecycleFileName, pAppend=True)

    # lowercase
    gPrinter.print("Working on lowercase version", Level.INFO)
    write_list_to_file(pLines=[lWord.lower() for lWord in lListOfBasewords], pFileName=lRecycleFileName, pAppend=True)
    gPrinter.print("Garbage collecting", Level.INFO)
    gc.collect()

    # minus last two characters
    gPrinter.print("Working on original words minus last two characters", Level.INFO)
    lListOfBasewords = [lWord.decode("utf-8")[:lWord.__len__()-2]  for lWord in lListOfPasswords]
    write_list_to_file(pLines=lListOfBasewords, pFileName=lRecycleFileName, pAppend=True)

    # lowercase
    gPrinter.print("Working on lowercase version", Level.INFO)
    write_list_to_file(pLines=[lWord.lower() for lWord in lListOfBasewords], pFileName=lRecycleFileName, pAppend=True)
    gPrinter.print("Garbage collecting", Level.INFO)
    gc.collect()

    # minus last three characters
    gPrinter.print("Working on original words minus last three characters", Level.INFO)
    lListOfBasewords = [lWord.decode("utf-8")[:lWord.__len__()-3]  for lWord in lListOfPasswords]
    write_list_to_file(pLines=lListOfBasewords, pFileName=lRecycleFileName, pAppend=True)

    # lowercase
    gPrinter.print("Working on lowercase version", Level.INFO)
    write_list_to_file(pLines=[lWord.lower() for lWord in lListOfBasewords], pFileName=lRecycleFileName, pAppend=True)
    gPrinter.print("Garbage collecting", Level.INFO)
    gc.collect()

    lCmd = ['touch']
    lCmd.append('/tmp/file')
    gPrinter.print("Running command {}".format(lCmd), Level.INFO)
    lCompletedProcess = subprocess.run(lCmd, stdout=subprocess.PIPE)

    lCmd = ['sort']
    lCmd.append('-u')
    lCmd.append('-o /tmp/file')
    lCmd.append(lRecycleFileName)
    gPrinter.print("Running command {}".format(lCmd), Level.INFO)
    lCompletedProcess = subprocess.run(lCmd, stdout=subprocess.PIPE)

    lCmd = ['mv']
    lCmd.append('/tmp/file')
    lCmd.append(lRecycleFileName)
    gPrinter.print("Running command {}".format(lCmd), Level.INFO)
    lCompletedProcess = subprocess.run(lCmd, stdout=subprocess.PIPE)

    gPrinter.print("Wordlist created: {}".format(lRecycleFileName), Level.INFO)

    exit(0)

    do_run_jtr_wordlist_mode(pJTR=pJTR, pWordlist=lRecycleFileName, pRule="SlowHashesPhase1")
    do_run_jtr_wordlist_mode(pJTR=pJTR, pWordlist=lRecycleFileName, pRule="Best126")
    do_run_jtr_wordlist_mode(pJTR=pJTR, pWordlist=lRecycleFileName, pRule="SlowHashesPhase2")
    do_run_jtr_wordlist_mode(pJTR=pJTR, pWordlist=lRecycleFileName, pRule="SlowHashesPhase3")
    do_run_jtr_wordlist_mode(pJTR=pJTR, pWordlist=lRecycleFileName, pRule="OneRuleToRuleThemAll")

    os.remove(lRecycleFileName)

    gPrinter.print("Finished Recycle mode", Level.INFO)


def run_statistical_crack_mode(pJTR: JohnTheRipper, pPercentile: float,
                                 pMaxAllowedCharactersToBruteForce: int) -> None:

    # The JTR POT file is the source of passwords
    gPrinter.print("Parsing JTR POT file at {}".format(pJTR.jtr_pot_file_path), Level.INFO)
    lListOfPasswords = pJTR.parse_passwords_from_pot()

    if pJTR.verbose:
        lCountPasswords = lListOfPasswords.__len__()
        gPrinter.print("Using {} passwords in statistical analysis: ".format(str(lCountPasswords)), Level.INFO)
        if lCountPasswords > 1000000: gPrinter.print("That is a lot of passwords. Statistical analysis may take a while.", Level.WARNING)

    # Let PasswordStats class analyze most likely masks
    gPrinter.print("Beginning statistical analysis", Level.INFO)
    lPasswordStats = PasswordStats(lListOfPasswords)
    gPrinter.print("Parsed {} passwords into {} masks".format(lPasswordStats.count_passwords, lPasswordStats.count_masks), Level.INFO)

    # Calculate masks most likely need to crack X% of the password hashes
    lMasks = lPasswordStats.get_popular_masks(pPercentile)
    gPrinter.print("Password masks ({} percentile): {}".format(pPercentile, lMasks), Level.INFO)

    run_smart_mask_mode(pJTR=pJTR, pMasks=lMasks, pMaxAllowedCharactersToBruteForce=pMaxAllowedCharactersToBruteForce)


def run_pathwell_mode(pJTR: JohnTheRipper, pFirstMask: int, pLastMask: int,
                                 pMaxAllowedCharactersToBruteForce: int) -> None:

    gPrinter.print("Starting Pathwell mode", Level.INFO)

    lPathwellFileName = 'masks/pathwell.txt'

    with open(lPathwellFileName, "r") as lPathwellFile:
        lMasks = lPathwellFile.read().splitlines()
    lPathwellFile.close()

    lPathwellMasks = []
    for i in range(pFirstMask-1, pLastMask):
        lPathwellMasks.append(lMasks[i])

    run_smart_mask_mode(pJTR=pJTR, pMasks=lPathwellMasks, pMaxAllowedCharactersToBruteForce=pMaxAllowedCharactersToBruteForce)

    gPrinter.print("Finished Pathwell Mode", Level.INFO)


def run_smart_mask_mode(pJTR: JohnTheRipper, pMasks: list, pMaxAllowedCharactersToBruteForce: int):

    # For each mask, try high probability guesses
    lUndefinedMasks = []
    for lMask in pMasks:
        gPrinter.print("Processing mask: {}".format(lMask), Level.INFO)

        # If the number of characters in the mask is "small" as defined by
        # MAX_CHARS_TO_BRUTEFORCE, then use brute-force on the pattern.
        # If there are more characters than the limit, use "smart brute-force"
        # which is a hybrid between dictionary and mask mode.
        lCountCharacters = int(len(lMask) / 2)
        if lCountCharacters <= pMaxAllowedCharactersToBruteForce:
            lWordlist = ""
            do_run_jtr_mask_mode(pJTR=pJTR, pMask=lMask, pWordlist=lWordlist, pRule=None)
        else:

            # All lowercase letters
            if re.match('^(\?l)+$', lMask):
                lCountLetters = lMask.count('?l')
                if lCountLetters > pMaxAllowedCharactersToBruteForce:
                    lWordlist = "dictionaries/{}-character-words.txt".format(str(lCountLetters))
                    lRule=""
                    do_run_jtr_wordlist_mode(pJTR=pJTR, pWordlist=lWordlist, pRule=lRule)

            # All uppercase
            elif re.match('^(\?u)+$', lMask):
                lCountLetters = lMask.count('?u')
                lWordlist = "dictionaries/{}-character-words.txt".format(str(lCountLetters))
                lRule = "uppercase"
                do_run_jtr_wordlist_mode(pJTR=pJTR, pWordlist=lWordlist, pRule=lRule)

            # Uppercase followed by lowercase (assume only leading letter is uppercase)
            elif re.match('^(\?u)(\?l)+$', lMask):
                lCountLetters = lMask.count('?u') + lMask.count('?l')
                lWordlist = "dictionaries/{}-character-words.txt".format(str(lCountLetters))
                lRule = "capitalize"
                do_run_jtr_wordlist_mode(pJTR=pJTR, pWordlist=lWordlist, pRule=lRule)

            # Lowercase ending with digits
            elif re.match('^(\?l)+(\?d)+$', lMask):
                lCountLetters = lMask.count('?l')
                lCountDigits = lMask.count('?d')
                lWordlist = "dictionaries/{}-character-words.txt".format(str(lCountLetters))
                lRule = "append{}digits".format(str(lCountDigits))
                do_run_jtr_wordlist_mode(pJTR=pJTR, pWordlist=lWordlist, pRule=lRule)

            # Uppercase followed by digits
            elif re.match('^(\?u)+(\?d)+$', lMask):
                lCountLetters = lMask.count('?u')
                lCountDigits = lMask.count('?d')
                lWordlist = "dictionaries/{}-character-words.txt".format(str(lCountLetters))
                lRule = "uppercaseappend{}digits".format(str(lCountDigits))
                do_run_jtr_wordlist_mode(pJTR=pJTR, pWordlist=lWordlist, pRule=lRule)

            # Uppercase, lowercase, then digits (assume only leading letter is uppercase)
            elif re.match('^(\?u)(\?l)+(\?d)+$', lMask):
                lCountLetters = lMask.count('?u') + lMask.count('?l')
                lCountDigits = lMask.count('?d')
                lWordlist = "dictionaries/{}-character-words.txt".format(str(lCountLetters))
                lRule = "capitalizeappend{}digits".format(str(lCountDigits))
                do_run_jtr_wordlist_mode(pJTR=pJTR, pWordlist=lWordlist, pRule=lRule)

            # Low number of digits. We do not cover large numbers of digits because
            # precomputing dictionary files would be huge and running mask mode takes a long time.
            # Right now we support 4-6 digits only. Recall we cover 4 and 6 digits specifically in
            # "prayer" mode so we do not repeat those two masks here.
            elif re.match('^(\?d)+$', lMask):
                lCountDigits = lMask.count('?d')
                if lCountDigits == 5:
                    lWordlist = "dictionaries/{}-digit-numbers.txt".format(str(lCountDigits))
                    lRule =""
                    do_run_jtr_wordlist_mode(pJTR=pJTR, pWordlist=lWordlist, pRule=lRule)
                else:
                    gPrinter.print("Did not process mask {} because it is out of policy".format(lMask), Level.ERROR)

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
                    lRule =""
                    do_run_jtr_mask_mode(pJTR=pJTR, pMask=lMaskParam, pWordlist=lWordlist, pRule=None)
                else:
                    gPrinter.print("Did not process mask {} because it is out of policy".format(lMask), Level.ERROR)

            # Lowercase ending with something other than the masks already accounted for. If the
            # ending pattern is longer than 4 characters, we do not try because it takes a long time
            # to test that many hashes
            elif re.match('^(\?u)+', lMask):
                lPrefix = re.search('^(\?u)+', lMask).group()
                lCountLetters = lPrefix.count("?u")
                lSuffix = lMask[lCountLetters * 2:]
                if len(lSuffix) <= 4:
                    lWordlist = "dictionaries/{}-character-words.txt".format(str(lCountLetters))
                    lMaskParam = "--mask=?w{}".format(lSuffix)
                    lRule = "uppercase"
                    do_run_jtr_mask_mode(pJTR=pJTR, pMask=lMaskParam, pWordlist=lWordlist, pRule=lRule)
                else:
                    gPrinter.print("Did not process mask {} because it is out of policy".format(lMask), Level.ERROR)

            # Capitalized ending with something other than the masks already accounted for. If the
            # ending pattern is longer than 4 characters, we do not try because it takes a long time
            # to test that many hashes
            elif re.match('^(\?u)(\?l)+$', lMask):
                lPrefix = re.search('^(\?u)(\?l)+', lMask).group()
                lCountLetters = lPrefix.count('?u') + lPrefix.count('?l')
                lSuffix = lMask[lCountLetters * 2:]
                if len(lSuffix) <= 4:
                    lWordlist = "dictionaries/{}-character-words.txt".format(str(lCountLetters))
                    lMaskParam = "--mask=?w{}".format(lSuffix)
                    lRule = "capitalize"
                    do_run_jtr_mask_mode(pJTR=pJTR, pMask=lMaskParam, pWordlist=lWordlist, pRule=lRule)
                else:
                    gPrinter.print("Did not process mask {} because it is out of policy".format(lMask), Level.ERROR)

            else:
                lUndefinedMasks.append(lMask)
                gPrinter.print("No policy defined for mask {}".format(lMask), Level.ERROR)

    # List masks that did not match a pattern so that a pattern can be added
    if lUndefinedMasks: gPrinter.print(
        "There was no policy defined for the following masks: {}".format(lUndefinedMasks), Level.ERROR)


def run_jtr_brute_force_mode(pJTR: JohnTheRipper, pMinCharactersToBruteForce: int,
                             pMaxCharactersToBruteForce: int, pMaxAllowedCharactersToBruteForce: int) -> None:

    lSmartMasks = []
    lSymbolMasks = []
    lBruteMasks = []
    for i in range(pMinCharactersToBruteForce, pMaxCharactersToBruteForce + 1):

        if i <= pMaxAllowedCharactersToBruteForce:
            lBruteMasks.append("?a"*i)
        else:
            lLowersMask = "?l" * i
            lUppersMask = "?u" * i
            lDigitsMask = "?d" * i
            lSmartMasks.extend([lLowersMask, lUppersMask, lDigitsMask])

            # UpperLower pattern requires at least 2 characters
            if i > 1:
                lUpperLowersMask = "?u" + "?l" * (i - 1)
                lSmartMasks.append(lUpperLowersMask)

            #From 1 digit up to i-1 digits where i is length of pattern
            for j in range(1, i):
                lLowerDigitMask = "?l" * (i-j) + "?d" * j
                lUpperDigitMask = "?u" * (i-j) + "?d" * j
                lSmartMasks.append(lLowerDigitMask)
                lSmartMasks.append(lUpperDigitMask)

                # Only generate capitalized if pattern at least 3 characters (i > 2)
                # long and starts with at least an upper and a lower (i - j >= 2)
                if (i > 2) and (i - j >= 2):
                    lUpperLowerDigitMask = "?u" + "?l" * (i-j-1) + "?d" * j
                    lSmartMasks.append(lUpperLowerDigitMask)

    # Make additional masks by replacing last character of each mask with a symbol.
    # This will create duplicates (i.e. ?l?l?l and ?l?l?d both become ?l?l?s)
    for lMask in lSmartMasks:
        lSymbolMasks.append(lMask[:lMask.__len__()-2] + "?s")

    # Remove duplicates from symbol masks and add to list of masks
    lSmartMasks.extend(list(set(lSymbolMasks)))

    # combine brute-force masks with smart masks
    lSmartMasks.extend(lBruteMasks)

    for lMask in lSmartMasks:
        do_run_jtr_mask_mode(pJTR=pJTR, pMask=lMask, pWordlist=None, pRule=None)


def run_jtr_single_mode(pJTR: JohnTheRipper) -> None:
    """
    :rtype: None
    """
    # Hard to say how many mangles but will be proportional to number of hashes
    do_run_jtr_single_mode(pJTR=pJTR)


def run_jtr_prince_mode(pJTR: JohnTheRipper) -> None:
    """
    :rtype: None
    """
    # Hard to say how many mangles but will be proportional to number of hashes
    do_run_jtr_prince_mode(pJTR=pJTR)


def run_jtr_prayer_mode(pJTR: JohnTheRipper, pMethod: int) -> None:

    lTechniques = Techniques()
    lFolder, lDictionaries, lRules = lTechniques.get_technique(pMethod)

    # Run the wordlist and rule
    for lDictionary in lDictionaries:
        for lRule in lRules:
            do_run_jtr_wordlist_mode(pJTR=pJTR, pWordlist=lFolder + "/" + lDictionary, pRule=lRule)


def run_main_program(pParser: Parser):

    gPrinter.verbose = pParser.verbose
    gPrinter.debug = pParser.debug

    if pParser.show_examples:
        gPrinter.print_example_usage()
        exit(0)

    lJTR = JohnTheRipper(pJTRExecutableFilePath = pParser.config_file.JTR_EXECUTABLE_FILE_PATH,
                         pJTRPotFilePath = pParser.config_file.JTR_POT_FILE_PATH,
                         pHashFilePath=pParser.hash_file, pHashFormat=pParser.hash_format, pPassThrough=pParser.jtr_pass_through,
                         pVerbose=pParser.verbose, pDebug=pParser.debug)

    lWatcher = Watcher(pJTR=lJTR, pCrackingMode="Cracking Job")
    lWatcher.start_timer()
    lWatcher.print_program_starting_message()

    # Hopefully user has some knowledge of system to give good base words
    if pParser.run_basewords_mode:
        run_jtr_baseword_mode(pJTR=lJTR, pBaseWords=pParser.basewords)

    # John the Ripper Single Crack mode
    if pParser.run_jtr_single_crack:
        run_jtr_single_mode(pJTR=lJTR)

    # Techniques mode
    for i in pParser.techniques:
        run_jtr_prayer_mode(pJTR=lJTR, pMethod=i)

    # Pathwell mode
    if pParser.run_pathwell_mode:
        run_pathwell_mode(pJTR=lJTR, pFirstMask=pParser.first_pathwell_mask, pLastMask=pParser.last_pathwell_mask,
                          pMaxAllowedCharactersToBruteForce=pParser.config_file.MAX_CHARS_TO_BRUTEFORCE)

    # Smart brute-force
    if pParser.run_brute_force:
        run_jtr_brute_force_mode(pJTR=lJTR,
                                 pMinCharactersToBruteForce=pParser.min_characters_to_brute_force,
                                 pMaxCharactersToBruteForce=pParser.max_characters_to_brute_force,
                                 pMaxAllowedCharactersToBruteForce=pParser.config_file.MAX_CHARS_TO_BRUTEFORCE)

    # John the Ripper Prince mode
    if pParser.run_jtr_prince_mode:
        run_jtr_prince_mode(pJTR=lJTR)

    # If the user chooses -s option, begin statistical analysis to aid targeted cracking routines
    if pParser.run_stat_crack:
        run_statistical_crack_mode(pJTR=lJTR, pPercentile=pParser.percentile,
                                 pMaxAllowedCharactersToBruteForce=pParser.config_file.MAX_CHARS_TO_BRUTEFORCE)

    if pParser.recycle_passwords:
        run_jtr_recycle_mode(pJTR=lJTR)

    lWatcher.stop_timer()
    lWatcher.print_program_finsihed_message(pReporter=gReporter)


if __name__ == '__main__':

    # GLOBALS
    gReporter = Reporter()
    gPrinter = Printer()

    lArgParser = argparse.ArgumentParser(description="""
  ___          ___
 | _ )_  _ ___| _ \__ _ ______
 | _ \ || / -_)  _/ _` (_-<_-<
 |___/\_, \___|_| \__,_/__/__/
      |__/
 
 Automated password hash analysis - Fortuna Fortis Paratus
""", formatter_class=RawTextHelpFormatter)
    lArgParser.add_argument('-f', '--hash-format',
                            type=str,
                            help="The hash algorithm used to hash the password(s). This value must be one of the values supported by John the Ripper. To see formats supported by JTR, use command \"john --list=formats\". It is strongly recommended to provide an optimal value. If no value is provided, John the Ripper will guess.\n\n",
                            action='store')
    lArgParser.add_argument('-w', '--basewords',
                            type=str,
                            help="Supply a comma-separated list of lowercase, unmangled base words thought to be good candidates. For example, if Wiley Coyote is cracking hashes from Acme Inc., Wiley might provide the word \"acme\". Be careful how many words are supplied as Byepass will apply many mangling rules. Up to several should run reasonably fast.\n\n",
                            action='store')
    lArgParser.add_argument('-u', '--jtr-single-crack',
                            help='Run John the Ripper''s Single Crack mode. This mode uses information in the user account metadata to generate guesses. This mode is most effective when the hashes are formatted to include GECOS fields.',
                            action='store_true')
    lArgParser.add_argument('-t', '--techniques',
                            type=str,
                            help="Comma-separated list of integers between 0-15 that determines what password cracking techniques are attempted. Default is level 1,2 and 3. Example of running levels 1 and 2 --techniques=1,2\n\n1: Common Passwords\n2: Small Dictionaries. Small Rulesets\n3: Calendar Related\n4: Medium Dictionaries. Small Rulesets\n5: Small Dictionaries. Medium Rulesets\n6: Medium Dictionaries. Medium Rulesets\n7: Large Password List. Custom Ruleset\n8: Medium-Large Dictionaries. Small Rulesets\n9: Small Dictionaries. Large Rulesets\n10: Medium Dictionaries. Large Rulesets\n11: Medium-Large Dictionaries. Medium Rulesets\n12: Large Dictionaries. Small Rulesets\n13: Medium-Large Dictionaries. Large Rulesets\n14: Large Dictionaries. Medium Rulesets\n15: Large Dictionaries. Large Rulesets\n\n",
                            action='store')
    lArgParser.add_argument('-b', '--brute-force',
                            type=str,
                            help="Bruce force common patterns with at least MIN characters up to MAX characters. Provide minimum and maxiumum number of characters as comma-separated, positive integers (i.e. 4,6 means 4 characters to 6 characters).\n\n",
                            action='store')
    lArgParser.add_argument('-l', '--pathwell',
                            type=str,
                            help="Try common patterns based on pathwell masks. Pathwell masks represent the 50 most common patterns. Use masks number FIRST to LAST. For example, masks 1 thorugh 5. Provide mask numbers as comma-separated, positive integers (i.e. 1,5 means use masks 1-5.\n\n",
                            action='store')
    lArgParser.add_argument('-c', '--jtr-prince',
                            help='Run John the Ripper''s Prince mode. This mode combines words within a dicitonary to generate guesses.',
                            action='store_true')
    lArgParser.add_argument('-r', '--recycle',
                            help='After all cracking attempts are finished, use the root words of already cracked passwords to create a new dictionary. Try to crack more passwords with the new dictionary.',
                            action='store_true')
    lArgParser.add_argument('-s', '--stat-crack',
                            help="Enable statistical cracking. Byepass will run relatively fast cracking strategies in hopes of cracking enough passwords to induce a pattern and create \"high probability\" masks. Byepass will use the masks in an attempt to crack more passwords.\n\n",
                            action='store_true')
    lArgParser.add_argument('-p', '--percentile',
                            type=float,
                            help="Based on statistical analysis of the passwords cracked during initial phase, use only the masks statistically likely to be needed to crack at least the given percent of passwords. For example, if a value of 0.25 provided, only use the relatively few masks needed to crack 25 passwords of the passwords. Note that password cracking effort follows an exponential distribution, so cracking a few more passwords takes a lot more effort (relatively speaking). A good starting value if completely unsure is 25 percent (0.25).\n\n",
                            action='store')
    lArgParser.add_argument('-a', '--all',
                             help="Shortcut equivalent to -w [RUN_ALL_BASEWORDS] -t [RUN_ALL_TECHNIQUES] -l [RUN_ALL_FIRST_PATHWELL_MASK,RUN_ALL_LAST_PATHWELL_MASK] -s -p [RUN_ALL_PERCENTILE] -u -c -r. See config.py for values used.",
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

    run_main_program(pParser=Parser(lArgParser.parse_args(), Config))