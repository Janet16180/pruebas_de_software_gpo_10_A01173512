"""Unit tests for computeStatistics module."""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

import pytest  # noqa: E402
from compute_statistics import (  # noqa: E402
    StatisticsCalculator,
    StatisticsResult,
    process_file,
    format_results,
)

DATA_DIR = BASE_DIR / "data"


# ──────────────────────────────────────────────
# StatisticsCalculator.sort_numbers
# ──────────────────────────────────────────────


class TestSortNumbers:
    """Tests for the quicksort implementation."""

    def test_sort_empty_list(self):
        """An empty list should return an empty list."""
        assert StatisticsCalculator.sort_numbers([]) == []

    def test_sort_single_element(self):
        """A single element list is already sorted."""
        assert StatisticsCalculator.sort_numbers([42]) == [42]

    def test_sort_already_sorted(self):
        """An already sorted list should remain the same."""
        assert StatisticsCalculator.sort_numbers([1, 2, 3, 4, 5]) == [
            1,
            2,
            3,
            4,
            5,
        ]

    def test_sort_reverse_order(self):
        """A reverse-sorted list should be sorted ascending."""
        assert StatisticsCalculator.sort_numbers([5, 4, 3, 2, 1]) == [
            1,
            2,
            3,
            4,
            5,
        ]

    def test_sort_with_duplicates(self):
        """Duplicates should be preserved in the sorted output."""
        assert StatisticsCalculator.sort_numbers([3, 1, 2, 1, 3]) == [
            1,
            1,
            2,
            3,
            3,
        ]

    def test_sort_negative_numbers(self):
        """Negative numbers should be sorted correctly."""
        assert StatisticsCalculator.sort_numbers([-3, -1, -2, 0, 2]) == [
            -3,
            -2,
            -1,
            0,
            2,
        ]

    def test_sort_decimals(self):
        """Decimal numbers should be sorted correctly."""
        assert StatisticsCalculator.sort_numbers([1.5, 0.3, 2.7, 1.1]) == [
            0.3,
            1.1,
            1.5,
            2.7,
        ]


# ──────────────────────────────────────────────
# StatisticsCalculator.sqrt
# ──────────────────────────────────────────────


class TestSqrt:
    """Tests for the Newton-Raphson square root implementation."""

    def test_sqrt_zero(self):
        """Square root of zero should be zero."""
        assert StatisticsCalculator.sqrt(0) == 0.0

    def test_sqrt_negative(self):
        """Square root of a negative number should return zero."""
        assert StatisticsCalculator.sqrt(-4) == 0.0

    def test_sqrt_perfect_square(self):
        """Square root of a perfect square should be exact."""
        assert StatisticsCalculator.sqrt(4) == pytest.approx(2.0, abs=1e-6)
        assert StatisticsCalculator.sqrt(9) == pytest.approx(3.0, abs=1e-6)
        assert StatisticsCalculator.sqrt(16) == pytest.approx(4.0, abs=1e-6)

    def test_sqrt_non_perfect_square(self):
        """Square root of non-perfect squares should be accurate."""
        assert StatisticsCalculator.sqrt(2) == pytest.approx(
            1.414213, abs=1e-6
        )
        assert StatisticsCalculator.sqrt(3) == pytest.approx(
            1.732050, abs=1e-6
        )

    def test_sqrt_large_number(self):
        """Square root of a large number should be accurate."""
        assert StatisticsCalculator.sqrt(1000000) == pytest.approx(
            1000.0, abs=1e-6
        )


# ──────────────────────────────────────────────
# StatisticsCalculator.mean
# ──────────────────────────────────────────────


