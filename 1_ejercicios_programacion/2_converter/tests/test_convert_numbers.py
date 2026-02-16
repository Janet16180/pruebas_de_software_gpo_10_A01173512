"""Unit tests for convertNumbers module."""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

import pytest  # noqa: E402
from convertNumbers import (  # noqa: E402
    NumberConverter,
    process_file,
    format_results,
)

DATA_DIR = BASE_DIR / "data"


# ──────────────────────────────────────────────
# NumberConverter.to_binary
# ──────────────────────────────────────────────


class TestToBinary:
    """Tests for the binary conversion implementation."""

    def test_zero(self):
        """Zero should return '0'."""
        assert NumberConverter.to_binary(0) == "0"

    def test_positive_small(self):
        """Small positive integers should convert correctly."""
        assert NumberConverter.to_binary(1) == "1"
        assert NumberConverter.to_binary(2) == "10"
        assert NumberConverter.to_binary(5) == "101"
        assert NumberConverter.to_binary(10) == "1010"

    def test_positive_powers_of_two(self):
        """Powers of two should produce a 1 followed by zeros."""
        assert NumberConverter.to_binary(8) == "1000"
        assert NumberConverter.to_binary(256) == "100000000"

    def test_positive_large(self):
        """Large positive integers should convert correctly."""
        assert NumberConverter.to_binary(255) == "11111111"
        assert NumberConverter.to_binary(6980368) == "11010101000001100010000"

    def test_negative_twos_complement(self):
        """Negative numbers should use 32-bit two's complement."""
        assert (
            NumberConverter.to_binary(-1) == "11111111111111111111111111111111"
        )
        assert (
            NumberConverter.to_binary(-39)
            == "11111111111111111111111111011001"
        )
        assert (
            NumberConverter.to_binary(-50)
            == "11111111111111111111111111001110"
        )

    def test_negative_small(self):
        """Small negatives should have leading ones in two's complement."""
        assert (
            NumberConverter.to_binary(-6) == "11111111111111111111111111111010"
        )
        assert (
            NumberConverter.to_binary(-4) == "11111111111111111111111111111100"
        )


# ──────────────────────────────────────────────
# NumberConverter.to_hexadecimal
# ──────────────────────────────────────────────


class TestToHexadecimal:
    """Tests for the hexadecimal conversion implementation."""

    def test_zero(self):
        """Zero should return '0'."""
        assert NumberConverter.to_hexadecimal(0) == "0"

    def test_positive_small(self):
        """Small positive integers should convert correctly."""
        assert NumberConverter.to_hexadecimal(10) == "A"
        assert NumberConverter.to_hexadecimal(15) == "F"
        assert NumberConverter.to_hexadecimal(16) == "10"
        assert NumberConverter.to_hexadecimal(255) == "FF"

    def test_positive_large(self):
        """Large positive integers should convert correctly."""
        assert NumberConverter.to_hexadecimal(6980368) == "6A8310"
        assert NumberConverter.to_hexadecimal(50986) == "C72A"

    def test_uppercase_letters(self):
        """Hexadecimal output should use uppercase A-F."""
        assert NumberConverter.to_hexadecimal(171) == "AB"
        assert NumberConverter.to_hexadecimal(3735928559) == "DEADBEEF"

    def test_negative_twos_complement(self):
        """Negative numbers should use 32-bit two's complement."""
        assert NumberConverter.to_hexadecimal(-1) == "FFFFFFFF"
        assert NumberConverter.to_hexadecimal(-39) == "FFFFFFD9"
        assert NumberConverter.to_hexadecimal(-50) == "FFFFFFCE"

    def test_negative_small(self):
        """Small negative values should produce two's complement hex."""
        assert NumberConverter.to_hexadecimal(-6) == "FFFFFFFA"
        assert NumberConverter.to_hexadecimal(-16) == "FFFFFFF0"


# ──────────────────────────────────────────────
# Consistency between binary and hexadecimal
# ──────────────────────────────────────────────


