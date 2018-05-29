
import argparse
from argparse import RawTextHelpFormatter
from pwstats import PasswordStats


if __name__ == '__main__':

    READ_BYTES = 'rb'

    lArgParser = argparse.ArgumentParser(
        description='PassTime: Automate statistical analysis of passwords in support of password cracking tasks',
        epilog="""
        Examples:\n\n
        \tList masks representing 75 percent of the passwords in input file worst-10000-passwords.txt\n\n
        \tpython3 passtime.py -l -p 0.75 -i worst-10000-passwords.txt\n\n
        \tGenerate probability density function (PDF), masks, marginal percentile (MP), cummulative percentile (CP) and count of passwords representing 75 percent of the passwords in input file worst-10000-passwords.txt\n\n
        \tpython3 passtime.py -a -p 0.75 -i worst-10000-passwords.txt\n\n
        """,
        formatter_class=RawTextHelpFormatter)
    lArgParser.add_argument('-v', '--verbose', help='Enable verbose output', action='store_true')
    lArgParser.add_argument('-l', '--list-masks', help='List password masks for the passwords provided in the INPUT FILE', action='store_true')
    lArgParser.add_argument('-a', '--analyze-passwords', help='Perform analysis on the password provided in the INPUT FILE. A probability density function (PDF) will be displayed with the masks matching PERCENTILE percent of passwords. The marginal and cummulative percentages represented by each mask are provided with the number of passwords matched by the mask.', action='store_true')
    lArgParser.add_argument('-p', '--percentile', type=float, help='Based on statistical analysis of the passwords provided, only list masks matching the given PERCENTILE percent of passwords. For example, if a value of 0.25 provided, only lists the relatively few masks needed to crack 25 percent of the passwords. Ideally, these would be the only masks needed to crack the same percentage of the remaining, uncracked passwords. However, the prediction is only as good as the sample passwords provided in the INPUT FILE. The more closely the provided passwords match the target passwords, the better the prediction.', action='store')
    lRawDataOptionsGroup = lArgParser.add_argument_group('Raw Data Options')
    lRawDataOptionsGroup.add_argument('-d', '--dump-data', help='Write the ordinal position, raw count and cumulative count of passwords represented to file. Useful to analyze values in spreadsheet. Values are written comma-separated.', action='store_true')
    lRawDataOptionsGroup.add_argument('-o', '--output-file', type=str, help='Write the data to the file specified', action='store')
    requiredAguments = lArgParser.add_argument_group('required arguments')
    requiredAguments.add_argument('-i', '--input-file', type=str, help='Path to file containing passwords to analyze', action='store',
                            required=True)
    lArgs = lArgParser.parse_args()

    # Input validation
    if lArgs.percentile and not (lArgs.list_masks or lArgs.analyze_passwords):
        raise ValueError('Argument -p/--percentile is only valid when -l/--list-masks or -a,--analyze-passwords provided')

    if lArgs.percentile and (lArgs.analyze_passwords or lArgs.list_masks):
            if not 0.0 <= lArgs.percentile <= 1.00:
                raise ValueError('The percentile provided must be between 0.0 and 1.0.')

    if lArgs.output_file and not lArgs.dump_data:
        raise ValueError('The output_file parameter requires the -d/--dump-data flag to be set')

    # By default, all masks are discovered
    if lArgs.percentile:
        lPercentile = lArgs.percentile
    else:
        lPercentile = 1.0

    # Read input file into dictionary
    lListOfPasswords = []
    if lArgs.verbose:
        print()
        print("[*] Reading input file " + lArgs.input_file)
    if lArgs.input_file:
        with open(lArgs.input_file, READ_BYTES) as lFile:
            lListOfPasswords = lFile.readlines()
    if lArgs.verbose: print("[*] Finished reading input file " + lArgs.input_file)

    # Count passwords imported
    if lArgs.verbose:
        lCountPasswords = lListOfPasswords.__len__()
        print("[*] Passwords imported: " + str(lCountPasswords))
        if lCountPasswords > 1000000: print("[*] That is a lot of passwords. Parsing may take a while.")

    # Calculate password statistics and store in PasswordStats object
    if lArgs.verbose: print("[*] Parsing input file " + lArgs.input_file)
    lPasswordStats = PasswordStats(lListOfPasswords)
    if lArgs.verbose:
        print("[*] Finished parsing input file " + lArgs.input_file)
        print("[*] Parsed {} passwords into {} masks".format(lPasswordStats.count_passwords, lPasswordStats.count_masks))

    if lArgs.analyze_passwords:
        lPasswordStats.get_analysis(lPercentile)

    if lArgs.list_masks:
        if lArgs.verbose: print("[*] Password masks ({} percentile):".format(lPercentile), end='')
        print(lPasswordStats.get_popular_masks(lPercentile))

    if lArgs.dump_data:

        if lArgs.output_file:
            if lArgs.verbose: print("[*] Finished writing password counts per mask to output file " + lArgs.output_file)
            lPasswordStats.export_password_counts_to_csv(lArgs.output_file)
        else:
            if lArgs.verbose: print("[*] Password counts per mask")
            lPasswordStats.export_password_counts_to_stdout()




