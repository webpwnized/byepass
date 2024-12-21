from typing import NamedTuple

class TaskRecord(NamedTuple):
    Mode: str
    Mask: str
    Wordlist: str
    Rule: str
    NumberPasswordsCracked: int
    NumberPasswordsCrackedPerSecond: int
    PercentPasswordsCracked: int

class Reporter:

    __mTaskRecords = []

    def appendRecord(self, pMode: str, pWordlist: str, pRule: str, pMask: str,
                     pNumberPasswordsCracked: int, pNumberPasswordsCrackedPerSecond: int,
                     pPercentPasswordsCracked):

        lTaskRecord = TaskRecord(Mode=pMode, Mask=pMask, Wordlist=pWordlist, Rule=pRule,
                                 NumberPasswordsCracked=pNumberPasswordsCracked,
                                 NumberPasswordsCrackedPerSecond=pNumberPasswordsCrackedPerSecond,
                                 PercentPasswordsCracked=pPercentPasswordsCracked)

        self.__mTaskRecords.append(lTaskRecord)

    def reportResults(self):
        # Sort by percent passwords cracked then raw number cracked
        self.__mTaskRecords.sort(key=lambda x: x.NumberPasswordsCracked, reverse=True)
        self.__mTaskRecords.sort(key=lambda x: x.PercentPasswordsCracked, reverse=True)

        for lRecord in self.__mTaskRecords:
            lLine = ""

            if lRecord.Mode: lLine += "Mode:{}\t\t".format(lRecord.Mode)
            lLine += "Cracked:{}\t".format(lRecord.NumberPasswordsCracked)
            lLine += "{}%".format(lRecord.PercentPasswordsCracked)
            print(lLine)