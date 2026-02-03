"""Compute descriptive statistics from a file containing numbers."""
import argparse
import logging
import re
import time
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)


class StatisticsCalculator:
    """Class containing static methods for computing descriptive statistics."""

    @staticmethod
    def sort_numbers(numbers: list[float]) -> list[float]:
        """
        Sort a list of numbers using quicksort algorithm.

        Source: https://stackoverflow.com/a/3855607
        Posted by fmark, modified by community. See post 'Timeline' for history.

        Args:
            numbers: List of numbers to sort.

        Returns:
            list: Sorted list of numbers.
        """
        if numbers == []:
            return []
        else:
            pivot = numbers[0]
            lesser = StatisticsCalculator.sort_numbers(
                [x for x in numbers[1:] if x < pivot]
            )
            greater = StatisticsCalculator.sort_numbers(
                [x for x in numbers[1:] if x >= pivot]
            )
            return lesser + [pivot] + greater

    @staticmethod
    def sqrt(number: float) -> float:
        """
        Calculate the square root using Newton-Raphson method.

        Args:
            number: The number to find the square root of.

        Returns:
            float: The square root value.
        """
        if number < 0:
            return 0.0
        if number == 0:
            return 0.0

        guess = number / 2.0
        tolerance = 1e-10

        while True:
            new_guess = (guess + number / guess) / 2.0
            diff = new_guess - guess
            if diff < 0:
                diff = -diff
            if diff < tolerance:
                break
            guess = new_guess

        return new_guess

    @staticmethod
    def mean(numbers: list[float]) -> float:
        """
        Calculate the arithmetic mean of a list of numbers.

        Args:
            numbers: List of numbers.

        Returns:
            float: The mean value.
        """
        if not numbers:
            return 0.0

        total = 0.0
        count = 0
        for num in numbers:
            total += num
            count += 1

        return total / count

    @staticmethod
    def median(numbers: list[float]) -> float:
        """
        Calculate the median of a list of numbers.

        Args:
            numbers: List of numbers.

        Returns:
            float: The median value.
        """
        if not numbers:
            return 0.0

        sorted_numbers = StatisticsCalculator.sort_numbers(numbers)
        n = len(sorted_numbers)

        if n % 2 == 1:
            return sorted_numbers[n // 2]
        else:
            mid1 = sorted_numbers[n // 2 - 1]
            mid2 = sorted_numbers[n // 2]
            return (mid1 + mid2) / 2

    @staticmethod
    def mode(numbers: list[float]) -> list[float]:
        """
        Calculate the mode of a list of numbers.

        Args:
            numbers: List of numbers.

        Returns:
            list: List of mode values (can be multiple if there's a tie).
        """
        if not numbers:
            return []

        frequency = {}
        for num in numbers:
            if num in frequency:
                frequency[num] += 1
            else:
                frequency[num] = 1

        max_count = 0
        for count in frequency.values():
            if count > max_count:
                max_count = count

        modes = []
        for num, count in frequency.items():
            if count == max_count:
                modes.append(num)

        return StatisticsCalculator.sort_numbers(modes)

    @staticmethod
    def variance(numbers: list[float]) -> float:
        """
        Calculate the population variance of a list of numbers.

        Args:
            numbers: List of numbers.

        Returns:
            float: The variance value.
        """
        if not numbers:
            return 0.0

        mean_val = StatisticsCalculator.mean(numbers)
        squared_diff_sum = 0.0

        for num in numbers:
            diff = num - mean_val
            squared_diff_sum += diff * diff

        return squared_diff_sum / len(numbers)

    @staticmethod
    def std_dev(numbers: list[float]) -> float:
        """
        Calculate the population standard deviation of a list of numbers.

        Args:
            numbers: List of numbers.

        Returns:
            float: The standard deviation value.
        """
        if not numbers:
            return 0.0

        variance_val = StatisticsCalculator.variance(numbers)
        return StatisticsCalculator.sqrt(variance_val)


def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments for the statistics computation program.

    Returns:
        argparse.Namespace: Parsed arguments containing the input file path.
    """
    parser = argparse.ArgumentParser(
        prog='computeStatistics.py',
        description='Compute descriptive statistics (mean, median, mode, '
                    'standard deviation, and variance) from a file containing '
                    'numbers.',
        epilog='Example: python computeStatistics.py fileWithData.txt'
    )

    parser.add_argument(
        'input_file',
        type=Path,
        help='Path to the file containing numbers (one per line)'
    )

    return parser.parse_args()


def process_file(file_path: Path) -> list[float]:
    """
    Read and parse numbers from a file.

    Args:
        file_path: Path to the input file.

    Returns:
        list: List of valid numbers parsed from the file.
    """
    if not file_path.exists():
        logger.error("File '%s' does not exist", file_path)
        return []

    if not file_path.is_file():
        logger.error("'%s' is not a file", file_path)
        return []

    numbers = []
    number_pattern = re.compile(
        r"^[-+]?(\d+\.?\d*|\d*\.?\d+)$"
    )

    with open(file_path, 'r', encoding='utf-8') as f:
        line_number = 0
        for line in f:
            line_number += 1
            line = line.strip()

            if not line:
                continue

            match_number = number_pattern.match(line)

            if not match_number:
                logger.error(
                    "Line %d '%s' cannot be converted to a number",
                    line_number,
                    line
                )
                continue

            numbers.append(float(line))

    return numbers


def format_results(
    count: int,
    mean: float,
    median: float,
    mode: list[float],
    std_dev: float,
    variance: float,
    elapsed_time: float
) -> str:
    """
    Format the statistics results as a string.

    Args:
        count: Number of valid data points.
        mean: Calculated mean.
        median: Calculated median.
        mode: Calculated mode(s).
        std_dev: Calculated standard deviation.
        variance: Calculated variance.
        elapsed_time: Time taken for computation.

    Returns:
        str: Formatted results string.
    """
    if not mode or len(mode) > 1:
        mode_str = 'N/A'
    else:
        mode_str = f"{mode[0]:f}"

    results = [
        "=" * 50,
        "DESCRIPTIVE STATISTICS RESULTS",
        "=" * 50,
        f"Count:              {count}",
        f"Mean:               {mean:f}",
        f"Median:             {median:f}",
        f"Mode:               {mode_str}",
        f"Standard Deviation: {std_dev:f}",
        f"Variance:           {variance:f}",
        "=" * 50,
        f"Elapsed Time:       {elapsed_time:.6f} seconds",
        "=" * 50,
    ]

    return '\n'.join(results)


def write_results_to_file(results: str, output_file: str = "StatisticsResults.txt") -> None:
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
    """Main function to orchestrate the statistics computation."""
    start_time = time.time()

    args = parse_args()
    file_path = args.input_file

    numbers = process_file(file_path)

    if not numbers:
        logger.error("No valid numbers found in the file")
        return

    mean = StatisticsCalculator.mean(numbers)
    median = StatisticsCalculator.median(numbers)
    mode = StatisticsCalculator.mode(numbers)
    variance = StatisticsCalculator.variance(numbers)
    std_dev = StatisticsCalculator.std_dev(numbers)

    end_time = time.time()
    elapsed_time = end_time - start_time

    results = format_results(
        count=len(numbers),
        mean=mean,
        median=median,
        mode=mode,
        std_dev=std_dev,
        variance=variance,
        elapsed_time=elapsed_time
    )

    logger.info(results)
    write_results_to_file(results)
    logger.info("Results also saved to: StatisticsResults.txt")


if __name__ == '__main__':
    main()
