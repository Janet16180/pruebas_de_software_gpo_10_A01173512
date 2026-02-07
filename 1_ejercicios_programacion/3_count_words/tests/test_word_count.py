"""Unit tests for wordCount module."""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

import pytest  # noqa: E402
from wordCount import (  # noqa: E402
    is_valid_word,
    normalize_word,
    sort_words,
    count_words,
    process_file,
    format_results,
)

DATA_DIR = BASE_DIR / "data"


# ──────────────────────────────────────────────
# is_valid_word
# ──────────────────────────────────────────────


class TestIsValidWord:
    """Tests for the word validation function."""

    def test_valid_alpha(self):
        """A word with only letters is valid."""
        assert is_valid_word("hello") is True

    def test_valid_numeric(self):
        """A word with digits is valid."""
        assert is_valid_word("123") is True

    def test_valid_alphanumeric(self):
        """A word with letters and digits is valid."""
        assert is_valid_word("abc123") is True

    def test_valid_with_punctuation(self):
        """A word with punctuation but also alphanumeric chars is valid."""
        assert is_valid_word("hello!") is True
        assert is_valid_word("it's") is True

    def test_invalid_only_punctuation(self):
        """A word with only punctuation is invalid."""
        assert is_valid_word("!!!") is False
        assert is_valid_word("---") is False

    def test_invalid_empty_string(self):
        """An empty string is invalid."""
        assert is_valid_word("") is False


# ──────────────────────────────────────────────
# normalize_word
# ──────────────────────────────────────────────


class TestNormalizeWord:
    """Tests for the word normalization function."""

    def test_lowercase_conversion(self):
        """Uppercase letters should be converted to lowercase."""
        assert normalize_word("HELLO") == "hello"
        assert normalize_word("Hello") == "hello"

    def test_already_lowercase(self):
        """Lowercase words should remain unchanged."""
        assert normalize_word("world") == "world"

    def test_punctuation_removed(self):
        """Punctuation should be stripped from the word."""
        assert normalize_word("hello!") == "hello"
        assert normalize_word("it's") == "its"
        assert normalize_word("co-op") == "coop"

    def test_digits_preserved(self):
        """Digits should be preserved."""
        assert normalize_word("abc123") == "abc123"

    def test_only_punctuation(self):
        """A string of only punctuation should return empty string."""
        assert normalize_word("!!!") == ""

    def test_empty_string(self):
        """An empty string should return empty string."""
        assert normalize_word("") == ""


# ──────────────────────────────────────────────
# sort_words
# ──────────────────────────────────────────────


class TestSortWords:
    """Tests for the bubble sort implementation."""

    def test_empty_list(self):
        """An empty list should return an empty list."""
        assert sort_words([]) == []

    def test_single_element(self):
        """A single element list is already sorted."""
        assert sort_words([("apple", 1)]) == [("apple", 1)]

    def test_alphabetical_order(self):
        """Words should be sorted alphabetically."""
        data = [("banana", 2), ("apple", 3), ("cherry", 1)]
        result = sort_words(data)
        assert result == [("apple", 3), ("banana", 2), ("cherry", 1)]

    def test_already_sorted(self):
        """An already sorted list should remain the same."""
        data = [("a", 1), ("b", 2), ("c", 3)]
        assert sort_words(data) == [("a", 1), ("b", 2), ("c", 3)]

    def test_does_not_modify_original(self):
        """sort_words should not modify the original list."""
        data = [("banana", 2), ("apple", 3)]
        sort_words(data)
        assert data == [("banana", 2), ("apple", 3)]


# ──────────────────────────────────────────────
# count_words
# ──────────────────────────────────────────────


class TestCountWords:
    """Tests for the word frequency counting."""

    def test_empty_list(self):
        """An empty list should return an empty dict."""
        assert count_words([]) == {}

    def test_single_word(self):
        """A single word should have count 1."""
        assert count_words(["hello"]) == {"hello": 1}

    def test_repeated_words(self):
        """Repeated words should be counted correctly."""
        result = count_words(["a", "b", "a", "c", "b", "a"])
        assert result == {"a": 3, "b": 2, "c": 1}

    def test_all_unique(self):
        """All unique words should each have count 1."""
        result = count_words(["one", "two", "three"])
        assert result == {"one": 1, "two": 1, "three": 1}


# ──────────────────────────────────────────────
# process_file
# ──────────────────────────────────────────────


class TestProcessFile:
    """Tests for file reading and word parsing."""

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

    def test_simple_words(self, tmp_path):
        """Simple words should be normalized and returned."""
        data_file = tmp_path / "words.txt"
        data_file.write_text("Hello World\n")
        result = process_file(data_file)
        assert result == ["hello", "world"]

    def test_punctuation_handled(self, tmp_path):
        """Words with punctuation should be normalized."""
        data_file = tmp_path / "punct.txt"
        data_file.write_text("hello! it's a test.\n")
        result = process_file(data_file)
        assert result == ["hello", "its", "a", "test"]

    def test_invalid_tokens_skipped(self, tmp_path):
        """Tokens with no alphanumeric characters should be skipped."""
        data_file = tmp_path / "invalid.txt"
        data_file.write_text("hello --- world !!!\n")
        result = process_file(data_file)
        assert result == ["hello", "world"]

    def test_multiple_lines(self, tmp_path):
        """Words across multiple lines should all be collected."""
        data_file = tmp_path / "multi.txt"
        data_file.write_text("one two\nthree four\n")
        result = process_file(data_file)
        assert result == ["one", "two", "three", "four"]


# ──────────────────────────────────────────────
# format_results
# ──────────────────────────────────────────────


