from enum import Enum

class Level(Enum):
    INFO = 0
    WARNING = 1
    ERROR = 2
    SUCCESS = 3
    DEBUG = 4

class Printer:

    __grey = 37
    __red = 91
    __green = 92
    __yellow = 93
    __blue = 94
    __magenta = 95
    __cyan = 96
    __white = 97
    __bold = "\033[1m"
    __not_bold = "\033[21m"
    __mVerbose: bool = False
    __mDebug: bool = False
    __mColorMap = {
        Level.INFO: __white,
        Level.WARNING: __yellow,
        Level.ERROR: __red,
        Level.SUCCESS: __green,
        Level.DEBUG: __cyan
    }
    __mLevelMap = {
        Level.INFO: "[*] INFO: ",
        Level.WARNING: "[*] WARNING: ",
        Level.ERROR: "[*] ERROR: ",
        Level.SUCCESS: "[*] SUCCESS: ",
        Level.DEBUG: "[*] DEBUG: "
    }

    @property  # getter method
    def verbose(self) -> bool:
        return self.__mVerbose

    @verbose.setter  # setter method
    def verbose(self: object, pVerbose: bool):
        self.__mVerbose = pVerbose

    @property  # getter method
    def debug(self) -> bool:
        return self.__mDebug

    @debug.setter  # setter method
    def debug(self: object, pDebug: bool):
        self.__mDebug = pDebug

    # Default Constructor Method
    def __init__(self) -> None:
        self.__mVerbose: bool = False
        self.__mDebug: bool = False

    # private methods

    # public method
    def print(self, pMessage: str, pLevel: Level) -> None:
        # Only print INFO and SUCCESS messages if verbose is true
        # Only print DEBUG messages if debug is true
        # Warning, Error are always printed
        if (pLevel in [Level.INFO, Level.SUCCESS]) and not self.verbose: return None
        if (pLevel in [Level.DEBUG]) and not self.debug: return None
        print("\033[1;{}m{}{}\033[21;0m".format(self.__mColorMap[pLevel], self.__mLevelMap[pLevel], pMessage))

    def print_example_usage(self):
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