class TestConversionConsistency:
    """Tests that binary and hex conversions are consistent with each other."""

    def test_positive_roundtrip(self):
        """Binary and hex should represent the same value for positives."""
        for number in [0, 1, 42, 255, 1000, 6980368]:
            binary = NumberConverter.to_binary(number)
            hexadecimal = NumberConverter.to_hexadecimal(number)
            assert int(binary, 2) == number
            assert int(hexadecimal, 16) == number

    def test_negative_roundtrip(self):
        """Binary and hex two's complement should represent the same value."""
        for number in [-1, -39, -50, -6]:
            binary = NumberConverter.to_binary(number)
            hexadecimal = NumberConverter.to_hexadecimal(number)
            assert int(binary, 2) == int(hexadecimal, 16)


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
        """Valid integers should be parsed and converted correctly."""
        data_file = tmp_path / "ints.txt"
        data_file.write_text("10\n255\n0\n")
        result = process_file(data_file)
        assert len(result) == 3
        assert result[0] == (10, "1010", "A")
        assert result[1] == (255, "11111111", "FF")
        assert result[2] == (0, "0", "0")

    def test_negative_integers(self, tmp_path):
        """Negative integers should use two's complement."""
        data_file = tmp_path / "neg.txt"
        data_file.write_text("-39\n-6\n")
        result = process_file(data_file)
        assert len(result) == 2
        assert result[0] == (
            -39,
            "11111111111111111111111111011001",
            "FFFFFFD9",
        )
        assert result[1] == (
            -6,
            "11111111111111111111111111111010",
            "FFFFFFFA",
        )

    def test_invalid_lines_skipped(self, tmp_path):
        """Invalid lines (decimals, text) should be skipped."""
        data_file = tmp_path / "mixed.txt"
        data_file.write_text("10\nABC\n20\n3.14\n30\n")
        result = process_file(data_file)
        assert len(result) == 3
        assert result[0][0] == 10
        assert result[1][0] == 20
        assert result[2][0] == 30

    def test_blank_lines_skipped(self, tmp_path):
        """Blank lines should be silently skipped."""
        data_file = tmp_path / "blanks.txt"
        data_file.write_text("1\n\n2\n\n3\n")
        result = process_file(data_file)
        assert len(result) == 3

    def test_tc1_count(self):
        """TC1 should produce 200 conversions."""
        result = process_file(DATA_DIR / "TC1.txt")
        assert len(result) == 200

    def test_tc2_count(self):
        """TC2 should produce 200 conversions."""
        result = process_file(DATA_DIR / "TC2.txt")
        assert len(result) == 200

    def test_tc3_count(self):
        """TC3 should produce 200 conversions."""
        result = process_file(DATA_DIR / "TC3.txt")
        assert len(result) == 200

    def test_tc4_count(self):
        """TC4 should produce 38 conversions (3 invalid lines)."""
        result = process_file(DATA_DIR / "TC4.txt")
        assert len(result) == 38


# ──────────────────────────────────────────────
# format_results
# ──────────────────────────────────────────────


class TestFormatResults:
    """Tests for result string formatting."""

    def test_format_contains_header(self):
        """Output should contain the header."""
        result = format_results([(10, "1010", "A")], 0.001)
        assert "NUMBER CONVERSION RESULTS" in result

    def test_format_contains_columns(self):
        """Output should contain column headers."""
        result = format_results([(10, "1010", "A")], 0.001)
        assert "NUMBER" in result
        assert "BINARY" in result
        assert "HEXADECIMAL" in result

    def test_format_total_count(self):
        """Total count should reflect the number of conversions."""
        conversions = [(10, "1010", "A"), (255, "11111111", "FF")]
        result = format_results(conversions, 0.001)
        assert "Total numbers converted: 2" in result

    def test_format_elapsed_time(self):
        """Elapsed time should appear formatted with 6 decimals."""
        result = format_results([(1, "1", "1")], 1.234567)
        assert "Elapsed Time: 1.234567 seconds" in result

    def test_format_conversion_row(self):
        """Each conversion should appear as a row in the output."""
        result = format_results(
            [(-39, "11111111111111111111111111011001", "FFFFFFD9")], 0.0
        )
        assert "-39" in result
        assert "11111111111111111111111111011001" in result
        assert "FFFFFFD9" in result