class TestFormatResults:
    """Tests for result string formatting."""

    def test_format_contains_header(self):
        """Output should contain the header."""
        result = format_results([("hello", 1)], 1, 0.001)
        assert "WORD COUNT RESULTS" in result

    def test_format_contains_columns(self):
        """Output should contain column headers."""
        result = format_results([("hello", 1)], 1, 0.001)
        assert "WORD" in result
        assert "FREQUENCY" in result

    def test_format_total_words(self):
        """Total words processed should appear in the output."""
        result = format_results([("a", 3), ("b", 2)], 5, 0.001)
        assert "Total words processed: 5" in result

    def test_format_distinct_words(self):
        """Distinct words count should reflect the word list length."""
        result = format_results([("a", 3), ("b", 2)], 5, 0.001)
        assert "Distinct words found:  2" in result

    def test_format_elapsed_time(self):
        """Elapsed time should appear formatted with 6 decimals."""
        result = format_results([("x", 1)], 1, 1.234567)
        assert "Elapsed Time: 1.234567 seconds" in result

    def test_format_word_row(self):
        """Each word-frequency pair should appear in the output."""
        result = format_results([("conservative", 2)], 2, 0.0)
        assert "conservative" in result


# ──────────────────────────────────────────────
# Integration tests – compare against expected results
# ──────────────────────────────────────────────


class TestIntegrationTC1:
    """Integration tests for TC1.txt against t1_result.txt."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Load and process words from TC1."""
        self.words = process_file(DATA_DIR / "TC1.txt")
        self.frequency = count_words(self.words)
        word_list = [(w, c) for w, c in self.frequency.items()]
        self.sorted_words = sort_words(word_list)

    def test_total_words(self):
        assert len(self.words) == 100

    def test_distinct_words(self):
        assert len(self.sorted_words) == 99

    def test_conservative_appears_twice(self):
        """'conservative' is the only word with count 2."""
        assert self.frequency["conservative"] == 2

    def test_alphabetical_order(self):
        """Words should be sorted alphabetically."""
        word_names = [w for w, _ in self.sorted_words]
        assert word_names == sorted(word_names)

    def test_first_word(self):
        """First word alphabetically should be 'achievement'."""
        assert self.sorted_words[0][0] == "achievement"

    def test_last_word(self):
        """Last word alphabetically should be 'worse'."""
        assert self.sorted_words[-1][0] == "worse"


class TestIntegrationTC2:
    """Integration tests for TC2.txt against t2_result.txt."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Load and process words from TC2."""
        self.words = process_file(DATA_DIR / "TC2.txt")
        self.frequency = count_words(self.words)
        word_list = [(w, c) for w, c in self.frequency.items()]
        self.sorted_words = sort_words(word_list)

    def test_total_words(self):
        assert len(self.words) == 184

    def test_distinct_words(self):
        assert len(self.sorted_words) == 144

    def test_words_with_frequency_4(self):
        """Several words should appear exactly 4 times."""
        freq_4_words = {w for w, c in self.sorted_words if c == 4}
        expected = {
            "amongst",
            "brass",
            "chain",
            "doc",
            "filme",
            "holders",
            "inflation",
            "kingston",
            "lease",
            "monaco",
            "revenues",
            "targeted",
        }
        assert freq_4_words == expected

    def test_pre_frequency(self):
        """'pre' should appear 3 times."""
        assert self.frequency["pre"] == 3

    def test_wood_frequency(self):
        """'wood' should appear 3 times."""
        assert self.frequency["wood"] == 3


class TestIntegrationTC3:
    """Integration tests for TC3.txt against t3_result.txt."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Load and process words from TC3."""
        self.words = process_file(DATA_DIR / "TC3.txt")
        self.frequency = count_words(self.words)
        word_list = [(w, c) for w, c in self.frequency.items()]
        self.sorted_words = sort_words(word_list)

    def test_total_words(self):
        assert len(self.words) == 500

    def test_distinct_words(self):
        assert len(self.sorted_words) == 487

    def test_notice_frequency(self):
        """'notice' should appear 3 times (highest frequency)."""
        assert self.frequency["notice"] == 3

    def test_alphabetical_order(self):
        """Words should be sorted alphabetically."""
        word_names = [w for w, _ in self.sorted_words]
        assert word_names == sorted(word_names)


class TestIntegrationTC4:
    """Integration tests for TC4.txt against t4_result.txt."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Load and process words from TC4."""
        self.words = process_file(DATA_DIR / "TC4.txt")
        self.frequency = count_words(self.words)
        word_list = [(w, c) for w, c in self.frequency.items()]
        self.sorted_words = sort_words(word_list)

    def test_total_words(self):
        assert len(self.words) == 1000

    def test_distinct_words(self):
        assert len(self.sorted_words) == 949

    def test_started_frequency(self):
        """'started' should appear 3 times."""
        assert self.frequency["started"] == 3

    def test_alphabetical_order(self):
        """Words should be sorted alphabetically."""
        word_names = [w for w, _ in self.sorted_words]
        assert word_names == sorted(word_names)


class TestIntegrationTC5:
    """Integration tests for TC5.txt against t5_result.txt."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Load and process words from TC5."""
        self.words = process_file(DATA_DIR / "TC5.txt")
        self.frequency = count_words(self.words)
        word_list = [(w, c) for w, c in self.frequency.items()]
        self.sorted_words = sort_words(word_list)

    def test_total_words(self):
        assert len(self.words) == 5000

    def test_distinct_words(self):
        assert len(self.sorted_words) == 3750

    def test_alphabetical_order(self):
        """Words should be sorted alphabetically."""
        word_names = [w for w, _ in self.sorted_words]
        assert word_names == sorted(word_names)
