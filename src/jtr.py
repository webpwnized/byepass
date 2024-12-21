import subprocess
import time
from os import path
from printer import Printer, Level

class JohnTheRipper:

    __mJohnExecutableFilePath: str = ""
    __mJohnPotFilePath: str = ""
    __mHashFilePath: str = ""
    __mHashFormat: str = ""
    __mPassThrough: str = ""
    __mWordlist: str = ""
    __mPathToWordlist: str = ""
    __mPrinceElementCountMin: int = 2
    __mPrinceElementCountMax: int = 3
    __mMasksAlreadyBruteForced: list = []
    __mVerbose: bool = False
    __mDebug: bool = False
    __mNumberHashesInHashFile: int = 0
    __mPrinter: Printer = Printer

    READ_BYTES = 'rb'

    @property  # getter method
    def jtr_executable_file_path(self):
        return self.__mJohnExecutableFilePath

    @jtr_executable_file_path.setter  # setter method
    def jtr_executable_file_path(self: object, pJohnExecutableFilePath: str):
        self.__mJohnExecutableFilePath = pJohnExecutableFilePath

    @property  # getter method
    def jtr_pot_file_path(self):
        return self.__mJTRPotFilePath

    @jtr_pot_file_path.setter  # setter method
    def jtr_pot_file_path(self: object, pJTRPotFilePath: str):
        self.__mJTRPotFilePath = pJTRPotFilePath

    @property  # getter method
    def jtr_hash_file_path(self):
        return self.__mHashFilePath

    @jtr_hash_file_path.setter  # setter method
    def jtr_hash_file_path(self: object, pHashFilePath: str):
        self.__mHashFilePath = pHashFilePath
        self.__mNumberHashesInHashFile = self.__count_hashes_in_input_file()

    @property  # getter method
    def hash_format(self):
        return self.__mHashFormat

    @hash_format.setter  # setter method
    def hash_format(self: object, pHashFormat: str):
        self.__mHashFormat = pHashFormat

    @property  # getter method
    def pass_through(self):
        return self.__mPassThrough

    @pass_through.setter  # setter method
    def pass_through(self: object, pPassThrough: str):
        self.__mPassThrough = pPassThrough

    @property  # getter method
    def wordlist(self):
        return self.__mWordlist

    @wordlist.setter  # setter method
    def wordlist(self: object, pWordlist: str):
        self.__mWordlist = pWordlist

    @property  # getter method
    def path_to_wordlist(self):
        return self.__mPathToWordlist

    @path_to_wordlist.setter  # setter method
    def path_to_wordlist(self: object, pPathToWordlist: str):
        self.__mPathToWordlist = pPathToWordlist

    @property  # getter method
    def prince_element_count_min(self):
        return self.__mPrinceElementCountMin

    @prince_element_count_min.setter  # setter method
    def prince_element_count_min(self: object, pPrinceElementCountMin: int):
        self.__mPrinceElementCountMin = pPrinceElementCountMin

    @property  # getter method
    def prince_element_count_max(self):
        return self.__mPrinceElementCountMax

    @prince_element_count_max.setter  # setter method
    def prince_element_count_max(self: object, pPrinceElementCountMax: int):
        self.__mPrinceElementCountMax = pPrinceElementCountMax

    @property  # getter method
    def masks_already_brute_forced(self):
        return self.__mMasksAlreadyBruteForced

    @property  # getter method
    def verbose(self) -> bool:
        return self.__mVerbose

    @verbose.setter  # setter method
    def verbose(self: object, pVerbose: bool) -> None:
        self.__mVerbose = pVerbose
        self.__mPrinter.verbose = pVerbose

    @property  # getter method
    def debug(self) -> bool:
        return self.__mDebug

    @debug.setter  # setter method
    def debug(self: object, pDebug: bool) -> None:
        self.__mDebug = pDebug
        self.__mPrinter.debug = pDebug

    @property  # getter method
    def number_hashes_in_hash_file(self) -> int:
        return self.__mNumberHashesInHashFile

    # Constructor Methods
    def __init__(self: object, pJTRExecutableFilePath: str, pJTRPotFilePath: str,
                 pHashFilePath: str, pHashFormat: str, pPassThrough: str,
                 pVerbose: bool, pDebug: bool) -> None:
        self.__mJohnExecutableFilePath = pJTRExecutableFilePath
        self.__mJTRPotFilePath = pJTRPotFilePath
        self.__mHashFilePath = pHashFilePath
        self.__mHashFormat = pHashFormat
        self.__mPassThrough = pPassThrough
        self.__mVerbose = pVerbose
        self.__mDebug = pDebug
        self.__mNumberHashesInHashFile = self.__count_hashes_in_input_file()
        self.__mPrinter.verbose = pVerbose
        self.__mPrinter.debug = pDebug

    # Private Methods
    def __crack(self, lCmdArgs: list):
        if self.__mHashFormat: lCmdArgs.append("--format={}".format(self.__mHashFormat))
        if self.__mPassThrough: lCmdArgs.append(self.__mPassThrough)
        lCmdArgs.append(self.__mHashFilePath)
        self.__run_jtr(lCmdArgs)

    def __run_jtr(self, lCmdArgs: list):
        # Note: subprocess.run() accepts the command to run as a list of arguments.
        # lCmd is this list.

        lCmd = [self.__mJohnExecutableFilePath]
        lCmd.extend(lCmdArgs)
        self.__mPrinter.print("Running command {}".format(lCmd), Level.INFO)
        lCompletedProcess = subprocess.run(lCmd, stdout=subprocess.PIPE)
        time.sleep(0.5)

    def __estimate_prince_mode(self, pCmdArgs: list) -> None:
        pCmdArgs.append("--prince-keyspace")
        self.__run_jtr(lCmdArgs=pCmdArgs)
        pCmdArgs.remove("--prince-keyspace")

    def __count_hashes_in_input_file(self) -> int:

        lLines: int = 0
        for lLine in open(self.__mHashFilePath):
            lLines += 1
        return lLines

    # Public Methods
    def run_single_crack(self) -> None:
        lCmdArgs = ["--single"]
        self.__crack(lCmdArgs=lCmdArgs)

    # Must stay under 26 bits
    def run_prince_mode(self, pPathToWordlist: str, pWordlist: str,
                        pPrinceElementCountMin: int, pPrinceElementCountMax: int) -> None:
        lCmdArgs = ["--prince={}/{}".format(pPathToWordlist, pWordlist)]
        lCmdArgs.append("--prince-elem-cnt-min={}".format(pPrinceElementCountMin))
        lCmdArgs.append("--prince-elem-cnt-max={}".format(pPrinceElementCountMax))
        if self.__mVerbose: self.__estimate_prince_mode(lCmdArgs)
        lCmdArgs.append("--rule=prince")
        self.__crack(lCmdArgs=lCmdArgs)

    def run_prince_mode(self) -> None:
        lCmdArgs = ["--prince={}/{}".format(self.__mPathToWordlist, self.__mWordlist)]
        lCmdArgs.append("--prince-elem-cnt-min={}".format(self.__mPrinceElementCountMin))
        lCmdArgs.append("--prince-elem-cnt-max={}".format(self.__mPrinceElementCountMax))
        if self.__mVerbose: self.__estimate_prince_mode(lCmdArgs)
        lCmdArgs.append("--rule=prince")
        self.__crack(lCmdArgs=lCmdArgs)

    def run_wordlist_mode(self, pWordlist: str, pRule: str) -> None:
        lCmdArgs = ["--wordlist={}".format(pWordlist)]
        if pRule: lCmdArgs.append("--rule={}".format(pRule))
        self.__crack(lCmdArgs=lCmdArgs)

    def run_mask_mode(self, pMask: str, pWordlist: str, pRule: str) -> None:
        # There are two modes that run brute force using masks. Keep track of masks
        # already checked in case the same mask would be tried twice.
        if pMask in self.__mMasksAlreadyBruteForced:
            self.__mPrinter.print("Mask {} has already been tested in this session. Moving on to next task.".format(pMask), Level.WARNING)
            return None
        else:
            self.__mMasksAlreadyBruteForced.append(pMask)
            lCmdArgs = ["--mask={}".format(pMask)]
            if pWordlist: lCmdArgs.append("--wordlist={}".format(pWordlist))
            if pRule: lCmdArgs.append("--pRule={}".format(pRule))
            self.__crack(lCmdArgs=lCmdArgs)

    def parse_passwords_from_pot(self) -> list:

        lListOfPasswords = []

        self.__mPrinter.print("Reading input file {}".format(self.__mJTRPotFilePath), Level.INFO)

        with open(self.__mJTRPotFilePath, self.READ_BYTES) as lFile:
            lPotFile = lFile.readlines()

        self.__mPrinter.print("Processing input file {}".format(self.__mJTRPotFilePath), Level.INFO)

        for lLine in lPotFile:
            # LANMAN passwords are case-insensitive so they throw off statistical analysis
            # For LANMAN, we assume lowercase (most popular choice) but errors will be inherent
            if not lLine[0:3] == b'$LM':
                lPassword = lLine.strip().split(b':')[1]
            else:
                lPassword = lLine.strip().split(b':')[1].lower()
            lListOfPasswords.append(lPassword)
        self.__mPrinter.print("Finished processing input file {}".format(self.__mJTRPotFilePath), Level.INFO)

        return lListOfPasswords

    def parse_jtr_show(self) -> None:

        lCmd = [self.jtr_executable_file_path]
        lCmd.append("--show")
        if self.__mHashFormat: lCmd.append("--format={}".format(self.__mHashFormat))
        lCmd.append(self.__mHashFilePath)
        lCompletedProcess = subprocess.run(lCmd, stdout=subprocess.PIPE)
        lCrackedPasswords = lCompletedProcess.stdout.split(b'\n')
        for lCrackedPassword in lCrackedPasswords:
            try:
                print(lCrackedPassword.decode("utf-8"))
            except:
                pass

    def count_passwords_in_pot(self) -> int:

        lLines = 0
        try:
            if path.exists(self.__mJTRPotFilePath):
                for lLine in open(self.__mJTRPotFilePath):
                    lLines += 1
        except:
            lLines = 0
        return lLines

    def rm_pot_file(self) -> None:

        if path.exists(self.__mJTRPotFilePath):
            lCompletedProcess = subprocess.run(["rm", self.__mJTRPotFilePath], stdout=subprocess.PIPE)
            self.__mPrinter.print("Deleted file {}".format(self.__mJTRPotFilePath), Level.WARNING)
            time.sleep(0.5)