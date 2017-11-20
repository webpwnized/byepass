
import argparse
from argparse import RawTextHelpFormatter
from pwstats import PasswordStats


if __name__ == '__main__':

    READ_BYTES = 'rb'

    lArgParser = argparse.ArgumentParser(
        description='PassTime: Automate statistical analysis of passwords in support of password cracking tasks',
        epilog='',
        formatter_class=RawTextHelpFormatter)
    lArgParser.add_argument('-v', '--verbose', help='Enable verbose output', action='store_true')
    lArgParser.add_argument('-l', '--list-masks', help='List password masks for the password provided in the INPUT FILE', action='store_true')
    lArgParser.add_argument('-p', '--percentile', type=float, help='Based on statistical analysis of the passwords provided, only list masks needed to crack at least the given percent of passwords. For example, if a value of 0.25 provided, only lists the relatively few masks needed to crack 25% of the passwords. The prediction is only as good as the sample passwords provided in the INPUT FILE. The more closely the provided passwords match the target passwords, the better the prediction.', action='store')
    lArgParser.add_argument('-a', '--analyze-passwords', help='Perform analysis on the password provided in the INPUT FILE', action='store_true')
    lArgParser.add_argument('-i', '--input-file', type=str, help='Path to file containing passwords to analyze', action='store',
                            required=True)
    lArgs = lArgParser.parse_args()

    if lArgs.percentile and not (lArgs.list_masks or lArgs.analyze_passwords):
        raise ValueError('Argument -p/--percentile is only valid when -l/--list-masks provided')

    if lArgs.percentile and (lArgs.analyze_passwords or lArgs.list_masks):
            if not 0.0 <= lArgs.percentile <= 1.00:
                raise ValueError('The percentile provided must be between 0.0 and 1.0.')

    lListOfPasswords = []
    if lArgs.verbose:
        print()
        print("[*] Reading input file " + lArgs.input_file)
    if lArgs.input_file:
        with open(lArgs.input_file, READ_BYTES) as lFile:
            lListOfPasswords = lFile.readlines()
    if lArgs.verbose: print("[*] Finished reading input file " + lArgs.input_file)

    if lArgs.verbose:
        lCountPasswords = lListOfPasswords.__len__()
        print("[*] Passwords imported: " + str(lCountPasswords))
        if lCountPasswords > 1000000: print("[*] That is a lot of passwords. Parsing may take a while.")

    if lArgs.verbose: print("[*] Parsing input file " + lArgs.input_file)
    lPasswordStats = PasswordStats(lListOfPasswords)
    if lArgs.verbose:
        print("[*] Finished parsing input file " + lArgs.input_file)
        print("[*] Parsed {} passwords into {} masks".format(lPasswordStats.count_passwords, lPasswordStats.count_masks))

    if lArgs.analyze_passwords:
        if lArgs.percentile:
            lPasswordStats.get_analysis(lArgs.percentile)
        else:
            lPasswordStats.get_analysis(1.0)

    if lArgs.list_masks:
        if lArgs.percentile:
            if lArgs.verbose: print("[*] Password masks ({} percentile):".format(lArgs.percentile), end='')
            print(lPasswordStats.get_popular_masks(lArgs.percentile))
        else:
            print(lPasswordStats.masks)