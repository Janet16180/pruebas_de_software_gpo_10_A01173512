"""Convert numbers to binary and hexadecimal representation."""
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
    Parse command line arguments for the number conversion program.

    Returns:
        argparse.Namespace: Parsed arguments containing the input file path.
    """
    parser = argparse.ArgumentParser(
        prog='convertNumbers.py',
        description='Convert numbers from a file to binary and hexadecimal '
                    'representation.',
        epilog='Example: python convertNumbers.py fileWithData.txt'
    )

    parser.add_argument(
        'input_file',
        type=Path,
        help='Path to the file containing numbers (one per line)'
    )

    return parser.parse_args()


def process_file(file_path: Path) -> list[tuple[int, str, str]]:
    """
    Read and parse numbers from a file, converting them to binary and hex.

    Args:
        file_path: Path to the input file.

    Returns:
        list: List of tuples (original_number, binary, hexadecimal).
    """
    if not file_path.exists():
        logger.error("File '%s' does not exist", file_path)
        return []

    if not file_path.is_file():
        logger.error("'%s' is not a file", file_path)
        return []

    results = []

    with open(file_path, 'r', encoding='utf-8') as f:
        line_number = 0
        for line in f:
            line_number += 1
            line = line.strip()

            if not line:
                continue

            try:
                number = int(line)
            except ValueError:
                logger.error(
                    "Line %d: '%s' is not a valid integer",
                    line_number,
                    line
                )
                continue

            if number >= 0:
                binary = bin(number)[2:]
                hexadecimal = hex(number)[2:].upper()
            else:
                twos_complement = (2**32) + number
                binary = bin(twos_complement)[2:]
                hexadecimal = hex(twos_complement)[2:].upper()
            results.append((number, binary, hexadecimal))

    return results


def format_results(
    conversions: list[tuple[int, str, str]],
    elapsed_time: float
) -> str:
    """
    Format the conversion results as a string.

    Args:
        conversions: List of tuples (number, binary, hexadecimal).
        elapsed_time: Time taken for computation.

    Returns:
        str: Formatted results string.
    """
    lines = [
        "=" * 80,
        "NUMBER CONVERSION RESULTS",
        "=" * 80,
        f"{'NUMBER':<20}\t{'BINARY':<40}\t{'HEXADECIMAL':<20}",
        "-" * 80,
    ]

    for number, binary, hexadecimal in conversions:
        lines.append(f"{number:<20}\t{binary:<40}\t{hexadecimal:<20}")

    lines.extend([
        "-" * 80,
        f"Total numbers converted: {len(conversions)}",
        "=" * 80,
        f"Elapsed Time: {elapsed_time:.6f} seconds",
        "=" * 80,
    ])

    return '\n'.join(lines)


def write_results_to_file(
    results: str,
    output_file: str = "ConvertionResults.txt"
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
    """Main function to orchestrate the number conversion."""
    start_time = time.time()

    args = parse_args()
    file_path = args.input_file

    conversions = process_file(file_path)

    if not conversions:
        logger.error("No valid numbers found in the file")
        return

    end_time = time.time()
    elapsed_time = end_time - start_time

    results = format_results(conversions, elapsed_time)

    logger.info(results)
    write_results_to_file(results)
    logger.info("Results also saved to: ConvertionResults.txt")


if __name__ == '__main__':
    main()
