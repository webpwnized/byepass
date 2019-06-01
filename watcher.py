import time
from os import path
import subprocess

class Watcher:

    # Private Attributes
    __mStartTime = 0.0
    __mStopTime = 0.0
    __mRunTime = 0.0
    __mCrackingMode = ""
    __mVerbose = False
    __mDebug = False
    __mNumberHashes = 0
    __mJTRPotFilePath = ""
    __mNumberPasswordsCrackedBefore = 0
    __mNumberPasswordsCrackedAfter = 0
    __mNumberPasswordsCrackedByThisMode = 0
    __mNumberPasswordsCrackedByThisModePerSecond = 0
    __mPercentPasswordsCrackedByThisMode = 0.0

    @property           # getter method
    def start_time(self):
        return self.__mStartTime

    @property           # getter method
    def stop_time(self):
        return self.__mStopTime

    @stop_time.setter  # setter method
    def stop_time(self: object, pStopTime: float):
        self.__mStopTime = pStopTime

    @property  # getter method
    def run_time(self):
        return self.__mRunTime

    @property           # getter method
    def cracking_mode(self):
        return self.__cracking_mode

    @cracking_mode.setter  # setter method
    def cracking_mode(self: object, pMode: str):
        self.__cracking_mode = pMode

    @property  # getter method
    def number_hashes(self):
        return self.__mNumberHashes

    @number_hashes.setter  # setter method
    def number_hashes(self: object, pNumberHashes: int):
        self.__mNumberHashes = pNumberHashes

    @property           # getter method
    def verbose(self):
        return self.__mVerbose

    @verbose.setter  # setter method
    def verbose(self: object, pVerbose: bool):
        self.__mVerbose = pVerbose

    @property  # getter method
    def debug(self):
        return self.__mDebug

    @debug.setter  # setter method
    def debug(self: object, pDebug: bool):
        self.__mDebug = pDebug

    @property  # getter method
    def jtr_pot_file_path(self):
        return self.__mJTRPotFilePath

    @jtr_pot_file_path.setter  # setter method
    def jtr_pot_file_path(self: object, pJTRPotFilePath: str):
        self.__mJTRPotFilePath = pJTRPotFilePath

    @property  # getter method
    def number_passwords_cracked_before(self):
        return self.__mNumberPasswordsCrackedBefore

    @property  # getter method
    def number_passwords_cracked_after(self):
        return self.__mNumberPasswordsCrackedAfter

    @property  # getter method
    def number_passwords_cracked_by_this_mode(self):
        return self.__mNumberPasswordsCrackedByThisMode

    @property  # getter method
    def number_passwords_cracked_by_this_mode_per_second(self):
        return self.__mNumberPasswordsCrackedByThisModePerSecond

    @property  # getter method
    def percent_passwords_cracked_by_this_mode(self):
        return self.__mPercentPasswordsCrackedByThisMode

    # Constructor Methods
    def __init__(self: object, pCrackingMode: str, pVerbose: bool, pDebug: bool, pNumberHashes: int, pJTRPotFilePath: str) -> None:
        self.__mCrackingMode = pCrackingMode
        self.__mNumberHashes = pNumberHashes
        self.__mVerbose = pVerbose
        self.__mDebug = pDebug
        self.__mJTRPotFilePath = pJTRPotFilePath

    # Private methods
    def __count_passwords_in_jtr_pot_file(self) -> int:

        lLines = 0
        try:
            if path.exists(self.__mJTRPotFilePath):
                for lLine in open(self.__mJTRPotFilePath):
                    lLines += 1
        except:
            lLines = 0

        return lLines

    def __rm_jtr_pot_file(self) -> None:

        if path.exists(self.__mJTRPotFilePath):
            lCompletedProcess = subprocess.run(["rm", self.__mJTRPotFilePath], stdout=subprocess.PIPE)
            print("[*] Deleted file {}".format(self.__mJTRPotFilePath))
            time.sleep(0.5)

    # Public methods
    def start_timer(self) -> None:
        if self.__mDebug: self.__rm_jtr_pot_file()
        self.__mStartTime = time.time()
        self.__mNumberPasswordsCrackedBefore = self.__count_passwords_in_jtr_pot_file()

    # Public methods
    def stop_timer(self) -> None:
        self.__mStopTime = time.time()
        self.__mRunTime = self.__mStopTime - self.__mStartTime
        self.__mNumberPasswordsCrackedAfter = self.__count_passwords_in_jtr_pot_file()
        self.__mNumberPasswordsCrackedByThisMode = self.__mNumberPasswordsCrackedAfter - self.__mNumberPasswordsCrackedBefore
        self.__mPercentPasswordsCrackedByThisMode = round(self.__mNumberPasswordsCrackedByThisMode / self.__mNumberHashes * 100, 2)
        self.__mNumberPasswordsCrackedByThisModePerSecond = self.__mNumberPasswordsCrackedByThisMode // self.__mRunTime

    def print_mode_start_message(self) -> None:
        if self.__mVerbose:
            print("[*] Starting mode: {}".format(self.__mCrackingMode))
            print("[*] Passwords cracked before {} mode: {}".format(self.__mCrackingMode, self.__mNumberPasswordsCrackedBefore))

    def print_mode_finsihed_message(self) -> None:
        if self.__mVerbose:
            print("[*] Finished {} mode".format(self.__mCrackingMode))

        print("[*] Passwords cracked by mode: {} ({} percent)".format(self.__mNumberPasswordsCrackedByThisMode,
                                                                      self.__mPercentPasswordsCrackedByThisMode))
        if self.__mDebug:
            print("\tDuration: {}".format(self.__mRunTime))
            print("\tPasswords cracked per second: {}".format(self.__mNumberPasswordsCrackedByThisModePerSecond))