class TestMean:
    """Tests for the mean calculation."""

    def test_mean_empty_list(self):
        """Mean of an empty list should be zero."""
        assert StatisticsCalculator.mean([]) == 0.0

    def test_mean_single_element(self):
        """Mean of a single element is that element."""
        assert StatisticsCalculator.mean([5.0]) == 5.0

    def test_mean_integers(self):
        """Mean of integer values."""
        assert StatisticsCalculator.mean([1, 2, 3, 4, 5]) == pytest.approx(3.0)

    def test_mean_negative_numbers(self):
        """Mean with negative numbers."""
        assert StatisticsCalculator.mean([-2, -1, 0, 1, 2]) == pytest.approx(
            0.0
        )

    def test_mean_decimals(self):
        """Mean of decimal numbers."""
        assert StatisticsCalculator.mean([1.5, 2.5, 3.5]) == pytest.approx(2.5)


# ──────────────────────────────────────────────
# StatisticsCalculator.median
# ──────────────────────────────────────────────


class TestMedian:
    """Tests for the median calculation."""

    def test_median_empty_list(self):
        """Median of an empty list should be zero."""
        assert StatisticsCalculator.median([]) == 0.0

    def test_median_single_element(self):
        """Median of a single element is that element."""
        assert StatisticsCalculator.median([7.0]) == 7.0

    def test_median_odd_count(self):
        """Median with an odd number of elements."""
        assert StatisticsCalculator.median([3, 1, 2]) == pytest.approx(2.0)

    def test_median_even_count(self):
        """Median with even count is the average of two middle."""
        assert StatisticsCalculator.median([1, 2, 3, 4]) == pytest.approx(2.5)

    def test_median_unsorted_input(self):
        """Median should work with unsorted input."""
        assert StatisticsCalculator.median([5, 1, 3, 4, 2]) == pytest.approx(
            3.0
        )


# ──────────────────────────────────────────────
# StatisticsCalculator.mode
# ──────────────────────────────────────────────


class TestMode:
    """Tests for the mode calculation."""

    def test_mode_empty_list(self):
        """Mode of an empty list should be an empty list."""
        assert StatisticsCalculator.mode([]) == []

    def test_mode_single_mode(self):
        """A single most frequent value should be the mode."""
        assert StatisticsCalculator.mode([1, 2, 2, 3]) == [2]

    def test_mode_multiple_modes(self):
        """Multiple values with highest frequency are all returned."""
        result = StatisticsCalculator.mode([1, 1, 2, 2, 3])
        assert result == [1, 2]

    def test_mode_all_unique(self):
        """When all values are unique, all are modes (same frequency)."""
        result = StatisticsCalculator.mode([1, 2, 3])
        assert result == [1, 2, 3]

    def test_mode_all_same(self):
        """When all values are the same, that value is the mode."""
        assert StatisticsCalculator.mode([5, 5, 5]) == [5]


# ──────────────────────────────────────────────
# StatisticsCalculator.variance
# ──────────────────────────────────────────────


class TestVariance:
    """Tests for the population variance calculation."""

    def test_variance_empty_list(self):
        """Variance of an empty list should be zero."""
        assert StatisticsCalculator.variance([]) == 0.0

    def test_variance_single_element(self):
        """Variance of a single element should be zero."""
        assert StatisticsCalculator.variance([10]) == pytest.approx(0.0)

    def test_variance_identical_values(self):
        """Variance of identical values should be zero."""
        assert StatisticsCalculator.variance([3, 3, 3, 3]) == pytest.approx(
            0.0
        )

    def test_variance_known_values(self):
        """Variance of [2, 4, 4, 4, 5, 5, 7, 9] = 4.0."""
        assert StatisticsCalculator.variance(
            [2, 4, 4, 4, 5, 5, 7, 9]
        ) == pytest.approx(4.0)


# ──────────────────────────────────────────────
# StatisticsCalculator.std_dev
# ──────────────────────────────────────────────


