# Default values when john compiled in /opt
# This should be the correct values if John is installed as expected
#JTR_EXECUTABLE_FILE_PATH = "/opt/JohnTheRipper/run/john"
#JTR_POT_FILE_PATH = "/opt/JohnTheRipper/run/john.pot"

# Default values for Kali Linux Rolling 2018
# NOTE: You should install the latest version of JTR.
# A video tutorial is available at https://www.youtube.com/watch?v=7R10QN_uCh0
#JTR_EXECUTABLE_FILE_PATH = "/usr/sbin/john"
#JTR_POT_FILE_PATH = "/root/.john/john.pot"

# Example of john being installed in a custom directory
JTR_EXECUTABLE_FILE_PATH = "/opt/john/run/john"
JTR_POT_FILE_PATH = "/opt/john/run/john.pot"

DEBUG = False
