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
MAX_CHARS_TO_BRUTEFORCE = 7
