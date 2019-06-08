import time
from os import path
import subprocess
from printer import Printer, Level
from jtr import JohnTheRipper

class Watcher:

    # Private Attributes
    __mStartTime = 0.0
    __mStopTime = 0.0
    __mRunTime = 0.0
    __mCrackingMode = ""
    __mNumberPasswordsCrackedBefore = 0
    __mNumberPasswordsCrackedAfter = 0
    __mNumberPasswordsCrackedByThisMode = 0
    __mNumberPasswordsCrackedByThisModePerSecond = 0
    __mPercentPasswordsCrackedByThisMode = 0.0
    __mPrinter: Printer = Printer()
    __mJTR: JohnTheRipper = None

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

    @property  # getter method
    def jtr(self):
        return self.__mJTR

    @jtr.setter  # setter method
    def jtr(self: object, pJTR: JohnTheRipper):
        self.__mJTR = pJTR

    # Constructor Methods
    def __init__(self: object, pJTR: JohnTheRipper, pCrackingMode: str) -> None:
        self.__mCrackingMode = pCrackingMode
        self.__mJTR = pJTR
        self.__mPrinter.verbose = pJTR.verbose
        self.__mPrinter.debug = pJTR.debug

    # Public methods
    def start_timer(self) -> None:
        if self.__mJTR.debug: self.__mJTR.rm_pot_file()
        self.__mStartTime = time.time()
        self.__mNumberPasswordsCrackedBefore = self.__mJTR.count_passwords_in_pot()

    # Public methods
    def stop_timer(self) -> None:
        self.__mStopTime = time.time()
        self.__mRunTime = self.__mStopTime - self.__mStartTime
        self.__mNumberPasswordsCrackedAfter = self.__mJTR.count_passwords_in_pot()
        self.__mNumberPasswordsCrackedByThisMode = self.__mNumberPasswordsCrackedAfter - self.__mNumberPasswordsCrackedBefore
        self.__mPercentPasswordsCrackedByThisMode = round(self.__mNumberPasswordsCrackedByThisMode / self.__mJTR.number_hashes_in_hash_file * 100, 2)
        self.__mNumberPasswordsCrackedByThisModePerSecond = self.__mNumberPasswordsCrackedByThisMode // self.__mRunTime

    def print_mode_start_message(self) -> None:
        self.__mPrinter.print("Starting mode: {}".format(self.__mCrackingMode), Level.INFO)
        self.__mPrinter.print("Passwords cracked before {} mode: {}".format(self.__mCrackingMode, self.__mNumberPasswordsCrackedBefore), Level.INFO)

    def print_mode_finsihed_message(self) -> None:
        self.__mPrinter.print("Finished {} mode".format(self.__mCrackingMode), Level.SUCCESS)

        lLevel = Level.SUCCESS if self.__mNumberPasswordsCrackedByThisMode else Level.WARNING
        self.__mPrinter.print("Passwords cracked by mode: {} ({} percent)".format(self.__mNumberPasswordsCrackedByThisMode,
                                                                      self.__mPercentPasswordsCrackedByThisMode), lLevel)
        self.__mPrinter.print("Duration: {}".format(self.__mRunTime), Level.DEBUG)
        self.__mPrinter.print("Passwords cracked per second: {}".format(self.__mNumberPasswordsCrackedByThisModePerSecond), Level.DEBUG)