class TestStdDev:
    """Tests for the population standard deviation calculation."""

    def test_std_dev_empty_list(self):
        """Standard deviation of an empty list should be zero."""
        assert StatisticsCalculator.std_dev([]) == 0.0

    def test_std_dev_single_element(self):
        """Standard deviation of a single element should be zero."""
        assert StatisticsCalculator.std_dev([10]) == pytest.approx(0.0)

    def test_std_dev_known_values(self):
        """Standard deviation of [2, 4, 4, 4, 5, 5, 7, 9] = 2.0."""
        assert StatisticsCalculator.std_dev(
            [2, 4, 4, 4, 5, 5, 7, 9]
        ) == pytest.approx(2.0, abs=1e-6)


# ──────────────────────────────────────────────
# process_file
# ──────────────────────────────────────────────


class TestProcessFile:
    """Tests for file reading and parsing."""

    def test_nonexistent_file(self):
        """A nonexistent file should return an empty list."""
        assert process_file(Path("nonexistent.txt")) == []

    def test_directory_instead_of_file(self, tmp_path):
        """A directory path should return an empty list."""
        assert process_file(tmp_path) == []

    def test_empty_file(self, tmp_path):
        """An empty file should return an empty list."""
        empty_file = tmp_path / "empty.txt"
        empty_file.write_text("")
        assert process_file(empty_file) == []

    def test_valid_integers(self, tmp_path):
        """Valid integer lines should be parsed correctly."""
        data_file = tmp_path / "ints.txt"
        data_file.write_text("1\n2\n3\n4\n5\n")
        assert process_file(data_file) == [1.0, 2.0, 3.0, 4.0, 5.0]

    def test_valid_decimals(self, tmp_path):
        """Valid decimal lines should be parsed correctly."""
        data_file = tmp_path / "decs.txt"
        data_file.write_text("1.5\n-2.3\n+0.7\n.25\n")
        assert process_file(data_file) == [1.5, -2.3, 0.7, 0.25]

    def test_invalid_lines_skipped(self, tmp_path):
        """Invalid lines should be skipped, valid ones kept."""
        data_file = tmp_path / "mixed.txt"
        data_file.write_text("10\nABA\n20\n5,3\n30\n")
        result = process_file(data_file)
        assert result == [10.0, 20.0, 30.0]

    def test_blank_lines_skipped(self, tmp_path):
        """Blank lines should be silently skipped."""
        data_file = tmp_path / "blanks.txt"
        data_file.write_text("1\n\n2\n\n3\n")
        assert process_file(data_file) == [1.0, 2.0, 3.0]

    def test_tc1_count(self):
        """TC1 should produce 400 valid numbers."""
        numbers = process_file(DATA_DIR / "TC1.txt")
        assert len(numbers) == 400

    def test_tc2_count(self):
        """TC2 should produce 1977 valid numbers (3 invalid lines)."""
        numbers = process_file(DATA_DIR / "TC2.txt")
        assert len(numbers) == 1977

    def test_tc5_count(self):
        """TC5 should produce 307 valid numbers."""
        numbers = process_file(DATA_DIR / "TC5.txt")
        assert len(numbers) == 307


# ──────────────────────────────────────────────
# format_results
# ──────────────────────────────────────────────


