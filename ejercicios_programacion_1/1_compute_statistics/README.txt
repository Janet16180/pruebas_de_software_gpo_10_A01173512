computeStatistics.py
====================

A command line program that computes descriptive statistics from a file containing numbers.

Usage
-----

python computeStatistics.py fileWithData.txt

The program reads numbers from the input file and calculates:
- Count (number of valid entries)
- Mean
- Median
- Mode (shows N/A if there are multiple modes or all values are unique)
- Standard Deviation
- Variance

Results are displayed on screen and saved to StatisticsResults.txt.


Input File Format
-----------------

The input file must contain one number per line.

Valid formats:
- Integers: 42, -17, +5
- Decimals: 3.14, -0.5, .25, 123.456

Invalid formats (will be skipped with an error message):
- Numbers separated by comma: 5,3 (ambiguous: could be two numbers or a decimal)
- Numbers separated by semicolon: 11;54
- Text or letters: ABC, hello, 405s
- Empty lines (ignored silently)

Example of a valid input file:

    10
    20
    30.5
    -15
    100


Design Decisions
----------------

The requirements did not specify the exact input format, so I made the following decisions based on the examples provided:

1. One number per line: Since the requirements mention "a list of items" without specifying a delimiter, I chose one number per line as the safest interpretation.

2. Comma as invalid: A line like "5,3" is ambiguous. It could mean two separate numbers (5 and 3) or a decimal number using European notation (5.3). To avoid confusion, lines containing commas are treated as invalid.

3. Semicolon as invalid: Similar to commas, semicolons could be interpreted as separators. Lines like "11;54" are treated as invalid.

4. Mode display: When multiple values share the highest frequency (multiple modes), the program displays N/A instead of listing all modes.

5. Decimal point: Only the period (.) is accepted as a decimal separator, following standard programming conventions.


Output Format
-------------

The program prints results to the screen and saves them to StatisticsResults.txt:

==================================================
DESCRIPTIVE STATISTICS RESULTS
==================================================
Count:              [number of valid entries]
Mean:               [calculated mean]
Median:             [calculated median]
Mode:               [mode value or N/A]
Standard Deviation: [calculated std dev]
Variance:           [calculated variance]
==================================================
Elapsed Time:       [execution time] seconds
==================================================


Error Handling
--------------

When the program encounters invalid data:
- An error message is printed to the console showing the line number and content
- The invalid line is skipped
- Processing continues with the remaining lines

Example error output:
    Line 5 'ABA' cannot be converted to a number
    Line 10 '23,45' cannot be converted to a number

