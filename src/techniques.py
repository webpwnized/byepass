from typing import NamedTuple

class Technique(NamedTuple):
    folder: str
    dictionaries: list
    rules: list

class Techniques:

    __mTechniques = {}

    # Folders in which wordlists are stored
    __mDictionaryFolder = "dictionaries"
    __mPasswordFolder = "passwords"

    # Lists of dictionaries
    __mSmallDictionaries = ["calendar.txt", "short-list.txt", "brands.txt", "movie-characters.txt", "animals.txt",
                            "astrology.txt", "songs.txt"]
    __mMediumDictionaries = ["anime.txt", "sports.txt", "bible.txt", "top-10000-english-words.txt",
                             "top-10000-spanish-words.txt", "top-10000-german-words.txt"]
    __mLargeDictionaries = ["persons-names.txt", "other-base-words.txt", "places.txt"]
    __mVeryLargeDictionaries = ["all-english-words.txt", "all-spanish-words.txt", "all-french-words.txt", "all-german-words.txt"]
    __mCalendarDictionary = ["calendar.txt"]

    # Lists of passwords
    __mWorstPasswordList = ["worst-50000-passwords.txt"]

    # Lists of rules
    __mSmallRules = ["SlowHashesPhase1", "Best126", "SlowHashesPhase2"]
    __mMediumRules = ["SlowHashesPhase3"]
    __mLargeRules = ["OneRuleToRuleThemAll"]
    __HailmaryRule = ["Hailmary"]
    __CalendarRule = ["Calendar"]

    @property
    def techniques(self: object) -> dict:
        return self.__mTechniques

    # Constructor
    def __init__(self: object) -> None:
        self.__generate_techniques()

    # Private methods
    def __generate_techniques(self: object) -> None:

        # Words: 50,000 words  Rules: 1 mangles Factor: 50,000
        self.__mTechniques[1] = Technique(self.__mPasswordFolder, self.__mWorstPasswordList, self.__HailmaryRule)

        # Words: < 10,000 words  Rules: <=1,000 mangles Factor: <10,000,000
        self.__mTechniques[2] = Technique(self.__mDictionaryFolder, self.__mSmallDictionaries, self.__mSmallRules)

        # Words: 1,000 words  Rules: 10,000 mangles Factor: <10,000,000
        self.__mTechniques[3] = Technique(self.__mDictionaryFolder, self.__mCalendarDictionary, self.__CalendarRule)

        # Words: 10,000 words  Rules: <=1,000 mangles Factor: 10,000,000
        self.__mTechniques[4] = Technique(self.__mDictionaryFolder, self.__mMediumDictionaries, self.__mSmallRules)

        # Words: < 10,000 words  Rules: 6,500 mangles Factor: <65,000,000
        self.__mTechniques[5] = Technique(self.__mDictionaryFolder, self.__mSmallDictionaries, self.__mMediumRules)

        # Words: 10,000 words  Rules: 6,500 mangles Factor: 65,000,000
        self.__mTechniques[6] = Technique(self.__mDictionaryFolder, self.__mMediumDictionaries, self.__mMediumRules)

        # Words: 180,000 words  Rules: 1,000 mangles Factor: 180,000,000
        self.__mTechniques[7] = Technique(self.__mDictionaryFolder, self.__mLargeDictionaries, self.__mSmallRules)

        # Words: < 10,000 words  Rules: 50,000 mangles Factor: <500,000,000
        self.__mTechniques[8] = Technique(self.__mDictionaryFolder, self.__mSmallDictionaries, self.__mLargeRules)

        # Words: 10,000 words  Rules: 50,000 mangles Factor: 500,000,000
        self.__mTechniques[9] = Technique(self.__mDictionaryFolder, self.__mMediumDictionaries, self.__mLargeRules)

        # Words: 150,000 words  Rules: 6,500 mangles Factor: 975,000,000
        self.__mTechniques[10] = Technique(self.__mDictionaryFolder, self.__mLargeDictionaries, self.__mMediumRules)

        # Words: 2,000,000 words  Rules: 1,000 mangles Factor: 2,000,000,000
        self.__mTechniques[11] = Technique(self.__mDictionaryFolder, self.__mVeryLargeDictionaries, self.__mSmallRules)

        # Words: 150,000 words  Rules: 50,000 mangles Factor: 7,500,000,000
        self.__mTechniques[12] = Technique(self.__mDictionaryFolder, self.__mLargeDictionaries, self.__mLargeRules)

        # Words: 2,000,000 words  Rules: 6,500 mangles Factor: 13,000,000,000
        self.__mTechniques[13] = Technique(self.__mDictionaryFolder, self.__mVeryLargeDictionaries, self.__mMediumRules)

        # Words: 2,000,000 words  Rules: 50,000 mangles Factor: 100,000,000,000
        self.__mTechniques[14] = Technique(self.__mDictionaryFolder, self.__mVeryLargeDictionaries, self.__mLargeRules)

    # Public methods
    def get_technique(self, pTechnique: int) -> tuple:
        return self.__mTechniques[pTechnique].folder, self.__mTechniques[pTechnique].dictionaries, \
               self.__mTechniques[pTechnique].rules

