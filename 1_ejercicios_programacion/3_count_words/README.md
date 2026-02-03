wordCount.py
============

A command line program that counts word frequencies from a file containing words.

Usage
-----

python wordCount.py fileWithData.txt

The program reads words from the input file and calculates:
- Distinct words found
- Frequency of each word (how many times it appears)

Results are displayed on screen and saved to WordCountResults.txt.


Input File Format
-----------------

The input file must contain words separated by spaces (whitespace).

Valid formats:
- Words on a single line: hello world foo bar
- Words on multiple lines:
    hello world
    foo bar baz
- Mixed case: Hello WORLD HeLLo (treated as same word: "hello", "world")
- Words with punctuation: Hello! world. "test" (punctuation is stripped)

Invalid formats (will be skipped with an error message):
- Tokens with no alphanumeric characters: !!! ??? --- (pure punctuation)

Example of a valid input file:

    The quick brown fox jumps over the lazy dog
    The fox is quick and the dog is lazy
    Hello hello HELLO world


Design Decisions
----------------

The requirements did not specify exact details about word handling, so I made the following decisions:

1. Word delimiter - Whitespace only: Words are split by any whitespace (spaces, tabs, newlines). This follows the requirement that words are "presumable between spaces."

2. Case insensitivity: Words are compared case-insensitively. "Hello", "HELLO", and "hello" are all counted as the same word "hello". This is the most common approach for word frequency analysis.

3. Punctuation handling: Punctuation attached to words is stripped. For example:
   - "Hello!" becomes "hello"
   - "world." becomes "world"
   - "(test)" becomes "test"
   - "it's" becomes "its" (apostrophes are removed)
   This ensures that "hello" and "hello!" are counted as the same word.

4. Invalid token definition: A token is considered invalid only if it contains NO alphanumeric characters (letters or digits). Pure punctuation sequences like "!!!" or "---" are reported as errors.

5. Output sorting: Results are sorted alphabetically by word for easier reading and consistent output.

6. Numbers as words: Tokens containing digits (e.g., "abc123", "2024") are considered valid words. This allows counting identifiers or codes that mix letters and numbers.


Implementation Note: Basic Algorithms Requirement
-------------------------------------------------

The requirements state: "All computation MUST be calculated using the basic algorithms, not functions or libraries."

To comply with this requirement, the following algorithms were implemented manually instead of using Python's built-in functions:

- Word counting: Implemented using a manual dictionary loop instead of `collections.Counter`
- Sorting: Implemented using bubble sort algorithm instead of Python's built-in `sorted()` or `list.sort()`
- Character validation: Implemented using character comparison instead of `str.isalnum()`
- Case conversion: Implemented using ASCII arithmetic instead of `str.lower()`
- Word normalization: Implemented character-by-character instead of `str.translate()` or regex

Note: The instructions are not entirely clear about where the boundary lies. For example, it is ambiguous whether basic operations like `str.split()`, file I/O, or `dict` operations are allowed. This implementation interprets the requirement as applying specifically to the word counting and processing computations themselves, while allowing standard Python functionality for auxiliary tasks (reading files, argument parsing, splitting strings by whitespace, etc.).


Output Format
-------------

The program prints results to the screen and saves them to WordCountResults.txt:

```
============================================================
WORD COUNT RESULTS
============================================================
WORD                          	FREQUENCY
------------------------------------------------------------
brown                         	1
dog                           	2
fox                           	2
hello                         	3
is                            	2
jumps                         	1
lazy                          	2
over                          	1
quick                         	2
the                           	4
world                         	1
------------------------------------------------------------
Total words processed: 21
Distinct words found:  11
============================================================
Elapsed Time: 0.000123 seconds
============================================================
```


Error Handling
--------------

When the program encounters invalid data:
- An error message is printed to the console showing the line number and content
- The invalid token is skipped (not included in results)
- Processing continues with the remaining tokens

Example error output:
    Line 5: '!!!' is not a valid word (no alphanumeric)
    Line 8: '---' is not a valid word (no alphanumeric)