# ──────────────────────────────────────────────
# Integration tests – compare against expected results
# ──────────────────────────────────────────────


class TestIntegrationTC1:
    """Integration tests for TC1.txt against t1_result.txt."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Load conversions from TC1."""
        self.conversions = process_file(DATA_DIR / "TC1.txt")

    def test_count(self):
        assert len(self.conversions) == 200

    def test_first_conversion(self):
        """First number 6980368 → binary and hex."""
        number, binary, hexadecimal = self.conversions[0]
        assert number == 6980368
        assert binary == "11010101000001100010000"
        assert hexadecimal == "6A8310"

    def test_sample_conversions(self):
        """Spot-check a few conversions from the middle."""
        # 50986 (index 24)
        assert self.conversions[24] == (50986, "1100011100101010", "C72A")
        # 2250854 (index 199, last)
        assert self.conversions[199] == (
            2250854,
            "1000100101100001100110",
            "225866",
        )


class TestIntegrationTC2:
    """Integration tests for TC2.txt against t2_result.txt."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Load conversions from TC2."""
        self.conversions = process_file(DATA_DIR / "TC2.txt")

    def test_count(self):
        assert len(self.conversions) == 200

    def test_first_conversion(self):
        """First number 7116776 → binary and hex."""
        number, binary, hexadecimal = self.conversions[0]
        assert number == 7116776
        assert binary == "11011001001011111101000"
        assert hexadecimal == "6C97E8"

    def test_last_conversion(self):
        """Last number 39 → binary and hex."""
        number, binary, hexadecimal = self.conversions[199]
        assert number == 39
        assert binary == "100111"
        assert hexadecimal == "27"


class TestIntegrationTC3:
    """Integration tests for TC3.txt (mixed positive/negative)."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Load conversions from TC3."""
        self.conversions = process_file(DATA_DIR / "TC3.txt")

    def test_count(self):
        assert len(self.conversions) == 200

    def test_negative_conversion(self):
        """First number -39 should use two's complement."""
        number, binary, hexadecimal = self.conversions[0]
        assert number == -39
        assert binary == "11111111111111111111111111011001"
        assert hexadecimal == "FFFFFFD9"

    def test_zero_conversion(self):
        """Zero should convert to '0' in both bases."""
        number, binary, hexadecimal = self.conversions[8]
        assert number == 0
        assert binary == "0"
        assert hexadecimal == "0"

    def test_positive_conversion(self):
        """Positive number 8 in the mixed dataset."""
        number, binary, hexadecimal = self.conversions[2]
        assert number == 8
        assert binary == "1000"
        assert hexadecimal == "8"

    def test_last_conversion(self):
        """Last number 4."""
        number, binary, hexadecimal = self.conversions[199]
        assert number == 4
        assert binary == "100"
        assert hexadecimal == "4"


class TestIntegrationTC4:
    """Integration tests for TC4.txt (with invalid entries)."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Load conversions from TC4."""
        self.conversions = process_file(DATA_DIR / "TC4.txt")

    def test_count(self):
        """TC4 has 41 lines but 3 are invalid (ABC, ERR, VAL), so 38 valid."""
        assert len(self.conversions) == 38

    def test_first_conversion(self):
        """First valid number -39."""
        number, binary, hexadecimal = self.conversions[0]
        assert number == -39
        assert binary == "11111111111111111111111111011001"
        assert hexadecimal == "FFFFFFD9"

    def test_invalid_skipped(self):
        """Line 8 (ABC) should be skipped; 7th valid entry should be '5'."""
        assert self.conversions[6][0] == 5

    def test_last_conversion(self):
        """Last valid number -6."""
        number, binary, hexadecimal = self.conversions[37]
        assert number == -6
        assert binary == "11111111111111111111111111111010"
        assert hexadecimal == "FFFFFFFA"
