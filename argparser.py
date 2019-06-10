from printer import Printer, Level
import config as Config

class Parser:

    __mArgs = None
    __mConfiguration: Config = None
    __mDebug: bool = False
    __mVerbose: bool = False
    __mHashFormat: str = ""
    __mHashFile: str = ""
    __mJTRPassThrough: str = ""
    __mRunStatCrack: bool = False
    __mRunJTRSingleCrack: bool = False
    __mRecylePasswords: bool = False
    __mRunJTRPrinceMode: bool = False
    __mRunDefaultTechniques: bool = False
    __mRunBruteForce: bool = False
    __mRunBasewordsMode: bool = False
    __mShowExamples: bool = False
    __mPercentile: float = None
    __mBaseWords: list = None
    __mTechniques: list = None
    __mMinCharactersToBruteForce: int = 0
    __mMaxCharactersToBruteForce: int = 0
    __mPrinter: Printer = Printer()

    @property  # getter method
    def show_examples(self) -> bool:
        return self.__mShowExamples

    @property  # getter method
    def debug(self) -> bool:
        return self.__mDebug

    @debug.setter  # setter method
    def debug(self: object, pDebug: bool) -> None:
        self.__mDebug = pDebug
        self.__mPrinter.debug = pDebug

    @property  # getter method
    def verbose(self) -> bool:
        return self.__mVerbose

    @verbose.setter  # setter method
    def verbose(self: object, pVerbose: bool) -> None:
        self.__mVerbose = pVerbose
        self.__mPrinter.verbose = pVerbose

    @property  # getter method
    def run_stat_crack(self) -> bool:
        return self.__mRunStatCrack

    @property  # getter method
    def run_jtr_single_crack(self) -> bool:
        return self.__mRunJTRSingleCrack

    @property  # getter method
    def run_jtr_prince_mode(self) -> bool:
        return self.__mRunJTRPrinceMode

    @property  # getter method
    def percentile(self) -> float:
        return self.__mPercentile

    @property  # getter method
    def hash_format(self) -> str:
        return self.__mHashFormat

    @property  # getter method
    def hash_file(self) -> str:
        return self.__mHashFile

    @property  # getter method
    def basewords(self) -> list:
        return self.__mBaseWords

    @property  # getter method
    def techniques(self) -> list:
        return self.__mTechniques

    @property  # getter method
    def min_characters_to_brute_force(self) -> int:
        return self.__mMinCharactersToBruteForce

    @property  # getter method
    def max_characters_to_brute_force(self) -> int:
        return self.__mMaxCharactersToBruteForce

    @property  # getter method
    def recycle_passwords(self) -> bool:
        return self.__mRecylePasswords

    @property  # getter method
    def jtr_pass_through(self) -> str:
        return self.__mJTRPassThrough

    @property  # getter method
    def run_default_techniques(self) -> bool:
        return self.__mRunDefaultTechniques

    @property  # getter method
    def run_brute_force(self) -> bool:
        return self.__mRunBruteForce

    @property  # getter method
    def run_basewords_mode(self) -> bool:
        return self.__mRunBasewordsMode

    # Constructor Method
    def __init__(self: object, pArgs, pConfig: Config) -> None:
        self.__mArgs = pArgs
        self.__mConfiguration = pConfig
        self.__mVerbose = self.__mArgs.verbose
        self.__parse_arg_debug()
        self.__mShowExamples = self.__mArgs.examples
        self.__parse_arg_hash_format()
        self.__parse_arg_techniques()
        self.__parse_arg_brute_force()
        self.__mPrinter.verbose = self.__mVerbose
        self.__mPrinter.debug = self.__mDebug
        self.__mRunJTRSingleCrack = self.__mArgs.jtr_single_crack
        self.__mRunJTRPrinceMode = self.__mArgs.jtr_prince
        self.__mParseBasewords()
        self.__mHashFile = self.__mArgs.input_file
        self.__mRecylePasswords = self.__mArgs.recycle
        self.__mJTRPassThrough = self.__mArgs.pass_through

        # Input parameter validation
        if self.__mArgs.percentile and not self.__mArgs.stat_crack:
            self.__mPrinter.print(
                            "Argument 'percentile' provided without argument 'stat_crack'. Percentile will be ignored",
                            Level.WARNING)

        self.__mRunStatCrack = self.__mArgs.stat_crack
        self.__parse_arg_percentile()

        if self.__mArgs.all:
            self.__mTechniques = self.__mConfiguration.RUN_ALL_TECHNIQUES
            self.__mRunJTRSingleCrack = self.__mConfiguration.RUN_ALL_RUN_SINGLE_CRACK
            self.__mRunJTRPrinceMode = self.__mConfiguration.RUN_ALL_RUN_PRINCE_MODE
            self.__mRecylePasswords = self.__mConfiguration.RUN_ALL_RUN_RECYCLE_MODE
            self.__mRunStatCrack = self.__mConfiguration.RUN_ALL_RUN_STAT_CRACK
            self.__mPercentile = self.__mConfiguration.RUN_ALL_PERCENTILE
            self.__mRunBasewordsMode = self.__mConfiguration.RUN_ALL_RUN_BASEWORDS_MODE
            self.__mBaseWords = self.__mConfiguration.RUN_ALL_BASEWORDS

        self.__mRunDefaultTechniques = not self.__mRunJTRSingleCrack and not self.__mBaseWords and \
                                    not self.__mArgs.brute_force and not self.__mTechniques and \
                                    not self.__mRunStatCrack and not self.__mRecylePasswords and \
                                    not self.__mRunJTRPrinceMode

        # If user did not specify any technique, run default technique 1,2 and 3 by default
        if self.__mRunDefaultTechniques:
            self.__mTechniques = self.__mConfiguration.DEFAULT_TECHNIQUES
            self.__mPrinter.print("No technique specified. Using default techniques {}".format(self.__mTechniques), Level.WARNING)

    # private methods
    def __mParseBasewords(self):
        if self.__mArgs.basewords:
            lErrorMessage = 'Basewords must be supplied as a comma-separated list of words'

            try:
                self.__mBaseWords = list(self.__mArgs.basewords.split(","))
                self.__mRunBasewordsMode = True
            except:
                raise ValueError(lErrorMessage)

    def __parse_arg_percentile(self) -> None:

        if self.__mArgs.percentile:
            if not 0.0 <= self.__mArgs.percentile <= 1.00:
                raise ValueError('The percentile provided must be between 0.0 and 1.0.')
            self.__mPercentile = self.__mArgs.percentile
        else:
            self.__mPercentile = 1.0

    def __parse_arg_debug(self) -> None:
        if self.__mArgs.debug:
            self.__mDebug = self.__mArgs.debug
        else:
            self.__mDebug = self.__mConfiguration.DEBUG

    def __parse_arg_hash_format(self) -> str:
        if self.__mArgs.hash_format is not None:
            self.__mHashFormat = self.__mArgs.hash_format
        else:
            self.__mHashFormat = ""

    def __parse_arg_techniques(self) -> None:
        lTechniques = []

        if self.__mArgs.techniques is not None:

            lErrorMessage = 'Techniques must be supplied as a comma-separated list of integers between 0 and 15'

            try:
                lTechniques = list(map(int, self.__mArgs.techniques.split(",")))
            except:
                raise ValueError(lErrorMessage)

            lObservedTechniques = []
            for lTechnique in lTechniques:
                if 0 <= lTechnique <= 15:
                    if lTechnique in lObservedTechniques:
                        raise ValueError('Duplicate technique specified: {} '.format(lTechnique) + lErrorMessage)
                    lObservedTechniques.append(lTechnique)
                else:
                    raise ValueError(lErrorMessage)

            lTechniques.sort()

        self.__mTechniques = lTechniques

    def __parse_arg_brute_force(self) -> None:

        lSyntaxErrorMessage = 'Amount of characters to bruce-force must be a comma-separated pair of positive integer greater than 0. The MIN must be less than or equal to the MAX.'
        lValueErrorMessage = 'For amount of characters to bruce-force, the MIN must be less than or equal to the MAX.'

        try:
            if self.__mArgs.brute_force:
                lParameters = [x.strip() for x in self.__mArgs.brute_force.split(',')]
                lMinCharactersToBruteForce = int(lParameters[0])
                lMaxCharactersToBruteForce = int(lParameters[1])

                if lMinCharactersToBruteForce < 1:
                    raise ValueError(lSyntaxErrorMessage)
                if lMaxCharactersToBruteForce < 1:
                    raise ValueError(lSyntaxErrorMessage)
                if lMaxCharactersToBruteForce < lMinCharactersToBruteForce:
                    raise ValueError(lValueErrorMessage)
                self.__mRunBruteForce = True
                self.__mMinCharactersToBruteForce = lMinCharactersToBruteForce
                self.__mMaxCharactersToBruteForce = lMaxCharactersToBruteForce
            else:
                self.__mRunBruteForce = False
                self.__mMinCharactersToBruteForce = 0
                self.__mMaxCharactersToBruteForce = 0
        except:
            raise ValueError(lSyntaxErrorMessage)
