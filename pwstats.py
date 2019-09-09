# Leaked password lists: https://wiki.skullsecurity.org/Passwords
# Reference for test files: https://github.com/danielmiessler/SecLists/tree/master/Passwords
# JTR Cheatsheet: https://countuponsecurity.files.wordpress.com/2016/09/jtr-cheat-sheet.pdf
# JTR Mask Mode: https://github.com/magnumripper/JohnTheRipper/blob/bleeding-jumbo/doc/MASK

# - Static letters.
# - Ranges in [aouei] or [a-z] syntax. Or both, [0-9abcdef] is the same as
#      [0-9a-f].
# - Placeholders that are just a short form for ranges, like ?l which is
#      100% equivalent to [a-z].
# - ?l lower-case ASCII letters
# - ?u upper-case ASCII letters
# - ?d digits
# - ?s specials (all printable ASCII characters not in ?l, ?u or ?d)
# - ?a full 'printable' ASCII. Note that for formats that don't recognize case
#      (eg. LM), this only includes lower-case characters which is a tremendous
#      reduction of keyspace for the win.
# - ?B all 8-bit (0x80-0xff)
# - ?b all (0x01-0xff) (the NULL character is currently not supported by core).
# - ?h lower-case HEX digits (0-9, a-f)
# - ?H upper-case HEX digits (0-9, A-F)
# - ?L lower-case non-ASCII letters
# - ?U upper-case non-ASCII letters
# - ?D non-ASCII "digits"
# - ?S non-ASCII "specials"
# - ?A all valid characters in the current code page (including ASCII). Note
#      that for formats that don't recognize case (eg. LM), this only includes
#      lower-case characters which is a tremendous reduction of keyspace.
# - Placeholders that are custom defined, so we can e.g. define ?1 to mean [?u?l]
#   ?1 .. ?9 user-defined place-holder 1 .. 9
# - Placeholders for Hybrid Mask mode:
#   ?w is a placeholder for the original word produced by the parent mode in
#      Hybrid Mask mode.
#   ?W is just like ?w except the original word is case toggled (so PassWord
#      becomes pASSwORD).

from collections import OrderedDict
import math

class PasswordMask:

    # Private Attributes
    __mMask = ""
    __mOrdinalPosition = 0
    __mCountPasswordsRepresented = 0
    __mMarginalPercentilePasswordsRepresented = 0.0
    __mCumulativePercentilePasswordsRepresented = 0.0
    __mPrettyMarginalPercentilePasswordsRepresented = "0.0"
    __mPrettyCumulativePercentilePasswordsRepresented = "0.0"

    # Public Properties
    @property
    def mask(self: object) -> str:
        return self.__mMask

    @mask.setter
    def mask(self: object, pMask: str) -> None:
        self.__mMask = pMask

    @property
    def oridinal_position(self: object) -> int:
        return self.__mOrdinalPosition

    @oridinal_position.setter
    def oridinal_position(self: object, pOrdinalPosition: int) -> None:
        self.__mOrdinalPosition = pOrdinalPosition

    @property
    def count_passwords_represented(self: object) -> int:
        return self.__mCountPasswordsRepresented

    @count_passwords_represented.setter
    def count_passwords_represented(self: object, pCountPasswordsRepresented: int) -> None:
        self.__mCountPasswordsRepresented = pCountPasswordsRepresented

    @property
    def marginal_percentile(self: object) -> float:
        return self.__mMarginalPercentilePasswordsRepresented

    @marginal_percentile.setter
    def marginal_percentile(self: object, pMarginalPercentilePasswordsRepresented: float) -> None:
        self.__mMarginalPercentilePasswordsRepresented = pMarginalPercentilePasswordsRepresented

    @property
    def cumulative_percentile(self: object) -> float:
        return self.__mCumulativePercentilePasswordsRepresented

    @cumulative_percentile.setter
    def cumulative_percentile(self: object, pCumulativePercentilePasswordsRepresented: float) -> None:
        self.__mCumulativePercentilePasswordsRepresented = pCumulativePercentilePasswordsRepresented

    @property
    def pretty_marginal_percentile(self: object) -> float:
        return self.__mPrettyMarginalPercentilePasswordsRepresented

    @pretty_marginal_percentile.setter
    def pretty_marginal_percentile(self: object, pPrettyMarginalPercentilePasswordsRepresented: float) -> None:
        self.__mPrettyMarginalPercentilePasswordsRepresented = pPrettyMarginalPercentilePasswordsRepresented

    @property
    def pretty_cumulative_percentile(self: object) -> float:
        return self.__mPrettyCumulativePercentilePasswordsRepresented

    @pretty_cumulative_percentile.setter
    def pretty_cumulative_percentile(self: object, pPrettyCumulativePercentilePasswordsRepresented: float) -> None:
        self.__mPrettyCumulativePercentilePasswordsRepresented = pPrettyCumulativePercentilePasswordsRepresented

