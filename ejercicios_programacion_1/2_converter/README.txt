convertNumbers.py
=================

A command line program that converts numbers to binary and hexadecimal representation.

Usage
-----

python convertNumbers.py fileWithData.txt

The program reads integers from the input file and converts each to:
- Binary representation
- Hexadecimal representation (uppercase)

Results are displayed on screen and saved to ConvertionResults.txt.


Input File Format
-----------------

The input file must contain one integer per line.

Valid formats:
- Positive integers: 42, 255, 1000
- Negative integers: -39, -100
- Zero: 0

Invalid formats (will be skipped with an error message):
- Decimal numbers: 3.14, -0.5
- Text or letters: ABC, hello, 405s
- Empty lines (ignored silently)

Example of a valid input file:

    10
    255
    -39
    0
    1000


Design Decisions
----------------

The requirements did not specify the exact output format for conversions, so I made the following decisions:

1. Negative numbers - Two's complement: Since the requirements do not specify how to represent negative numbers in binary and hexadecimal, I use 32-bit two's complement representation. For example:
   - -39 in binary:  11111111111111111111111111011001
   - -39 in hex:     FFFFFFD9

2. Invalid data handling: The requirements state that "errors should be displayed in the console and the execution must continue." Invalid values are NOT included in the results file - only the error message is shown in the console. This ensures the output file contains only valid conversions.

3. Integer only: The program only accepts integers since binary and hexadecimal conversions are typically defined for integer values. Decimal numbers are treated as invalid input.

4. Output prefix removed: The standard Python prefixes '0b' (binary) and '0x' (hexadecimal) are removed from the output for cleaner presentation.

5. Hexadecimal case: Hexadecimal output uses uppercase letters (A-F) for consistency.


Implementation Note: Basic Algorithms Requirement
-------------------------------------------------

The requirements state: "All computation MUST be calculated using the basic algorithms, not functions or libraries."

To comply with this requirement, the following algorithms were implemented manually instead of using Python's built-in functions:

- Binary conversion: Implemented using the division-remainder algorithm instead of Python's built-in `bin()`
- Hexadecimal conversion: Implemented using the division-remainder algorithm instead of Python's built-in `hex()`

Note: The instructions are not entirely clear about where the boundary lies. For example, it is ambiguous whether basic operations like `int()`, file I/O, or string methods are allowed. This implementation interprets the requirement as applying specifically to the base conversion computations themselves, while allowing standard Python functionality for auxiliary tasks (reading files, argument parsing, parsing strings to integers, etc.).


Output Format
-------------

The program prints results to the screen and saves them to ConvertionResults.txt:

================================================================================
NUMBER CONVERSION RESULTS
================================================================================
NUMBER              	BINARY                                  	HEXADECIMAL
--------------------------------------------------------------------------------
10                  	1010                                    	A
255                 	11111111                                	FF
-39                 	11111111111111111111111111011001        	FFFFFFD9
--------------------------------------------------------------------------------
Total numbers converted: 3
================================================================================
Elapsed Time: 0.000123 seconds
================================================================================


Error Handling
--------------

When the program encounters invalid data:
- An error message is printed to the console showing the line number and content
- The invalid line is skipped (not included in results)
- Processing continues with the remaining lines

Example error output:
    Line 3: '3.14' is not a valid integer
    Line 7: 'ABC' is not a valid integer

