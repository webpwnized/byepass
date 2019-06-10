import time
import datetime
from printer import Printer, Level
from jtr import JohnTheRipper
from reporter import Reporter

class Watcher:

    # Private Attributes
    __mStartTime: time = None
    __mStopTime: time = None
    __mRunTime: time = None
    __mCrackingMode:str = ""
    __mNumberPasswordsCrackedBefore:int = 0
    __mNumberPasswordsCrackedAfter:int = 0
    __mNumberPasswordsCrackedByThisMode:int = 0
    __mNumberPasswordsCrackedByThisModePerSecond:int = 0
    __mPercentPasswordsCrackedByThisMode:int = 0.0
    __mPrinter: Printer = Printer()
    __mJTR: JohnTheRipper = None

    @property           # getter method
    def start_time(self) -> time:
        return self.__mStartTime

    @property           # getter method
    def stop_time(self) -> time:
        return self.__mStopTime

    @stop_time.setter  # setter method
    def stop_time(self: object, pStopTime: float):
        self.__mStopTime = pStopTime

    @property  # getter method
    def run_time(self) -> time:
        return self.__mRunTime

    @property           # getter method
    def cracking_mode(self) -> str:
        return self.__cracking_mode

    @cracking_mode.setter  # setter method
    def cracking_mode(self: object, pMode: str) -> None:
        self.__cracking_mode = pMode

    @property  # getter method
    def number_passwords_cracked_before(self) -> int:
        return self.__mNumberPasswordsCrackedBefore

    @property  # getter method
    def number_passwords_cracked_after(self) -> int:
        return self.__mNumberPasswordsCrackedAfter

    @property  # getter method
    def number_passwords_cracked_by_this_mode(self) -> int:
        return self.__mNumberPasswordsCrackedByThisMode

    @property  # getter method
    def number_passwords_cracked_by_this_mode_per_second(self) -> int:
        return self.__mNumberPasswordsCrackedByThisModePerSecond

    @property  # getter method
    def percent_passwords_cracked_by_this_mode(self) -> float:
        return self.__mPercentPasswordsCrackedByThisMode

    @property  # getter method
    def jtr(self) -> JohnTheRipper:
        return self.__mJTR

    @jtr.setter  # setter method
    def jtr(self: object, pJTR: JohnTheRipper) -> None:
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
        self.__mPrinter.print("Duration: {}".format(str(datetime.timedelta(seconds=int(self.run_time)))), Level.DEBUG)
        self.__mPrinter.print("Passwords cracked per second: {}".format(self.__mNumberPasswordsCrackedByThisModePerSecond), Level.DEBUG)

    def print_program_starting_message(self) -> None:
        self.__mPrinter.print(
            "Working on input file {} ({} lines)".format(self.jtr.jtr_hash_file_path, self.jtr.number_hashes_in_hash_file),
            Level.INFO)

    def print_program_finsihed_message(self, pReporter:Reporter) -> None:
        
        print("")
        self.__mPrinter.print("Techniques Attempted", Level.INFO)
        pReporter.reportResults()
        print("")
        self.__mPrinter.print("Duration: {}".format(str(datetime.timedelta(seconds=int(self.run_time)))), Level.INFO)
        self.__mPrinter.print("Passwords cracked (estimated): {} out of {} ({}%)".format(self.number_passwords_cracked_by_this_mode, self.jtr.number_hashes_in_hash_file, self.percent_passwords_cracked_by_this_mode), Level.INFO)
        self.__mPrinter.print("Passwords cracked per second (estimated): {}".format(self.number_passwords_cracked_by_this_mode_per_second), Level.INFO)
        print("")
        self.__mPrinter.print("Cracking attempt complete. Use john --show to see cracked passwords.", Level.INFO)
        self.__mPrinter.print("The command should be something like {}{}{} --show {}".format(self.jtr.jtr_executable_file_path, " --format=" if self.jtr.hash_format else "", self.jtr.hash_format, self.jtr.jtr_hash_file_path), Level.INFO)
        print("")
        self.__mPrinter.print("Keep cracking with incremental mode", Level.INFO)
        self.__mPrinter.print("The command should be something like {}{}{} --incremental {}".format(self.jtr.jtr_executable_file_path, " --format=" if self.jtr.hash_format else "", self.jtr.hash_format, self.jtr.jtr_hash_file_path), Level.INFO)
        print("")
