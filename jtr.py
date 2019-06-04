import subprocess
import time
from os import path

class JohnTheRipper:

    __mJohnExecutableFilePath = ""
    __mJohnPotFilePath = ""
    __mHashFilePath = ""
    __mHashFormat = ""
    __mPassThrough = ""

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
        if self.__mVerbose: print("[*] Running command {}".format(lCmd))
        lCompletedProcess = subprocess.run(lCmd, stdout=subprocess.PIPE)
        time.sleep(0.5)

    # Public Methods
    def run_single_crack(self) -> None:
        lCmdArgs = ["--single"]
        self.__crack(lCmdArgs=lCmdArgs)

    def run_prince_mode(self) -> None:
        lCmdArgs = ["--prince=dictionaries/prince.txt"]
        lCmdArgs.append("--rule=Best126")
        lCmdArgs.append("--prince-wl-max=16")
        lCmdArgs.append("--prince-case-permute")
        # lCmdArgs.append("--prince-wl-dist-len")
        self.__crack(lCmdArgs=lCmdArgs)

    def estimate_prince_mode(self) -> None:
        lCmdArgs = ["--prince=dictionaries/prince.txt"]
        lCmdArgs.append("--prince-wl-max=16")
        lCmdArgs.append("--prince-case-permute")
        # lCmdArgs.append("--prince-wl-dist-len")
        lCmdArgs.append("--prince-keyspace")
        self.__run_jtr(lCmdArgs=lCmdArgs)

    def run_wordlist_mode(self, pWordlist: str, pRule: str) -> None:
        lCmdArgs = ["--wordlist={}".format(pWordlist)]
        if pRule: lCmdArgs.append("--rule={}".format(pRule))
        self.__crack(lCmdArgs=lCmdArgs)

    def run_mask_mode(self, pMask: str, pWordlist: str) -> None:
        lCmdArgs = ["--mask={}".format(pMask)]
        if pWordlist: lCmdArgs.append("--wordlist={}".format(pWordlist))
        self.__crack(lCmdArgs=lCmdArgs)

    def parse_passwords_from_pot(self) -> list:

        lListOfPasswords = []

        if self.__mVerbose: print("[*] Reading input file {}".format(self.__mJTRPotFilePath))

        with open(self.__mJTRPotFilePath, self.READ_BYTES) as lFile:
            lPotFile = lFile.readlines()

        if self.__mVerbose: print("[*] Processing input file {}".format(self.__mJTRPotFilePath))

        for lLine in lPotFile:
            # LANMAN passwords are case-insensitive so they throw off statistical analysis
            # For LANMAN, we assume lowercase (most popular choice) but errors will be inherent
            if not lLine[0:3] == b'$LM':
                lPassword = lLine.strip().split(b':')[1]
            else:
                lPassword = lLine.strip().split(b':')[1].lower()
            lListOfPasswords.append(lPassword)
        if self.__mVerbose: print("[*] Finished processing input file {}".format(self.__mJTRPotFilePath))

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
