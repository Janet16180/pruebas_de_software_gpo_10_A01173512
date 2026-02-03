"""Count word frequencies from a file containing words."""
import argparse
import logging
import time
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments for the word count program.

    Returns:
        argparse.Namespace: Parsed arguments containing the input file path.
    """
    parser = argparse.ArgumentParser(
        prog='wordCount.py',
        description='Count word frequencies from a file containing words '
                    'separated by spaces.',
        epilog='Example: python wordCount.py fileWithData.txt'
    )

    parser.add_argument(
        'input_file',
        type=Path,
        help='Path to the file containing words (separated by spaces)'
    )

    return parser.parse_args()


def is_valid_word(word: str) -> bool:
    """
    Check if a string is a valid word.

    A valid word contains at least one alphanumeric character.

    Args:
        word: The string to validate.

    Returns:
        bool: True if the word is valid, False otherwise.
    """
    for char in word:
        if ('a' <= char <= 'z') or ('A' <= char <= 'Z') or ('0' <= char <= '9'):
            return True
    return False


def normalize_word(word: str) -> str:
    """
    Normalize a word by converting to lowercase and removing punctuation.

    Args:
        word: The word to normalize.

    Returns:
        str: The normalized word.
    """
    result = ""
    for char in word:
        if ('a' <= char <= 'z') or ('A' <= char <= 'Z') or ('0' <= char <= '9'):
            if 'A' <= char <= 'Z':
                result += chr(ord(char) + 32)
            else:
                result += char
    return result


def sort_words(word_list: list[tuple[str, int]]) -> list[tuple[str, int]]:
    """
    Sort a list of (word, count) tuples alphabetically using bubble sort.

    Args:
        word_list: List of tuples (word, count).

    Returns:
        list: Sorted list of tuples.
    """
    sorted_list = word_list[:]
    n = len(sorted_list)

    for i in range(n):
        for j in range(0, n - i - 1):
            if sorted_list[j][0] > sorted_list[j + 1][0]:
                sorted_list[j], sorted_list[j + 1] = (
                    sorted_list[j + 1], sorted_list[j]
                )

    return sorted_list


def count_words(words: list[str]) -> dict[str, int]:
    """
    Count the frequency of each word in a list.

    Args:
        words: List of words to count.

    Returns:
        dict: Dictionary mapping words to their frequencies.
    """
    frequency: dict[str, int] = {}

    for word in words:
        if word in frequency:
            frequency[word] += 1
        else:
            frequency[word] = 1

    return frequency


def process_file(file_path: Path) -> list[str]:
    """
    Read and parse words from a file.

    Args:
        file_path: Path to the input file.

    Returns:
        list: List of valid words parsed from the file.
    """
    if not file_path.exists():
        logger.error("File '%s' does not exist", file_path)
        return []

    if not file_path.is_file():
        logger.error("'%s' is not a file", file_path)
        return []

    words = []

    with open(file_path, 'r', encoding='utf-8') as f:
        line_number = 0
        for line in f:
            line_number += 1

            tokens = line.split()

            for token in tokens:
                if not is_valid_word(token):
                    logger.error(
                        "Line %d: '%s' is not a valid word (no alphanumeric)",
                        line_number,
                        token
                    )
                    continue

                normalized = normalize_word(token)
                if normalized:
                    words.append(normalized)

    return words


def format_results(
    word_counts: list[tuple[str, int]],
    total_words: int,
    elapsed_time: float
) -> str:
    """
    Format the word count results as a string.

    Args:
        word_counts: List of tuples (word, count) sorted alphabetically.
        total_words: Total number of words processed.
        elapsed_time: Time taken for computation.

    Returns:
        str: Formatted results string.
    """
    lines = [
        "=" * 60,
        "WORD COUNT RESULTS",
        "=" * 60,
        f"{'WORD':<30}\t{'FREQUENCY':<10}",
        "-" * 60,
    ]

    for word, count in word_counts:
        lines.append(f"{word:<30}\t{count:<10}")

    lines.extend([
        "-" * 60,
        f"Total words processed: {total_words}",
        f"Distinct words found:  {len(word_counts)}",
        "=" * 60,
        f"Elapsed Time: {elapsed_time:.6f} seconds",
        "=" * 60,
    ])

    return '\n'.join(lines)


def write_results_to_file(
    results: str,
    output_file: str = "WordCountResults.txt"
) -> None:
    """
    Write the results to a file.

    Args:
        results: Formatted results string.
        output_file: Name of the output file.
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(results)
        f.write('\n')


def main() -> None:
    """Main function to orchestrate the word count computation."""
    start_time = time.time()

    args = parse_args()
    file_path = args.input_file

    words = process_file(file_path)

    if not words:
        logger.error("No valid words found in the file")
        return

    frequency = count_words(words)

    word_list = []
    for word, count in frequency.items():
        word_list.append((word, count))

    sorted_word_counts = sort_words(word_list)

    end_time = time.time()
    elapsed_time = end_time - start_time

    results = format_results(sorted_word_counts, len(words), elapsed_time)

    logger.info(results)
    write_results_to_file(results)
    logger.info("Results also saved to: WordCountResults.txt")


if __name__ == '__main__':
    main()