class TestFormatResults:
    """Tests for result string formatting."""

    def test_format_contains_header(self):
        """Output should contain the header."""
        stats = StatisticsResult(10, 5.0, 5.0, [5.0], 1.0, 1.0, 0.001)
        result = format_results(stats)
        assert "DESCRIPTIVE STATISTICS RESULTS" in result

    def test_format_single_mode(self):
        """A single mode should be displayed as a number."""
        stats = StatisticsResult(10, 5.0, 5.0, [230.0], 1.0, 1.0, 0.001)
        result = format_results(stats)
        assert "Mode:               230.000000" in result

    def test_format_multiple_modes_na(self):
        """Multiple modes should display as N/A."""
        stats = StatisticsResult(10, 5.0, 5.0, [1.0, 2.0], 1.0, 1.0, 0.001)
        result = format_results(stats)
        assert "Mode:               N/A" in result

    def test_format_empty_mode_na(self):
        """An empty mode list should display as N/A."""
        stats = StatisticsResult(10, 5.0, 5.0, [], 1.0, 1.0, 0.001)
        result = format_results(stats)
        assert "Mode:               N/A" in result

    def test_format_count(self):
        """Count should appear in the output."""
        stats = StatisticsResult(42, 0.0, 0.0, [], 0.0, 0.0, 0.0)
        result = format_results(stats)
        assert "Count:              42" in result

    def test_format_elapsed_time(self):
        """Elapsed time should appear formatted with 6 decimals."""
        stats = StatisticsResult(1, 0.0, 0.0, [], 0.0, 0.0, 1.234567)
        result = format_results(stats)
        assert "Elapsed Time:       1.234567 seconds" in result


# ──────────────────────────────────────────────
# Integration tests – compare against expected results
# ──────────────────────────────────────────────


class TestIntegrationTC1:
    """Integration tests for TC1.txt against p1_result.txt."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Load numbers from TC1."""
        self.numbers = process_file(DATA_DIR / "TC1.txt")

    def test_count(self):
        assert len(self.numbers) == 400

    def test_mean(self):
        assert StatisticsCalculator.mean(self.numbers) == pytest.approx(
            242.320000, abs=1e-4
        )

    def test_median(self):
        assert StatisticsCalculator.median(self.numbers) == pytest.approx(
            239.500000, abs=1e-4
        )

    def test_mode_is_na(self):
        """TC1 mode is N/A (multiple modes)."""
        modes = StatisticsCalculator.mode(self.numbers)
        assert len(modes) > 1

    def test_std_dev(self):
        assert StatisticsCalculator.std_dev(self.numbers) == pytest.approx(
            145.258107, abs=1e-4
        )

    def test_variance(self):
        assert StatisticsCalculator.variance(self.numbers) == pytest.approx(
            21099.917600, abs=1e-2
        )


class TestIntegrationTC2:
    """Integration tests for TC2.txt against p2_result.txt."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Load numbers from TC2."""
        self.numbers = process_file(DATA_DIR / "TC2.txt")

    def test_count(self):
        assert len(self.numbers) == 1977

    def test_mean(self):
        assert StatisticsCalculator.mean(self.numbers) == pytest.approx(
            250.784016, abs=1e-4
        )

    def test_median(self):
        assert StatisticsCalculator.median(self.numbers) == pytest.approx(
            247.000000, abs=1e-4
        )

    def test_mode_single(self):
        """TC2 mode should be 230."""
        modes = StatisticsCalculator.mode(self.numbers)
        assert len(modes) == 1
        assert modes[0] == pytest.approx(230.0)

    def test_std_dev(self):
        assert StatisticsCalculator.std_dev(self.numbers) == pytest.approx(
            144.171319, abs=1e-4
        )

    def test_variance(self):
        assert StatisticsCalculator.variance(self.numbers) == pytest.approx(
            20785.369132, abs=1e-2
        )


class TestIntegrationTC3:
    """Integration tests for TC3.txt against p3_result.txt."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Load numbers from TC3."""
        self.numbers = process_file(DATA_DIR / "TC3.txt")

    def test_count(self):
        assert len(self.numbers) == 12624

    def test_mean(self):
        assert StatisticsCalculator.mean(self.numbers) == pytest.approx(
            249.776220, abs=1e-4
        )

    def test_median(self):
        assert StatisticsCalculator.median(self.numbers) == pytest.approx(
            249.000000, abs=1e-4
        )

    def test_mode_single(self):
        """TC3 mode should be 94."""
        modes = StatisticsCalculator.mode(self.numbers)
        assert len(modes) == 1
        assert modes[0] == pytest.approx(94.0)

    def test_std_dev(self):
        assert StatisticsCalculator.std_dev(self.numbers) == pytest.approx(
            145.317850, abs=1e-4
        )

    def test_variance(self):
        assert StatisticsCalculator.variance(self.numbers) == pytest.approx(
            21117.277473, abs=1e-2
        )


