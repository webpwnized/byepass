# Usage

## Using PassTime

**Automate statistical analysis of passwords in support of password cracking tasks**

**Usage**: passtime.py [-h] [-v] [-l] [-p PERCENTILE] [-a] -i INPUT_FILE

**Optional arguments:**

      -h, --help            show this help message and exit
      -v, --verbose         Enable verbose output
      -l, --list-masks      List password masks for the passwords provided in the INPUT FILE
      -p PERCENTILE, --percentile PERCENTILE
                            Based on statistical analysis of the passwords provided, only list masks matching the given PERCENTILE percent of passwords. For example, if a value of 0.25 provided, only lists the relatively few masks needed to crack 25 percent of the passwords. Ideally, these would be the only masks needed to crack the same percentage of the remaining, uncracked passwords. However, the prediction is only as good as the sample passwords provided in the INPUT FILE. The more closely the provided passwords match the target passwords, the better the prediction.
      -a, --analyze-passwords
                            Perform analysis on the password provided in the INPUT FILE. A probability density function (PDF) will be displayed with the masks matching PERCENTILE percent of passwords. The marginal and cummulative percentages represented by each mask are provided with the number of passwords matched by the mask.

**Required arguments:**
      -i INPUT_FILE, --input-file INPUT_FILE
                            Path to file containing passwords to analyze

## Examples:

### Listing Masks

List masks representing 75 percent of the passwords in input file passwords.txt

    python3 passtime.py -l -p 0.75 -i passwords.txt

### Analyzing Passwords

Generate probability density function (PDF), masks, marginal percentile (MP), cummulative percentile (CP) and count of passwords representing 75 percent of the passwords in input file passwords.txt

    python3 passtime.py -a -p 0.75 -i passwords.txt

### Creating format suitable for import into spreadsheet

Output the number of passwords represented by each mask sorted by count descending. The first row labels the mask. The second row contains the raw counts per mask. The third row contains the cumulative counts per mask. Values are comma-separated.

    python3 passtime.py -v -d -i passwords.txt

These same values can be output to a file with the addition of the -o/--output-file argument

    python3 passtime.py -v -d -i passwords.txt -o raw-data.csv
