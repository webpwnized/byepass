# Default values when john compiled in /opt
# This should be the correct values if John is installed as expected
JTR_EXECUTABLE_FILE_PATH = "/opt/JohnTheRipper/run/john"
JTR_POT_FILE_PATH = "/opt/JohnTheRipper/run/john.pot"

# Default values for Kali Linux Rolling 2018
# NOTE: You should install the latest version of JTR.
# A video tutorial is available at https://www.youtube.com/watch?v=7R10QN_uCh0
#JTR_EXECUTABLE_FILE_PATH = "/usr/sbin/john"
#JTR_POT_FILE_PATH = "/root/.john/john.pot"

# Example of john being installed in a custom directory
#JTR_EXECUTABLE_FILE_PATH = "/opt/john/run/john"
#JTR_POT_FILE_PATH = "/opt/john/run/john.pot"

DEBUG = False

# For the statistical cracking mode, MAX_CHARS_TO_BRUTEFORCE decides
# whether ByePass will brute-force all possible values or use
# "smart brute" mode which is a hybrid cracking mode that uses
# dicitionary words as the basis for mask cracking.
MAX_CHARS_TO_BRUTEFORCE = 6

# If the user does not provide any instructions, these techniques run by default
DEFAULT_TECHNIQUES = [7]

# If the user chooses the "all" option, these defaults are used
RUN_ALL_RUN_HAILMARY_MODE = True
RUN_ALL_RUN_SINGLE_CRACK = True
RUN_ALL_RUN_PRINCE_MODE = True
RUN_ALL_RUN_RECYCLE_MODE = True
RUN_ALL_RUN_STAT_CRACK = True
RUN_ALL_RUN_BASEWORDS_MODE = True
RUN_ALL_RUN_PATHWELL_MODE = True
RUN_ALL_TECHNIQUES = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
RUN_ALL_PERCENTILE = 0.90
RUN_ALL_FIRST_PATHWELL_MASK = 1
RUN_ALL_LAST_PATHWELL_MASK = 50
RUN_ALL_BASEWORDS = ["love", "alex", "mike", "angel", "blue", "chris", "password", "sunshine", "qwerty", "iloveyou",
                     "princess", "admin", "welcome", "football", "monkey", "july", "june", "march", "april",
                     "jan", "feb", "mar", "apr", "may", "aug", "sept", "oct", "nov", "dec"]