class TestIntegrationTC4:
    """Integration tests for TC4.txt against p4_result.txt (decimal data)."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Load numbers from TC4."""
        self.numbers = process_file(DATA_DIR / "TC4.txt")

    def test_count(self):
        assert len(self.numbers) == 12624

    def test_mean(self):
        assert StatisticsCalculator.mean(self.numbers) == pytest.approx(
            149.002673, abs=1e-4
        )

    def test_median(self):
        assert StatisticsCalculator.median(self.numbers) == pytest.approx(
            147.750000, abs=1e-4
        )

    def test_mode_single(self):
        """TC4 mode should be 123.75."""
        modes = StatisticsCalculator.mode(self.numbers)
        assert len(modes) == 1
        assert modes[0] == pytest.approx(123.750000)

    def test_std_dev(self):
        assert StatisticsCalculator.std_dev(self.numbers) == pytest.approx(
            130.414420, abs=1e-4
        )

    def test_variance(self):
        assert StatisticsCalculator.variance(self.numbers) == pytest.approx(
            17007.920843, abs=1e-2
        )


class TestIntegrationTC5:
    """Integration tests for TC5.txt against p5_result.txt."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Load numbers from TC5."""
        self.numbers = process_file(DATA_DIR / "TC5.txt")

    def test_count(self):
        assert len(self.numbers) == 307

    def test_mean(self):
        assert StatisticsCalculator.mean(self.numbers) == pytest.approx(
            241.495114, abs=1e-4
        )

    def test_median(self):
        assert StatisticsCalculator.median(self.numbers) == pytest.approx(
            241.000000, abs=1e-4
        )

    def test_mode_is_na(self):
        """TC5 mode is N/A (multiple modes)."""
        modes = StatisticsCalculator.mode(self.numbers)
        assert len(modes) > 1

    def test_std_dev(self):
        assert StatisticsCalculator.std_dev(self.numbers) == pytest.approx(
            145.464848, abs=1e-4
        )

    def test_variance(self):
        assert StatisticsCalculator.variance(self.numbers) == pytest.approx(
            21160.021963, abs=1e-2
        )


class TestIntegrationTC6:
    """Integration tests for TC6.txt against p6_result.txt (large numbers)."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Load numbers from TC6."""
        self.numbers = process_file(DATA_DIR / "TC6.txt")

    def test_count(self):
        assert len(self.numbers) == 3000

    def test_mean(self):
        assert StatisticsCalculator.mean(self.numbers) == pytest.approx(
            187906599279774728192.0, rel=1e-6
        )

    def test_median(self):
        assert StatisticsCalculator.median(self.numbers) == pytest.approx(
            188008049965542998016.0, rel=1e-6
        )

    def test_mode_is_na(self):
        """TC6 mode is N/A (multiple modes)."""
        modes = StatisticsCalculator.mode(self.numbers)
        assert len(modes) > 1


class TestIntegrationTC7:
    """Integration tests for TC7.txt against p7_result.txt (large numbers)."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Load numbers from TC7."""
        self.numbers = process_file(DATA_DIR / "TC7.txt")

    def test_count(self):
        assert len(self.numbers) == 12767

    def test_mean(self):
        assert StatisticsCalculator.mean(self.numbers) == pytest.approx(
            247467395499714904064.0, rel=1e-6
        )

    def test_median(self):
        assert StatisticsCalculator.median(self.numbers) == pytest.approx(
            246640973074290016256.0, rel=1e-6
        )

    def test_mode_is_na(self):
        """TC7 mode is N/A (multiple modes)."""
        modes = StatisticsCalculator.mode(self.numbers)
        assert len(modes) > 1