class PasswordMasks:

    # Private Attributes
    __mMasksWithStats = []
    __mJustMasks = []
    __mCountPasswordsRepresented = 0

    @property
    def masks_with_stats(self: object) -> list:
        return self.__mMasksWithStats

    @masks_with_stats.setter
    def masks_with_stats(self: object, pMasksWithStats: list) -> None:

        self.__mMasksWithStats = pMasksWithStats

        self.__mJustMasks.clear()
        for lMask in self.__mMasksWithStats:
            self.__mJustMasks.append(lMask.mask)

    @property
    def masks(self: object) -> list:
        return self.__mJustMasks

    @property
    def populated(self: object) -> bool:
        return bool(self.__mMasksWithStats)

    @property
    def count(self: object) -> int:
        return self.__mJustMasks.__len__()

    @property
    def count_passwords_represented(self: object) -> int:
        return self.__mCountPasswordsRepresented

    @count_passwords_represented.setter
    def count_passwords_represented(self: object, pCount: int) -> None:
        self.__mCountPasswordsRepresented = pCount

    def clear(self: object) -> None:
        self.__mMasksWithStats.clear()
        self.__mJustMasks.clear()


class PasswordStats:

    # Private Constants
    __ASCII_LOWERCASE_A = 97
    __ASCII_LOWERCASE_Z = 122
    __ASCII_UPPERCASE_A = 65
    __ASCII_UPPERCASE_Z = 90
    __ASCII_ZERO = 48
    __ASCII_NINE = 57
    __ASCII_SPACE = 32
    __ASCII_FORWARD_SLASH = 47
    __ASCII_COLON = 58
    __ASCII_AMPERSAND = 64
    __ASCII_LEFT_BRACKET = 91
    __ASCII_BACKTICK = 96
    __ASCII_LEFT_CURLY_BRACE = 123
    __ASCII_FORM_FEED = 255
    __ASCII_CARRIAGE_RETURN_LINE_FEED = b'\r\n'

    # Private Attributes
    # Note: Every password produces one mask, so the count of passwords is the count of masks.
    # This fact comes in handy when calculating basic stats.
    __mCharacterClasses = {}
    __mListOfPasswords = []
    __mPasswordMasks = PasswordMasks()

    # Constructor Methods
    def __init__(self: object, pListOfPasswords: list) -> None:

        self.__init__character_classes()
        self.__mListOfPasswords = pListOfPasswords
        self.__generate_masks()

    # Public Attributes

    # Public Properties
    @property
    def passwords(self: object) -> list:
        return self.__mListOfPasswords

    @passwords.setter
    def passwords(self: object, pListOfPasswords: list) -> None:
        self.__mListOfPasswords = pListOfPasswords
        self.__generate_masks()

    @property
    def masks(self: object) -> list:
        if not self.__mPasswordMasks.populated: self.__generate_masks()
        return self.__mPasswordMasks.masks

    @property
    def count_masks(self: object) -> list:
        if not self.__mPasswordMasks.populated: self.__generate_masks()
        return self.__mPasswordMasks.count

    @property
    def count_passwords(self: object) -> list:
        if not self.__mPasswordMasks.populated: self.__generate_masks()
        return self.__mPasswordMasks.count_passwords_represented

    # Private Methods
    def __init__character_classes(self: object) -> None:

        # - ?l lower-case ASCII letters
        # - ?u upper-case ASCII letters
        # - ?d digits
        # - ?s specials (all printable ASCII characters not in ?l, ?u or ?d)
        # - ?b all (0x01-0xff) (the NULL character is currently not supported by core).

        for i in range(0, 256, 1):
            if self.__ASCII_LOWERCASE_A <= i <= self.__ASCII_LOWERCASE_Z:
                self.__mCharacterClasses[i] = "?l"
            elif self.__ASCII_UPPERCASE_A <= i <= self.__ASCII_UPPERCASE_Z:
                self.__mCharacterClasses[i] = "?u"
            elif self.__ASCII_ZERO <= i <= self.__ASCII_NINE:
                self.__mCharacterClasses[i] = "?d"
            elif self.__ASCII_SPACE <= i <= self.__ASCII_FORWARD_SLASH:
                self.__mCharacterClasses[i] = "?s"
            elif self.__ASCII_COLON <= i <= self.__ASCII_AMPERSAND:
                self.__mCharacterClasses[i] = "?s"
            elif self.__ASCII_LEFT_BRACKET <= i <= self.__ASCII_BACKTICK:
                self.__mCharacterClasses[i] = "?s"
            elif self.__ASCII_LEFT_CURLY_BRACE <= i <= self.__ASCII_FORM_FEED:
                self.__mCharacterClasses[i] = "?s"
            else:
                self.__mCharacterClasses[i] = "?b"

    def __generate_masks(self: object) -> None:

        lMasks = {}
        lCountPasswords = self.__mListOfPasswords.__len__()

        for lPassword in self.__mListOfPasswords:
            lMask = ""
            lPassword = lPassword.rstrip(self.__ASCII_CARRIAGE_RETURN_LINE_FEED)

            if lPassword: #Do not use blank passwords
                # Build mask for password
                for i in lPassword:
                    lMask += self.__mCharacterClasses[i]

                if lMask in lMasks:
                    lMasks[lMask] += 1
                else:
                    lMasks[lMask] = 1

        # Sort dictionary by popularity of mask descending
        lMasks = OrderedDict(sorted(lMasks.items(), key=lambda x: -x[1]))

        lPWMasks = []
        lCumulativeCountSoFar = 0
        for lIndex, (lMask, lCount) in enumerate(lMasks.items()):
            lCumulativeCountSoFar += lCount
            lPWMask = PasswordMask()
            lPWMask.mask = lMask
            lPWMask.oridinal_position = (lIndex + 1)
            lPWMask.count_passwords_represented = lCount
            lPWMask.marginal_percentile = lCount / lCountPasswords
            lPWMask.cumulative_percentile = lCumulativeCountSoFar / lCountPasswords
            lPWMask.pretty_marginal_percentile = round(lPWMask.marginal_percentile * 100, 2)
            lPWMask.pretty_cumulative_percentile = round(lPWMask.cumulative_percentile * 100, 2)
            lPWMasks.append(lPWMask)

        self.__mPasswordMasks.masks_with_stats = lPWMasks
        self.__mPasswordMasks.count_passwords_represented = lCountPasswords


    def __export_password_counts(self: object) -> list:

        # Output to file: Ordinal position by rank, Count of passwords represented
        # by the mask, Cumulative count of passwords up to and including this mask
        lData = []
        lOrdinalPositionsString = ""
        lPasswordCountsString = ""
        lCumulativeCountsString = ""
        lCumulativeCounts = 0
        for lPasswordMask in self.__mPasswordMasks.masks_with_stats:
            lOrdinalPositionsString += str(lPasswordMask.oridinal_position) + ","
            lPasswordCountsString += str(lPasswordMask.count_passwords_represented) + ","
            lCumulativeCounts += lPasswordMask.count_passwords_represented
            lCumulativeCountsString += str(lCumulativeCounts) + ","

        lData.append(lOrdinalPositionsString[0:lOrdinalPositionsString.__len__()-1] + "\n")
        lData.append(lPasswordCountsString[0:lPasswordCountsString.__len__()-1] + "\n")
        lData.append(lCumulativeCountsString[0:lCumulativeCountsString.__len__()-1] + "\n")

        return lData


    # Public Methods
    def get_popular_masks(self: object, pPercentile:float = 1.00) -> list:

        if not 0.0 <= pPercentile <= 1.00:
            raise ValueError('Class: PasswordMasks(). Method: get_popular_masks(). Message: The percentile provided must be between 0.0 and 1.0.')

        lMasks = []
        for lMask in self.__mPasswordMasks.masks_with_stats:
            lMasks.append(lMask.mask)
            if lMask.cumulative_percentile >= pPercentile:
                return lMasks


    def export_password_counts_to_csv(self: object, pFileName: str) -> None:

        lData = self.__export_password_counts()

        lFileHandle = open(pFileName, mode="w")
        lFileHandle.write(lData[0])
        lFileHandle.write(lData[1])
        lFileHandle.write(lData[2])
        lFileHandle.flush()
        lFileHandle.close()


    def export_password_counts_to_stdout(self: object) -> None:

        lData = self.__export_password_counts()

        print(lData[0])
        print(lData[1])
        print(lData[2])


    def get_analysis(self: object, pPercentile:float = 1.00) -> None:

        MASK = 0
        PR = 1
        MP = 2
        PMP = 3
        CP = 4
        PCP = 5
        PADDING = "  "

        if not 0.0 <= pPercentile <= 1.00:
            raise ValueError('Class: PasswordMasks(). Method: get_analysis(). Message: The percentile provided must be between 0.0 and 1.0.')

        lPlotDatum = []
        lLongestMask = 0
        lCountPasswordsPlotted = 0
        for lPasswordMask in self.__mPasswordMasks.masks_with_stats:

            if len(lPasswordMask.mask) > lLongestMask: lLongestMask = len(lPasswordMask.mask)
            lPlotData = (lPasswordMask.mask, lPasswordMask.count_passwords_represented,
                         lPasswordMask.marginal_percentile, lPasswordMask.pretty_marginal_percentile,
                         lPasswordMask.cumulative_percentile, lPasswordMask.pretty_cumulative_percentile)
            lPlotDatum.append(lPlotData)
            lCountPasswordsPlotted += lPasswordMask.count_passwords_represented

            if lPasswordMask.cumulative_percentile >= pPercentile:
                break

        lCountMasks = self.__mPasswordMasks.count
        lPlotDatumRange = lPlotDatum.__len__()
        lCountDashes = max(lPlotDatumRange * 4 + 14, 38)
        lPlotDatumMaxMarginalPercentile = int(math.ceil(lPlotDatum[0][MP] * 100))

        # Graph Title
        print()
        self.__print_dashes(lCountDashes)
        print("{}Probability Density Function (PDF)".format(PADDING))
        print("{}Showing {} out of {} masks".format(PADDING, lPlotDatumRange, lCountMasks))
        print("{}Percentile: {} ".format(PADDING, pPercentile))
        self.__print_dashes(lCountDashes)

        # Graph
        for i in range(lPlotDatumMaxMarginalPercentile, 0, -1):
            lPercentile = i / 100

            if i % 2 == 0:
                print("{}%\t".format(i), end="")
            else:
                print("\t", end="")

            for lPlotData in lPlotDatum:
                if lPlotData[MP] >= lPercentile: print("*{}".format(PADDING), end="")
            print()

        # Graph Footer
        self.__print_dashes(lCountDashes)
        print("\t", end="")
        for i in range(1, lPlotDatumRange + 1, 1):
            print("{}{}".format(i, PADDING), end="")
        print()
        self.__print_dashes(lCountDashes)

        # Legend
        print()
        print("Legend: (MP - Marginal Percentile, CP - Cumulative Percentile)")
        print()

        # Headers
        print("\t{}{}{}Mask".format(PADDING, PADDING, PADDING), end="")
        # 4 is length of word "Mask"
        self.__make_spaces(lLongestMask - 4)
        print("MP  ", end="")
        print("\tCP  ", end="")
        print("\t\tPasswords")

        # Masks
        for i, lPlotData in enumerate(lPlotDatum):
            print("\t{:2}{}{}".format(i+1, PADDING, lPlotData[MASK]), end="")
            self.__make_spaces(lLongestMask - len(lPlotData[MASK]) + PADDING.__len__())
            print("{0:.2f}".format(lPlotData[PMP]), end="")
            print("\t{0:.2f}".format(lPlotData[PCP]), end="")
            print("\t\t{}".format(lPlotData[PR]))

        # Total passwords
        print("\t", end="")
        self.__make_spaces(lLongestMask + PADDING.__len__())
        print("\t\t\t\t--------")
        print("\t", end="")
        self.__make_spaces(lLongestMask + PADDING.__len__())
        print("\t\t\t\t{} out of {} passwords".format(lCountPasswordsPlotted, self.__mPasswordMasks.count_passwords_represented))
        print()

    # Static Methods
    @staticmethod
    def __print_dashes(pCount: int) -> None:
        for i in range(0, pCount):
            print("-", end="")
        print()

    @staticmethod
    def __make_spaces(pCount: int) -> None:
        for i in range(0, pCount):
            print(" ", end="")